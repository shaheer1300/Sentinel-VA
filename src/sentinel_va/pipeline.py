from __future__ import annotations

import json
import math
import os
import shutil
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely import covers, points
from shapely.geometry import shape

from .core import (
    StructuredLogger,
    atomic_write_text,
    config_hash,
    ensure_production_paths,
    new_manifest,
    sha256_file,
    snapshot_file,
    utc_now,
    validate_manifest,
    write_json,
)


CRASH_REQUIRED_COLUMNS = {
    "Document Number",
    "Datetime",
    "Route or Street Name",
    "Crash Severity",
    "Number of Fatalities",
    "Number of People with Suspected Serious Injury",
    "Number of People Injured",
    "Number of Pedestrian Fatalities",
    "Number of Pedestrians Injured",
    "Bicycle Involved",
    "Pedestrian Involved",
    "Intersection Type",
    "Latitude",
    "Longitude",
    "Night Crash",
}

SCHOOL_REQUIRED_COLUMNS = {
    "poi_id",
    "name",
    "business_status",
    "category_level_4",
    "latitude",
    "longitude",
    "locality",
    "last_verified_date",
}

K12_CATEGORIES = {
    "elementary school": "elementary",
    "middle school": "middle",
    "high school": "high",
    "k-12 school": "k12",
}


def _load_school_sources(root: Path, config: dict[str, Any]) -> pd.DataFrame:
    school_ids = set(config.get("school_input_ids", {"schools_primary_early", "schools_secondary"}))
    items = [item for item in config["inputs"] if item["id"] in school_ids]
    if not items:
        raise ValueError("no configured school inputs")
    if school_ids == {"nces_public_schools_2023_24", "nces_private_schools_2023_24"}:
        frames: list[pd.DataFrame] = []
        for item in items:
            source = pd.read_csv(root / item["path"], low_memory=False)
            required = {"NAME", "CITY", "STATE", "LAT", "LON", "SCHOOLYEAR"}
            _require_columns(source, required, item["id"])
            is_public = item["id"] == "nces_public_schools_2023_24"
            identifier = "NCESSCH" if is_public else "PPIN"
            _require_columns(source, {identifier}, item["id"])
            source = source.loc[
                source["STATE"].astype(str).str.casefold().eq("va")
                & source["CITY"].astype(str).str.casefold().eq("norfolk")
            ].copy()
            names = source["NAME"].astype(str)
            normalized = names.str.casefold()
            early_only = normalized.str.contains(r"preschool|early childhood|kindergarten", regex=True)
            classification = np.select(
                [
                    early_only,
                    normalized.str.contains("elementary"),
                    normalized.str.contains("middle"),
                    normalized.str.contains("high"),
                    normalized.str.contains(r"k-8|prek-8|pre-k-8", regex=True),
                ],
                ["early_childhood_only", "elementary", "middle", "high", "k12"],
                default="k12_unspecified",
            )
            frames.append(
                pd.DataFrame(
                    {
                        "source_file": Path(item["path"]).name,
                        "poi_id": source[identifier].astype(str),
                        "name": names,
                        "business_status": "reported_2023_24",
                        "category_level_4": classification,
                        "latitude": source["LAT"],
                        "longitude": source["LON"],
                        "locality": source["CITY"],
                        "last_verified_date": "2023-24_source_vintage",
                        "school_source_type": "public" if is_public else "private",
                        "source_school_year": source["SCHOOLYEAR"].astype(str),
                    }
                )
            )
        return pd.concat(frames, ignore_index=True)

    frames = []
    for item in items:
        frame = pd.read_csv(root / item["path"])
        _require_columns(frame, SCHOOL_REQUIRED_COLUMNS, "school")
        frame.insert(0, "source_file", Path(item["path"]).name)
        frame["school_source_type"] = "legacy_poi"
        frame["source_school_year"] = "unknown"
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def read_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    ensure_production_paths(config)
    return config


def _write_dataframe(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".partial")
    frame.to_csv(temp, index=False, lineterminator="\n")
    os.replace(temp, path)


def _artifact(path: Path, root: Path, rows: int | None = None) -> dict[str, Any]:
    result = {
        "path": path.relative_to(root).as_posix(),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }
    if rows is not None:
        result["rows"] = int(rows)
    return result


def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{label} schema missing columns: {', '.join(missing)}")


