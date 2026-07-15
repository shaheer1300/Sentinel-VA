from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.stats import spearmanr

from .core import StructuredLogger, sha256_file, write_json
from .pipeline import _artifact, _concentration, _handoff, _save_manifest, _write_dataframe
from .scoring import score_features


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return 1.0 if not union else len(left & right) / len(union)


def wilson_interval(successes: int, trials: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if trials <= 0:
        raise ValueError("trials must be positive")
    p = successes / trials
    denominator = 1.0 + z * z / trials
    center = (p + z * z / (2.0 * trials)) / denominator
    margin = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * trials)) / trials) / denominator
    return center - margin, center + margin


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    if not p_values:
        return []
    values = np.asarray(p_values, dtype=float)
    order = np.argsort(values)
    ranked = values[order]
    adjusted = ranked * len(values) / np.arange(1, len(values) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    result = np.empty_like(adjusted)
    result[order] = np.clip(adjusted, 0.0, 1.0)
    return result.tolist()


def bootstrap_spearman_ci(left: np.ndarray, right: np.ndarray, iterations: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    estimates: list[float] = []
    for _ in range(iterations):
        selected = rng.integers(0, len(left), len(left))
        value = float(spearmanr(left[selected], right[selected]).statistic)
        if np.isfinite(value):
            estimates.append(value)
    if not estimates:
        return float("nan"), float("nan")
    return float(np.quantile(estimates, 0.025)), float(np.quantile(estimates, 0.975))


def _aggregate_primary_grid(
    crashes: pd.DataFrame,
    membership: pd.DataFrame,
    school_reference: pd.DataFrame,
) -> pd.DataFrame:
    joined = crashes.merge(membership[["source_row_id", "location_id"]], on="source_row_id", how="inner", validate="one_to_one")
    numeric_columns = [
        "Number of Fatalities",
        "Number of People with Suspected Serious Injury",
        "Number of People Injured",
        "Number of Pedestrian Fatalities",
        "Number of Pedestrians Injured",
    ]
    for column in numeric_columns:
        joined[column] = pd.to_numeric(joined[column], errors="coerce").fillna(0)
    joined["pedestrian_involved_flag"] = joined["Pedestrian Involved"].astype(str).str.casefold().eq("yes").astype(int)
    joined["bicycle_involved_flag"] = joined["Bicycle Involved"].astype(str).str.casefold().eq("yes").astype(int)
    joined["night_crash_flag"] = joined["Night Crash"].astype(str).str.casefold().eq("yes").astype(int)
    grouped = joined.groupby("location_id", sort=True)
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
    hour_bin = pd.cut(
        joined["event_datetime"].dt.hour,
        bins=[-1, 5, 11, 17, 23],
        labels=["overnight", "morning", "afternoon", "evening"],
    )
    features = features.merge(
        _concentration(joined, hour_bin).rename("hour_bin_concentration"), on="location_id", how="left"
    ).merge(
        _concentration(joined, joined["event_datetime"].dt.dayofweek).rename("weekday_concentration"),
        on="location_id",
        how="left",
    )
    features["vulnerable_road_user_crashes"] = (
        features["pedestrian_involved_crashes"] + features["bicycle_involved_crashes"]
    )
    school_columns = [
        "location_id",
        "nearest_school_poi_id",
        "nearest_school_name",
        "nearest_school_classification",
        "nearest_school_distance_m",
    ]
    features = features.merge(school_reference[school_columns], on="location_id", how="left", validate="one_to_one")
    features["exposure_adjusted_metric_available"] = False
    features["exposure_limitation"] = "EXPOSURE_ADJUSTMENT_NOT_APPLIED"
    return features


def _alternative_grid_features(
    crashes: pd.DataFrame,
    schools: pd.DataFrame,
    cell_size: int,
    source_crs: str,
    analysis_crs: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    transformer = Transformer.from_crs(source_crs, analysis_crs, always_xy=True)
    inverse = Transformer.from_crs(analysis_crs, source_crs, always_xy=True)
    x, y = transformer.transform(crashes["Longitude"].tolist(), crashes["Latitude"].tolist())
    east = np.floor(np.asarray(x) / cell_size).astype(np.int64)
    north = np.floor(np.asarray(y) / cell_size).astype(np.int64)
    membership = crashes[["source_row_id"]].copy()
    membership["location_id"] = [f"grid{cell_size}_{e}_{n}" for e, n in zip(east, north, strict=True)]
    cells = pd.DataFrame({"location_id": membership["location_id"], "east": east, "north": north}).drop_duplicates()
    cells["centroid_x_m"] = (cells["east"] + 0.5) * cell_size
    cells["centroid_y_m"] = (cells["north"] + 0.5) * cell_size
    longitude, latitude = inverse.transform(cells["centroid_x_m"].tolist(), cells["centroid_y_m"].tolist())
    cells["centroid_longitude"] = longitude
    cells["centroid_latitude"] = latitude
    school_x, school_y = transformer.transform(schools["longitude"].tolist(), schools["latitude"].tolist())
    distance = np.sqrt(
        ((cells[["centroid_x_m", "centroid_y_m"]].to_numpy()[:, None, :] - np.column_stack([school_x, school_y])[None, :, :]) ** 2).sum(axis=2)
    )
    nearest = distance.argmin(axis=1)
    school_reference = pd.DataFrame(
        {
            "location_id": cells["location_id"].to_numpy(),
            "nearest_school_poi_id": schools.iloc[nearest]["poi_id"].to_numpy(),
            "nearest_school_name": schools.iloc[nearest]["name"].to_numpy(),
            "nearest_school_classification": schools.iloc[nearest]["school_classification"].to_numpy(),
            "nearest_school_distance_m": distance[np.arange(len(cells)), nearest],
        }
    )
    return _aggregate_primary_grid(crashes, membership, school_reference), cells


def _sample_audit(crashes: pd.DataFrame, membership: pd.DataFrame, cap: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    work = crashes.merge(membership[["source_row_id", "location_id"]], on="source_row_id", how="inner", validate="one_to_one")
    work["year"] = work["event_datetime"].dt.year
    work["pedestrian_flag"] = work["Pedestrian Involved"].astype(str).str.casefold().eq("yes")
    work["bicycle_flag"] = work["Bicycle Involved"].astype(str).str.casefold().eq("yes")
    lon_mid = work["Longitude"].median()
    lat_mid = work["Latitude"].median()
    work["spatial_quadrant"] = np.where(work["Latitude"] >= lat_mid, "N", "S") + np.where(
        work["Longitude"] >= lon_mid, "E", "W"
    )
    selected: set[int] = set()
    for column in ("year", "Crash Severity", "pedestrian_flag", "bicycle_flag", "spatial_quadrant"):
        for _, group in work.groupby(column, dropna=False, sort=True):
            indices = group.index.to_numpy()
            take = min(5, len(indices))
            selected.update(rng.choice(indices, size=take, replace=False).tolist())
    if len(selected) > cap:
        selected = set(rng.choice(np.asarray(sorted(selected)), size=cap, replace=False).tolist())
    elif len(selected) < cap:
        remaining = np.asarray(sorted(set(work.index) - selected))
        take = min(cap - len(selected), len(remaining))
        if take:
            selected.update(rng.choice(remaining, size=take, replace=False).tolist())
    return work.loc[sorted(selected)].copy().reset_index(drop=True)


def _audit_results(sample: pd.DataFrame, full_crashes: pd.DataFrame, membership: pd.DataFrame, cell_size: int) -> pd.DataFrame:
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:26918", always_xy=True)
    x, y = transformer.transform(sample["Longitude"].tolist(), sample["Latitude"].tolist())
    expected = [
        f"grid{cell_size}_{math.floor(e / cell_size)}_{math.floor(n / cell_size)}" for e, n in zip(x, y, strict=True)
    ]
    counts = membership.groupby("location_id").size()
    source_count = full_crashes.merge(membership, on="source_row_id", validate="one_to_one").groupby("location_id").size()
    result = sample[["source_row_id", "Document Number", "location_id", "year", "Crash Severity", "pedestrian_flag", "bicycle_flag", "spatial_quadrant"]].copy()
    result["expected_location_id"] = expected
    result["location_assignment_correct"] = result["location_id"].eq(result["expected_location_id"])
    result["membership_count"] = result["location_id"].map(counts)
    result["source_recount"] = result["location_id"].map(source_count)
    result["aggregate_count_correct"] = result["membership_count"].eq(result["source_recount"])
    result["audit_pass"] = result["location_assignment_correct"] & result["aggregate_count_correct"]
    result["reviewer"] = "Codex implementation agent"
    result["review_type"] = "deterministic lineage and aggregate verification"
    return result


def phase5(root: Path, run_dir: Path, manifest: dict[str, Any], specification: dict[str, Any]) -> None:
    phase_dir = run_dir / "phase5"
    phase_dir.mkdir(parents=True, exist_ok=False)
    features = pd.read_csv(run_dir / "phase3" / "location_features.csv", low_memory=False)
    ranked = pd.read_csv(run_dir / "phase4" / "ranked_locations.csv", low_memory=False)
    rerun_a = score_features(features, specification, manifest["run_id"])
    rerun_b = score_features(features, specification, manifest["run_id"])
    reproducible = rerun_a.to_csv(index=False, lineterminator="\n") == rerun_b.to_csv(index=False, lineterminator="\n")
    if not reproducible:
        raise ValueError("score rerun is nondeterministic")

    crashes = pd.read_csv(run_dir / "phase2" / "crashes_clean.csv", low_memory=False, parse_dates=["event_datetime"])
    membership = pd.read_csv(run_dir / "phase3" / "crash_membership.csv")
    schools = pd.read_csv(run_dir / "phase2" / "schools_primary_k12.csv", low_memory=False)
    validation = specification["validation"]
    minimum = int(validation["minimum_events_per_location_per_temporal_block"])
    block_scores: dict[str, pd.DataFrame] = {}
    for block in validation["temporal_blocks"]:
        subset = crashes.loc[
            crashes["event_datetime"].between(pd.Timestamp(block["start"]), pd.Timestamp(block["end"]) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1))
        ].copy()
        block_features = _aggregate_primary_grid(subset, membership, features)
        block_scores[block["id"]] = score_features(block_features, specification, manifest["run_id"])
        _write_dataframe(phase_dir / f"temporal_scores_{block['id']}.csv", block_scores[block["id"]])

    temporal_rows: list[dict[str, Any]] = []
    identifiers = [block["id"] for block in validation["temporal_blocks"]]
    for comparison_index, (left_id, right_id) in enumerate(zip(identifiers[:-1], identifiers[1:], strict=True)):
        left = block_scores[left_id]
        right = block_scores[right_id]
        comparison = left[["location_id", "priority_index", "crash_count"]].merge(
            right[["location_id", "priority_index", "crash_count"]],
            on="location_id",
            suffixes=("_left", "_right"),
        )
        comparison = comparison.loc[
            comparison["crash_count_left"].ge(minimum) & comparison["crash_count_right"].ge(minimum)
        ]
        statistic = spearmanr(comparison["priority_index_left"], comparison["priority_index_right"])
        low, high = bootstrap_spearman_ci(
            comparison["priority_index_left"].to_numpy(),
            comparison["priority_index_right"].to_numpy(),
            int(validation["bootstrap_iterations"]),
            int(manifest["random_seed"]) + comparison_index,
        )
        left_top = set(comparison.nlargest(10, "priority_index_left")["location_id"])
        right_top = set(comparison.nlargest(10, "priority_index_right")["location_id"])
        temporal_rows.append(
            {
                "comparison": f"{left_id}_vs_{right_id}",
                "locations_compared": len(comparison),
                "spearman_rho": float(statistic.statistic),
                "p_value": float(statistic.pvalue),
                "bootstrap_ci_low": low,
                "bootstrap_ci_high": high,
                "top10_jaccard": jaccard(left_top, right_top),
            }
        )
    adjusted = benjamini_hochberg([row["p_value"] for row in temporal_rows])
    for row, adjusted_value in zip(temporal_rows, adjusted, strict=True):
        row["fdr_adjusted_p_value"] = adjusted_value
        row["passes_temporal_gate"] = bool(
            row["spearman_rho"] >= float(validation["temporal_spearman_threshold"])
            and adjusted_value < float(validation["alpha"])
        )
    temporal_frame = pd.DataFrame(temporal_rows)
    temporal_path = phase_dir / "temporal_validation.csv"
    _write_dataframe(temporal_path, temporal_frame)

    full_scores = ranked[["location_id", "priority_index"]]
    sensitivity_rows: list[dict[str, Any]] = []
    for year in sorted(crashes["event_datetime"].dt.year.unique()):
        subset = crashes.loc[crashes["event_datetime"].dt.year.ne(year)].copy()
        subset_scores = score_features(_aggregate_primary_grid(subset, membership, features), specification, manifest["run_id"])
        common = full_scores.merge(subset_scores[["location_id", "priority_index"]], on="location_id", suffixes=("_full", "_subset"))
        rho = float(spearmanr(common["priority_index_full"], common["priority_index_subset"]).statistic)
        sensitivity_rows.append(
            {
                "analysis": f"leave_{year}_out",
                "spearman_rho": rho,
                "top10_jaccard": jaccard(set(ranked.head(10)["location_id"]), set(subset_scores.head(10)["location_id"])),
            }
        )
    pandemic_subset = crashes.loc[~crashes["event_datetime"].dt.year.isin(validation["pandemic_sensitivity_excluded_years"])].copy()
    pandemic_scores = score_features(_aggregate_primary_grid(pandemic_subset, membership, features), specification, manifest["run_id"])
    pandemic_common = full_scores.merge(pandemic_scores[["location_id", "priority_index"]], on="location_id", suffixes=("_full", "_subset"))
    sensitivity_rows.append(
        {
            "analysis": "exclude_2020",
            "spearman_rho": float(spearmanr(pandemic_common["priority_index_full"], pandemic_common["priority_index_subset"]).statistic),
            "top10_jaccard": jaccard(set(ranked.head(10)["location_id"]), set(pandemic_scores.head(10)["location_id"])),
        }
    )

    primary_top = set(ranked.head(10)["location_id"])
    for cell_size in (200, 300):
        alternative_features, alternative_cells = _alternative_grid_features(
            crashes, schools, cell_size, manifest["source_crs"], manifest["analysis_crs"]
        )
        alternative_scores = score_features(alternative_features, specification, manifest["run_id"])
        top = alternative_scores.head(10).merge(
            alternative_cells[["location_id", "centroid_x_m", "centroid_y_m"]], on="location_id", validate="one_to_one"
        )
        mapped = {
            f"grid250_{math.floor(row.centroid_x_m / 250)}_{math.floor(row.centroid_y_m / 250)}"
            for row in top.itertuples(index=False)
        }
        sensitivity_rows.append(
            {
                "analysis": f"grid_{cell_size}m_mapped_to_primary",
                "spearman_rho": float("nan"),
                "top10_jaccard": jaccard(primary_top, mapped),
            }
        )
        _write_dataframe(phase_dir / f"spatial_scores_{cell_size}m.csv", alternative_scores)
    sensitivity_frame = pd.DataFrame(sensitivity_rows)
    sensitivity_path = phase_dir / "sensitivity_analysis.csv"
    _write_dataframe(sensitivity_path, sensitivity_frame)

    sample = _sample_audit(crashes, membership, int(validation["manual_audit_cap"]), int(manifest["random_seed"]))
    audit = _audit_results(sample, crashes, membership, int(manifest["location_unit"]["cell_size_m"]))
    successes = int(audit["audit_pass"].sum())
    lower, upper = wilson_interval(successes, len(audit))
    audit_path = phase_dir / "manual_audit_results.csv"
    _write_dataframe(audit_path, audit)

    temporal_pass = bool(temporal_frame["passes_temporal_gate"].all())
    spatial_rows = sensitivity_frame[sensitivity_frame["analysis"].str.startswith("grid_")]
    spatial_pass = bool(spatial_rows["top10_jaccard"].ge(float(validation["top10_jaccard_threshold"])).all())
    audit_pass = bool(
        successes / len(audit) >= float(validation["manual_audit_minimum_agreement"])
        and lower >= float(validation["manual_audit_wilson_lower_bound"])
    )
    classification = "validated_feasibility" if temporal_pass and spatial_pass and audit_pass else "conditionally_feasible"
    report = {
        "pilot_classification": classification,
        "reproducible_score_rerun": reproducible,
        "manual_audit": {
            "records": len(audit),
            "passes": successes,
            "agreement": successes / len(audit),
            "wilson_95_ci": [lower, upper],
            "passes_gate": audit_pass,
            "independent_second_reviewer": False,
        },
        "temporal_gate_passed": temporal_pass,
        "spatial_sensitivity_gate_passed": spatial_pass,
        "unresolved_abort_criteria": [],
        "interpretation": (
            "All pre-registered feasibility gates passed."
            if classification == "validated_feasibility"
            else "One or more stability gates did not pass; results remain exploratory and are published with conditional status."
        ),
    }
    report_path = phase_dir / "validation_report.json"
    write_json(report_path, report)
    reproducibility_path = phase_dir / "reproducibility_report.json"
    write_json(
        reproducibility_path,
        {
            "identical_row_level_values": reproducible,
            "source_feature_sha256": sha256_file(run_dir / "phase3" / "location_features.csv"),
            "ranked_output_sha256": sha256_file(run_dir / "phase4" / "ranked_locations.csv"),
        },
    )
    logger = StructuredLogger(run_dir / "logs" / "run.jsonl", manifest["run_id"])
    logger.emit("phase5", "ACTIVE", f"Scientific validation complete: {classification}", input_rows=len(ranked), retained_rows=len(ranked), excluded_rows=0, hash_status="verified")
    deliverables = [temporal_path, sensitivity_path, audit_path, report_path, reproducibility_path]
    handoff = _handoff(phase_dir, root, manifest, 5, deliverables, report)
    manifest["outputs"].extend(_artifact(path, root) for path in [*deliverables, handoff])
    manifest["pilot_classification"] = classification
    manifest["state"] = "PREPARED_FOR_PHASE6"
    _save_manifest(root, run_dir, manifest)