def _handoff(
    phase_dir: Path,
    root: Path,
    manifest: dict[str, Any],
    phase: int,
    deliverables: list[Path],
    quality_metrics: dict[str, Any],
    decision: str = "GO",
) -> Path:
    record = {
        "phase": phase,
        "run_id": manifest["run_id"],
        "owner": "Sentinel-VA implementation lead",
        "completed_at_utc": utc_now(),
        "input_checkpoint": manifest["inputs"],
        "deliverables": [_artifact(path, root) for path in deliverables],
        "test_evidence": {
            "command": ".venv/Scripts/python.exe -m pytest",
            "report": f"outputs/test-evidence/{manifest['run_id']}-phase{phase}.xml",
            "requirement": "all tests passing",
        },
        "quality_metrics": quality_metrics,
        "deviations_or_incidents": [],
        "open_abort_criteria": [],
        "handoff_decision": decision,
    }
    path = phase_dir / "handoff.json"
    write_json(path, record)
    return path


def _save_manifest(root: Path, run_dir: Path, manifest: dict[str, Any]) -> None:
    validate_manifest(manifest)
    write_json(run_dir / "manifest.json", manifest)


def phase0(root: Path, config: dict[str, Any], run_id: str) -> tuple[dict[str, Any], Path]:
    run_dir = root / "outputs" / "runs" / run_id
    if run_dir.exists():
        raise FileExistsError(f"run already exists: {run_id}")
    for relative in ("logs", "phase0", "phase1", "phase2", "phase3", "checkpoints"):
        (run_dir / relative).mkdir(parents=True, exist_ok=False)
    logger = StructuredLogger(run_dir / "logs" / "run.jsonl", run_id)
    manifest = new_manifest(config, run_id)
    manifest["config_path"] = "configs/norfolk_pilot.json"
    manifest["config_hash"] = config_hash(config)
    manifest["outputs"].append({"path": f"outputs/runs/{run_id}", "type": "isolated_run_directory"})
    _save_manifest(root, run_dir, manifest)
    logger.emit("phase0", "PREPARED", "Run directory, manifest, and structured log initialized", hash_status="verified")
    environment_path = run_dir / "phase0" / "environment.json"
    write_json(environment_path, manifest["environment"])
    log_checkpoint_path = run_dir / "phase0" / "run_log_checkpoint.jsonl"
    atomic_write_text(log_checkpoint_path, (run_dir / "logs" / "run.jsonl").read_text(encoding="utf-8"))
    handoff = _handoff(
        run_dir / "phase0",
        root,
        manifest,
        0,
        [environment_path, log_checkpoint_path],
        {"manifest_valid": True, "isolated_run_directory": True, "production_inputs_are_not_fixtures": True},
    )
    manifest["outputs"].append(_artifact(handoff, root))
    _save_manifest(root, run_dir, manifest)
    return manifest, run_dir


def phase1(root: Path, config: dict[str, Any], manifest: dict[str, Any], run_dir: Path) -> None:
    logger = StructuredLogger(run_dir / "logs" / "run.jsonl", manifest["run_id"])
    phase_dir = run_dir / "phase1"
    raw_root = root / "data" / "raw" / "Norfolk"
    archive_root = root / "data" / "archive" / "Norfolk"
    source_rows: list[dict[str, Any]] = []

    for item in config["inputs"]:
        source = root / item["path"]
        if not source.exists():
            raise FileNotFoundError(source)
        raw_path = raw_root / source.name
        archive_path = archive_root / source.name
        source_hash = snapshot_file(source, raw_path)
        archive_hash = snapshot_file(source, archive_path)
        if source_hash != archive_hash:
            raise ValueError(f"archive mismatch for {source}")
        record = {
            **item,
            "sha256": source_hash,
            "bytes": source.stat().st_size,
            "raw_snapshot": raw_path.relative_to(root).as_posix(),
            "archive_snapshot": archive_path.relative_to(root).as_posix(),
            "hash_status": "verified",
        }
        source_rows.append(record)

    source_register = pd.DataFrame(source_rows)
    source_register_path = phase_dir / "source_register.csv"
    _write_dataframe(source_register_path, source_register)
    manifest["inputs"] = source_rows

    crash_path = root / next(item["path"] for item in config["inputs"] if item["id"] == "norfolk_crashes")
    crashes = pd.read_csv(crash_path, low_memory=False)
    _require_columns(crashes, CRASH_REQUIRED_COLUMNS, "crash")
    parsed_dates = pd.to_datetime(crashes["Datetime"], format="mixed", errors="coerce")
    unique_documents = int(crashes["Document Number"].nunique(dropna=True))
    year_counts = parsed_dates.dt.year.value_counts(dropna=False).sort_index().rename_axis("year").reset_index(name="count")
    severity_counts = crashes["Crash Severity"].fillna("<missing>").value_counts().rename_axis("crash_severity").reset_index(name="count")
    hour_counts = parsed_dates.dt.hour.value_counts(dropna=False).sort_index().rename_axis("hour").reset_index(name="count")
    intersection_counts = crashes["Intersection Type"].fillna("<missing>").value_counts().rename_axis("intersection_type").reset_index(name="count")
    missingness = crashes[list(sorted(CRASH_REQUIRED_COLUMNS))].isna().sum().rename_axis("column").reset_index(name="missing_count")

    schools = _load_school_sources(root, config)
    _require_columns(schools, SCHOOL_REQUIRED_COLUMNS, "school")
    school_status_counts = schools["business_status"].fillna("<missing>").value_counts().to_dict()

    adt_path = root / next(item["path"] for item in config["inputs"] if item["id"] == "norfolk_adt_transfer_limited")
    with adt_path.open("r", encoding="utf-8") as handle:
        adt = json.load(handle)
    transfer_limited = bool(adt.get("properties", {}).get("exceededTransferLimit", False))
    if transfer_limited and config["exposure_enabled"]:
        raise ValueError("transfer-limited ADT cannot be enabled")
    adt_features = len(adt.get("features", []))
    explicit_norfolk = sum(
        1
        for feature in adt.get("features", [])
        if "norfolk" in str(feature.get("properties", {}).get("FROM_JURISDICTION", "")).lower()
        or "norfolk" in str(feature.get("properties", {}).get("TO_JURISDICTION", "")).lower()
        or "norfolk" in str(feature.get("properties", {}).get("ROUTE_COMMON_NAME", "")).lower()
    )

    baseline = {
        "crash_rows": int(len(crashes)),
        "unique_crash_documents": unique_documents,
        "crash_datetime_min": None if parsed_dates.isna().all() else parsed_dates.min().isoformat(),
        "crash_datetime_max": None if parsed_dates.isna().all() else parsed_dates.max().isoformat(),
        "crash_datetime_parse_failures": int(parsed_dates.isna().sum()),
        "pedestrian_involved_rows": int(crashes["Pedestrian Involved"].astype(str).str.casefold().eq("yes").sum()),
        "bicycle_involved_rows": int(crashes["Bicycle Involved"].astype(str).str.casefold().eq("yes").sum()),
        "school_rows": int(len(schools)),
        "school_status_counts": {str(k): int(v) for k, v in school_status_counts.items()},
        "adt_features": adt_features,
        "adt_explicit_norfolk_matches": explicit_norfolk,
        "adt_exceeded_transfer_limit": transfer_limited,
        "exposure_enabled": bool(config["exposure_enabled"]),
    }
    baseline_path = phase_dir / "baseline_summary.json"
    write_json(baseline_path, baseline)
    table_paths = []
    for name, frame in (
        ("crash_counts_by_year.csv", year_counts),
        ("crash_counts_by_severity.csv", severity_counts),
        ("crash_counts_by_hour.csv", hour_counts),
        ("crash_counts_by_intersection_type.csv", intersection_counts),
        ("required_field_missingness.csv", missingness),
    ):
        path = phase_dir / name
        _write_dataframe(path, frame)
        table_paths.append(path)

    if config.get("production") and unique_documents != len(crashes):
        raise ValueError("crash document numbers are not unique")
    if not transfer_limited:
        raise ValueError("current ADT file was expected to be transfer-limited; inspect source change")
    if config["exposure_enabled"]:
        raise ValueError("exposure must remain disabled for current ADT")

    logger.emit(
        "phase1",
        "PREPARED",
        "Source snapshots and baseline verified",
        input_rows=len(crashes),
        retained_rows=len(crashes),
        excluded_rows=0,
        hash_status="verified",
    )
    handoff = _handoff(
        phase_dir,
        root,
        manifest,
        1,
        [source_register_path, baseline_path, *table_paths],
        {
            "crash_rows": len(crashes),
            "unique_documents": unique_documents,
            "school_rows": len(schools),
            "adt_transfer_limited": transfer_limited,
            "exposure_enabled": config["exposure_enabled"],
            "all_source_hashes_verified": True,
        },
    )
    manifest["outputs"].extend(_artifact(path, root) for path in [source_register_path, baseline_path, *table_paths, handoff])
    _save_manifest(root, run_dir, manifest)


def _validate_envelope(longitude: pd.Series, latitude: pd.Series, envelope: dict[str, Any]) -> pd.Series:
    return (
        longitude.between(envelope["min_longitude"], envelope["max_longitude"], inclusive="both")
        & latitude.between(envelope["min_latitude"], envelope["max_latitude"], inclusive="both")
    )


def _normalized_name(value: Any) -> str:
    return " ".join(str(value).casefold().split())


def phase2(root: Path, config: dict[str, Any], manifest: dict[str, Any], run_dir: Path) -> None:
    logger = StructuredLogger(run_dir / "logs" / "run.jsonl", manifest["run_id"])
    phase_dir = run_dir / "phase2"
    crash_path = root / next(item["path"] for item in config["inputs"] if item["id"] == "norfolk_crashes")
    crashes = pd.read_csv(crash_path, low_memory=False)
    _require_columns(crashes, CRASH_REQUIRED_COLUMNS, "crash")
    crashes.insert(0, "source_row_id", np.arange(2, len(crashes) + 2, dtype=np.int64))
    crashes["event_datetime"] = pd.to_datetime(crashes["Datetime"], format="mixed", errors="coerce")
    crashes["Latitude"] = pd.to_numeric(crashes["Latitude"], errors="coerce")
    crashes["Longitude"] = pd.to_numeric(crashes["Longitude"], errors="coerce")

    boundary_item = next(item for item in config["inputs"] if item["id"] == config["approved_boundary"]["input_id"])
    boundary_payload = json.loads((root / boundary_item["path"]).read_text(encoding="utf-8"))
    boundary_features = boundary_payload.get("features", [])
    if len(boundary_features) != 1:
        raise ValueError("approved Norfolk boundary must contain exactly one feature")
    boundary_properties = boundary_features[0].get("properties", {})
    if str(boundary_properties.get("GEOID")) != config["approved_boundary"]["expected_geoid"]:
        raise ValueError("approved boundary GEOID does not match Norfolk city")
    norfolk_boundary = shape(boundary_features[0]["geometry"])
    if norfolk_boundary.is_empty or not norfolk_boundary.is_valid:
        raise ValueError("approved Norfolk boundary geometry is empty or invalid")

    start = pd.Timestamp(config["study_start"])
    end = pd.Timestamp(config["study_end"])
    valid_datetime = crashes["event_datetime"].between(start, end, inclusive="both")
    finite_coords = np.isfinite(crashes["Latitude"]) & np.isfinite(crashes["Longitude"])
    in_envelope = _validate_envelope(crashes["Longitude"], crashes["Latitude"], config["validation_envelope"])
    in_approved_boundary = np.asarray(
        covers(norfolk_boundary, points(crashes["Longitude"].to_numpy(), crashes["Latitude"].to_numpy())),
        dtype=bool,
    )
    duplicate_document = crashes["Document Number"].duplicated(keep="first") | crashes["Document Number"].isna()

    reasons = np.select(
        [duplicate_document, ~valid_datetime, ~finite_coords, ~in_envelope, ~in_approved_boundary],
        [
            "duplicate_or_null_document_number",
            "invalid_or_out_of_window_datetime",
            "invalid_coordinate",
            "outside_validation_envelope",
            "outside_approved_norfolk_boundary",
        ],
        default="",
    )
    crashes["exclusion_reason"] = reasons
    included = crashes["exclusion_reason"].eq("")
    retained = crashes.loc[included].copy()
    retained["run_id"] = manifest["run_id"]
    retained["transformation_version"] = "phase2-v1"
    exclusions = crashes.loc[~included, ["source_row_id", "Document Number", "exclusion_reason"]].copy()
    exclusions["run_id"] = manifest["run_id"]

    crash_clean_path = phase_dir / "crashes_clean.csv"
    exclusions_path = phase_dir / "crash_exclusions.csv"
    _write_dataframe(crash_clean_path, retained)
    _write_dataframe(exclusions_path, exclusions)

    schools = _load_school_sources(root, config)
    schools["normalized_name"] = schools["name"].map(_normalized_name)
    schools["latitude"] = pd.to_numeric(schools["latitude"], errors="coerce")
    schools["longitude"] = pd.to_numeric(schools["longitude"], errors="coerce")
    schools["category_normalized"] = schools["category_level_4"].astype(str).str.casefold().str.strip()
    if set(config.get("school_input_ids", [])) == {"nces_public_schools_2023_24", "nces_private_schools_2023_24"}:
        schools["school_classification"] = schools["category_normalized"]
        active_status = schools["business_status"].astype(str).eq("reported_2023_24")
        qualifying_category = ~schools["school_classification"].eq("early_childhood_only")
    else:
        schools["school_classification"] = schools["category_normalized"].map(K12_CATEGORIES).fillna(
            schools["category_normalized"].map({"preschool": "preschool", "kindergarten": "kindergarten"}).fillna("other")
        )
        active_status = schools["business_status"].astype(str).str.casefold().eq("open")
        qualifying_category = schools["school_classification"].isin(K12_CATEGORIES.values())
    schools["coordinate_valid"] = np.isfinite(schools["latitude"]) & np.isfinite(schools["longitude"])
    schools["within_validation_envelope"] = _validate_envelope(
        schools["longitude"], schools["latitude"], config["validation_envelope"]
    )
    schools["within_approved_norfolk_boundary"] = np.asarray(
        covers(norfolk_boundary, points(schools["longitude"].to_numpy(), schools["latitude"].to_numpy())),
        dtype=bool,
    )
    schools["locality_valid"] = schools["locality"].astype(str).str.casefold().eq("norfolk")
    schools["status_normalized"] = schools["business_status"].astype(str).str.casefold().str.strip()
    schools["primary_k12_included"] = (
        active_status
        & qualifying_category
        & schools["coordinate_valid"]
        & schools["within_validation_envelope"]
        & schools["within_approved_norfolk_boundary"]
        & schools["locality_valid"]
    )
    schools["classification_rationale"] = np.where(
        schools["primary_k12_included"],
        "Open Norfolk K-12 category with valid coordinate; included as facility proximity only.",
        "Excluded from primary proximity layer due to status, non-K-12 category, locality, or coordinate validation; retained for audit.",
    )
    schools["run_id"] = manifest["run_id"]
    schools["transformation_version"] = "phase2-v1"

    duplicate_mask = schools["normalized_name"].duplicated(keep=False)
    duplicate_ledger = schools.loc[
        duplicate_mask,
        ["poi_id", "name", "normalized_name", "business_status", "school_classification", "latitude", "longitude", "primary_k12_included"],
    ].copy()
    duplicate_ledger["adjudication"] = "retain_distinct_coordinates; closed/non-K-12 records remain excluded by primary-layer rules"
    duplicate_ledger["evidence_status"] = "requires source/licensing confirmation before public release"

    primary = schools.loc[schools["primary_k12_included"]].copy()
    audit = schools.loc[~schools["primary_k12_included"]].copy()
    school_inventory_path = phase_dir / "school_inventory.csv"
    primary_path = phase_dir / "schools_primary_k12.csv"
    audit_path = phase_dir / "schools_audit.csv"
    duplicate_path = phase_dir / "duplicate_name_ledger.csv"
    _write_dataframe(school_inventory_path, schools)
    _write_dataframe(primary_path, primary)
    _write_dataframe(audit_path, audit)
    _write_dataframe(duplicate_path, duplicate_ledger)

    reconciliation = {
        "crash_input_rows": int(len(crashes)),
        "crash_retained_rows": int(len(retained)),
        "crash_excluded_rows": int(len(exclusions)),
        "crash_reconciliation_difference": int(len(crashes) - len(retained) - len(exclusions)),
        "school_input_rows": int(len(schools)),
        "school_primary_k12_rows": int(len(primary)),
        "school_audit_rows": int(len(audit)),
        "school_reconciliation_difference": int(len(schools) - len(primary) - len(audit)),
        "duplicate_name_rows": int(len(duplicate_ledger)),
        "validation_envelope": config["validation_envelope"],
        "approved_boundary": {
            "source_id": boundary_item["id"],
            "source_path": boundary_item["path"],
            "geoid": str(boundary_properties.get("GEOID")),
            "name": boundary_properties.get("NAME"),
            "predicate": config["approved_boundary"]["inclusion_predicate"],
        },
        "source_crs": config["source_crs"],
        "analysis_crs": config["analysis_crs"],
    }
    quality_path = phase_dir / "quality_report.json"
    write_json(quality_path, reconciliation)
    if reconciliation["crash_reconciliation_difference"] != 0 or reconciliation["school_reconciliation_difference"] != 0:
        raise ValueError("phase2 row reconciliation failed")
    if not primary["primary_k12_included"].all():
        raise ValueError("primary K-12 layer contains invalid row")

    logger.emit(
        "phase2",
        "PREPARED",
        "Clean crash and validated school layers created",
        input_rows=len(crashes),
        retained_rows=len(retained),
        excluded_rows=len(exclusions),
        hash_status="verified",
    )
    deliverables = [crash_clean_path, exclusions_path, school_inventory_path, primary_path, audit_path, duplicate_path, quality_path]
    handoff = _handoff(
        phase_dir,
        root,
        manifest,
        2,
        deliverables,
        reconciliation,
    )
    manifest["outputs"].extend(_artifact(path, root) for path in [*deliverables, handoff])
    _save_manifest(root, run_dir, manifest)


def _concentration(frame: pd.DataFrame, category: pd.Series) -> pd.Series:
    counts = frame.assign(_category=category).groupby(
        ["location_id", "_category"], dropna=False, observed=True
    ).size()
    totals = frame.groupby("location_id").size()
    return counts.groupby(level=0).max().div(totals).rename("concentration")


def phase3(root: Path, config: dict[str, Any], manifest: dict[str, Any], run_dir: Path) -> None:
    logger = StructuredLogger(run_dir / "logs" / "run.jsonl", manifest["run_id"])
    phase_dir = run_dir / "phase3"
    crashes = pd.read_csv(run_dir / "phase2" / "crashes_clean.csv", low_memory=False, parse_dates=["event_datetime"])
    schools = pd.read_csv(run_dir / "phase2" / "schools_primary_k12.csv", low_memory=False)
    transformer = Transformer.from_crs(config["source_crs"], config["analysis_crs"], always_xy=True)
    inverse = Transformer.from_crs(config["analysis_crs"], config["source_crs"], always_xy=True)
    crash_x, crash_y = transformer.transform(crashes["Longitude"].tolist(), crashes["Latitude"].tolist())
    if not np.isfinite(crash_x).all() or not np.isfinite(crash_y).all():
        raise ValueError("projected crash coordinates are invalid")
    cell_size = int(config["location_unit"]["cell_size_m"])
    east_index = np.floor(np.asarray(crash_x) / cell_size).astype(np.int64)
    north_index = np.floor(np.asarray(crash_y) / cell_size).astype(np.int64)
    crashes["projected_x_m"] = crash_x
    crashes["projected_y_m"] = crash_y
    crashes["grid_east_index"] = east_index
    crashes["grid_north_index"] = north_index
    crashes["location_id"] = [f"grid{cell_size}_{e}_{n}" for e, n in zip(east_index, north_index, strict=True)]
    crashes["assignment_status"] = "assigned"

    location_indices = crashes[["location_id", "grid_east_index", "grid_north_index"]].drop_duplicates().sort_values("location_id")
    location_indices["centroid_x_m"] = (location_indices["grid_east_index"] + 0.5) * cell_size
    location_indices["centroid_y_m"] = (location_indices["grid_north_index"] + 0.5) * cell_size
    centroid_lon, centroid_lat = inverse.transform(
        location_indices["centroid_x_m"].tolist(), location_indices["centroid_y_m"].tolist()
    )
    location_indices["centroid_longitude"] = centroid_lon
    location_indices["centroid_latitude"] = centroid_lat
    location_indices["location_label"] = [
        f"{cell_size} m grid cell near {lat:.5f}, {lon:.5f}" for lat, lon in zip(centroid_lat, centroid_lon, strict=True)
    ]
    location_indices["geometry_wkt"] = [f"POINT ({lon:.8f} {lat:.8f})" for lat, lon in zip(centroid_lat, centroid_lon, strict=True)]
    location_indices["run_id"] = manifest["run_id"]
    location_indices["location_method_version"] = "fixed-grid-v1"

    membership = crashes[["source_row_id", "Document Number", "location_id", "assignment_status"]].copy()
    membership["run_id"] = manifest["run_id"]

    numeric_columns = [
        "Number of Fatalities",
        "Number of People with Suspected Serious Injury",
        "Number of People Injured",
        "Number of Pedestrian Fatalities",
        "Number of Pedestrians Injured",
    ]
    for column in numeric_columns:
        crashes[column] = pd.to_numeric(crashes[column], errors="coerce").fillna(0)
    crashes["pedestrian_involved_flag"] = crashes["Pedestrian Involved"].astype(str).str.casefold().eq("yes").astype(int)
    crashes["bicycle_involved_flag"] = crashes["Bicycle Involved"].astype(str).str.casefold().eq("yes").astype(int)
    crashes["night_crash_flag"] = crashes["Night Crash"].astype(str).str.casefold().eq("yes").astype(int)

    grouped = crashes.groupby("location_id", sort=True)
    features = grouped.agg(
        crash_count=("Document Number", "size"),
        fatalities=("Number of Fatalities", "sum"),
        suspected_serious_injuries=("Number of People with Suspected Serious Injury", "sum"),
        people_injured=("Number of People Injured", "sum"),
        pedestrian_involved_crashes=("pedestrian_involved_flag", "sum"),
        bicycle_involved_crashes=("bicycle_involved_flag", "sum"),
        pedestrian_fatalities=("Number of Pedestrian Fatalities", "sum"),
        pedestrians_injured=("Number of Pedestrians Injured", "sum"),
        night_crashes=("night_crash_flag", "sum"),
        first_event_datetime=("event_datetime", "min"),
        last_event_datetime=("event_datetime", "max"),
    ).reset_index()
    features["vulnerable_road_user_crashes"] = (
        features["pedestrian_involved_crashes"] + features["bicycle_involved_crashes"]
    )
    hour_bin = pd.cut(
        crashes["event_datetime"].dt.hour,
        bins=[-1, 5, 11, 17, 23],
        labels=["overnight", "morning", "afternoon", "evening"],
    )
    hour_concentration = _concentration(crashes, hour_bin).rename("hour_bin_concentration")
    weekday_concentration = _concentration(crashes, crashes["event_datetime"].dt.dayofweek).rename("weekday_concentration")
    features = features.merge(hour_concentration, on="location_id", how="left").merge(weekday_concentration, on="location_id", how="left")

    school_x, school_y = transformer.transform(schools["longitude"].tolist(), schools["latitude"].tolist())
    if len(schools) == 0:
        raise ValueError("validated primary K-12 layer is empty")
    location_xy = location_indices[["centroid_x_m", "centroid_y_m"]].to_numpy()
    school_xy = np.column_stack([school_x, school_y])
    distances = np.sqrt(((location_xy[:, None, :] - school_xy[None, :, :]) ** 2).sum(axis=2))
    nearest_index = distances.argmin(axis=1)
    location_school = pd.DataFrame(
        {
            "location_id": location_indices["location_id"].to_numpy(),
            "nearest_school_poi_id": schools.iloc[nearest_index]["poi_id"].to_numpy(),
            "nearest_school_name": schools.iloc[nearest_index]["name"].to_numpy(),
            "nearest_school_classification": schools.iloc[nearest_index]["school_classification"].to_numpy(),
            "nearest_school_distance_m": distances[np.arange(len(location_indices)), nearest_index],
        }
    )
    features = features.merge(location_school, on="location_id", how="left")
    features["exposure_adjusted_metric_available"] = False
    features["exposure_limitation"] = "EXPOSURE_ADJUSTMENT_NOT_APPLIED"
    features["run_id"] = manifest["run_id"]
    features["feature_version"] = "phase3-v1"

    assignment_rate = float(membership["assignment_status"].eq("assigned").mean()) if len(membership) else 0.0
    if assignment_rate < float(config["location_unit"]["assignment_threshold"]):
        raise ValueError(f"location assignment rate {assignment_rate:.6f} is below threshold")
    if config["exposure_enabled"]:
        raise ValueError("Phase 3 implementation prohibits exposure metrics for transfer-limited ADT")

    candidate_path = phase_dir / "candidate_locations.csv"
    membership_path = phase_dir / "crash_membership.csv"
    feature_path = phase_dir / "location_features.csv"
    _write_dataframe(candidate_path, location_indices)
    _write_dataframe(membership_path, membership)
    _write_dataframe(feature_path, features)

    decision = f"""# Phase 3 Location-Unit Decision\n\n+**Primary unit:** {cell_size} m fixed grid cell  \n+**Source CRS:** `{config['source_crs']}`  \n+**Analysis CRS:** `{config['analysis_crs']}`  \n+**Method version:** `fixed-grid-v1`  \n+**Assignment rate:** {assignment_rate:.6%}\n+\n+## Decision\n+\n+The pilot uses deterministic fixed cells because crash coordinates are available but authoritative intersection topology has not been established. Each valid crash is projected into the meter-based analysis CRS and assigned by `floor(coordinate / {cell_size})`. Stable cell identifiers encode the projected east/north indices.\n+\n+## Rejected primary alternatives\n+\n+- Named intersections: roadway strings do not establish authoritative topology or consistent intersection identity.\n+- Derived intersections: would require an independently sourced and validated road network that is not present.\n+- Spatial clusters: introduce density parameters and potential instability when a complete fixed assignment is available.\n+- Corridors: require authoritative segment geometry and directionality not established in the current inputs.\n+\n+## Boundary and interpretation\n+\n+The configured coordinate envelope is a conservative data-quality check, not a legal Norfolk boundary. Grid cells are analytic aggregation proxies and are not legal school zones, engineered intersections, camera sites, or deployment recommendations. Sensitivity variants at 200 m and 300 m are pre-declared and may not silently replace this primary definition.\n+"""
    decision = decision.replace("\n+", "\n")
    decision_path = phase_dir / "location_decision.md"
    atomic_write_text(decision_path, decision)
    sensitivity_path = phase_dir / "sensitivity_config.json"
    write_json(sensitivity_path, config["sensitivity"])
    dictionary = pd.DataFrame(
        [
            ("location_id", "Stable fixed-grid identifier", "string", "Derived from projected cell indices"),
            ("crash_count", "Historical crash records assigned to cell", "integer", "Count of unique source rows"),
            ("fatalities", "Recorded fatalities", "integer", "Sum of Number of Fatalities"),
            ("suspected_serious_injuries", "Recorded suspected serious injuries", "integer", "Sum of source field"),
            ("people_injured", "Recorded people injured", "integer", "Sum of source field"),
            ("pedestrian_involved_crashes", "Crashes marked pedestrian involved", "integer", "Count where Pedestrian Involved = Yes"),
            ("bicycle_involved_crashes", "Crashes marked bicycle involved", "integer", "Count where Bicycle Involved = Yes"),
            ("vulnerable_road_user_crashes", "Pedestrian plus bicycle involved observations", "integer", "Component sum; overlap may exist"),
            ("hour_bin_concentration", "Largest share in one of four hour bins", "0..1", "Maximum bin count / cell crash count"),
            ("weekday_concentration", "Largest share on one weekday", "0..1", "Maximum weekday count / cell crash count"),
            ("nearest_school_distance_m", "Distance from cell centroid to nearest validated active K-12 POI", "meters", "Euclidean distance in EPSG:26918"),
            ("exposure_adjusted_metric_available", "Whether complete exposure adjustment exists", "boolean", "False for current transfer-limited ADT"),
        ],
        columns=["field", "definition", "unit_or_type", "formula_or_lineage"],
    )
    dictionary_path = phase_dir / "data_dictionary.csv"
    _write_dataframe(dictionary_path, dictionary)
    quality = {
        "eligible_crash_rows": int(len(crashes)),
        "assigned_crash_rows": int(membership["assignment_status"].eq("assigned").sum()),
        "unassigned_crash_rows": int(membership["assignment_status"].ne("assigned").sum()),
        "assignment_rate": assignment_rate,
        "assignment_threshold": float(config["location_unit"]["assignment_threshold"]),
        "candidate_locations": int(len(location_indices)),
        "feature_rows": int(len(features)),
        "validated_primary_k12_schools": int(len(schools)),
        "location_unit": config["location_unit"],
        "source_crs": config["source_crs"],
        "analysis_crs": config["analysis_crs"],
        "exposure_enabled": False,
    }
    quality_path = phase_dir / "quality_report.json"
    write_json(quality_path, quality)

    logger.emit(
        "phase3",
        "PREPARED",
        "Fixed-grid location assignment and feature generation complete",
        input_rows=len(crashes),
        retained_rows=len(membership),
        excluded_rows=0,
        assignment_rate=assignment_rate,
        hash_status="verified",
    )
    deliverables = [candidate_path, membership_path, feature_path, decision_path, sensitivity_path, dictionary_path, quality_path]
    handoff = _handoff(phase_dir, root, manifest, 3, deliverables, quality)
    manifest["outputs"].extend(_artifact(path, root) for path in [*deliverables, handoff])
    manifest["state"] = "PREPARED_FOR_PHASE4"
    _save_manifest(root, run_dir, manifest)


def load_existing_run(root: Path, run_id: str, config: dict[str, Any]) -> tuple[dict[str, Any], Path]:
    run_dir = root / "outputs" / "runs" / run_id
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"run manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    if manifest["config_hash"] != config_hash(config):
        raise ValueError("configuration changed; create a new run_id")
    return manifest, run_dir


def execute(
    root: Path,
    config_path: Path,
    run_id: str,
    from_phase: int,
    through_phase: int,
    execution_config_path: Path | None = None,
) -> Path:
    config = read_config(config_path)
    if from_phase == 0:
        manifest, run_dir = phase0(root, config, run_id)
        start = 1
    else:
        manifest, run_dir = load_existing_run(root, run_id, config)
        start = from_phase
    for phase in range(start, through_phase + 1):
        if phase == 1:
            phase1(root, config, manifest, run_dir)
        elif phase == 2:
            phase2(root, config, manifest, run_dir)
        elif phase == 3:
            phase3(root, config, manifest, run_dir)
        elif phase in {4, 5, 6, 7}:
            if execution_config_path is None:
                raise ValueError("Phase 4 and later require an execution specification")
            from .scoring import load_execution_config, phase4
            from .validation import phase5
            from .release import phase6, phase7

            specification = load_execution_config(execution_config_path)
            existing_hash = manifest.get("phase4_7_specification_hash")
            if existing_hash is not None and existing_hash != config_hash(specification):
                raise ValueError("Phase 4–7 specification changed; start a new run")
            if phase == 4:
                phase4(root, run_dir, manifest, specification)
            elif phase == 5:
                phase5(root, run_dir, manifest, specification)
            elif phase == 6:
                phase6(root, run_dir, manifest, specification)
            else:
                phase7(root, run_dir, manifest, specification)
        else:
            raise ValueError(f"unsupported phase: {phase}")
    return run_dir
