from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from pyproj import Transformer

from sentinel_va.pipeline import (
    CRASH_REQUIRED_COLUMNS,
    SCHOOL_REQUIRED_COLUMNS,
    _require_columns,
    execute,
)
from sentinel_va.core import sha256_file


def crash_row(document: str | None, when: str, lat: float | None, lon: float | None, pedestrian: str = "No") -> dict:
    row = {column: 0 for column in CRASH_REQUIRED_COLUMNS}
    row.update(
        {
            "Document Number": document,
            "Datetime": when,
            "Route or Street Name": "TEST ROAD",
            "Crash Severity": "Property Damage Only",
            "Number of Fatalities": 0,
            "Number of People with Suspected Serious Injury": 0,
            "Number of People Injured": 0,
            "Number of Pedestrian Fatalities": 0,
            "Number of Pedestrians Injured": 0,
            "Bicycle Involved": "No",
            "Pedestrian Involved": pedestrian,
            "Intersection Type": "Not at Intersection",
            "Latitude": lat,
            "Longitude": lon,
            "Night Crash": "No",
        }
    )
    return row


def school_row(poi: str, name: str, status: str, category: str, lat: float, lon: float) -> dict:
    row = {column: "" for column in SCHOOL_REQUIRED_COLUMNS}
    row.update(
        {
            "poi_id": poi,
            "name": name,
            "business_status": status,
            "category_level_4": category,
            "latitude": lat,
            "longitude": lon,
            "locality": "Norfolk",
            "last_verified_date": "2026-06-01",
        }
    )
    return row


@pytest.fixture()
def fixture_project(tmp_path: Path) -> tuple[Path, Path]:
    data = tmp_path / "data" / "Norfolk"
    data.mkdir(parents=True)
    crashes = pd.DataFrame(
        [
            crash_row("1", "January 1, 2020 08:00 AM", 36.88, -76.25, "Yes"),
            crash_row("2", "January 2, 2020 09:00 PM", 36.8805, -76.2505),
            crash_row("2", "January 3, 2020 10:00 AM", 36.881, -76.251),
            crash_row("4", "not-a-date", 36.882, -76.252),
            crash_row("5", "January 5, 2020 10:00 AM", None, -76.252),
            crash_row("6", "January 6, 2020 10:00 AM", 40.0, -80.0),
        ]
    )
    crashes.to_csv(data / "Traffic_Crashes.csv", index=False)
    first_schools = pd.DataFrame(
        [
            school_row("e", "Alpha School", "open", "Elementary school", 36.88, -76.25),
            school_row("p", "Preschool", "open", "Preschool", 36.89, -76.26),
            school_row("k", "Kindergarten", "open", "Kindergarten", 36.89, -76.27),
            school_row("c", "Closed School", "closed", "Elementary school", 36.90, -76.28),
            school_row("d1", "Duplicate Campus", "open", "Elementary school", 36.91, -76.29),
            school_row("d2", " duplicate  campus ", "open", "Elementary school", 36.92, -76.30),
        ]
    )
    second_schools = pd.DataFrame(
        [
            school_row("m", "Middle", "open", "Middle school", 36.88, -76.24),
            school_row("h", "High", "open", "High school", 36.87, -76.24),
            school_row("a", "All Grades", "open", "K-12 school", 36.86, -76.24),
        ]
    )
    first_schools.to_csv(data / "School_information.csv", index=False)
    second_schools.to_csv(data / "MiddleandHighschool_information.csv", index=False)
    adt = {"type": "FeatureCollection", "properties": {"exceededTransferLimit": True}, "features": []}
    (data / "Traffic Volums ADT.json").write_text(json.dumps(adt), encoding="utf-8")
    boundary = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"GEOID": "51710", "NAME": "Norfolk city"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-76.35, 36.80], [-76.15, 36.80], [-76.15, 36.99], [-76.35, 36.99], [-76.35, 36.80]]],
                },
            }
        ],
    }
    (data / "Norfolk_Census_Boundary_2025.geojson").write_text(json.dumps(boundary), encoding="utf-8")
    config = {
        "project": "Sentinel-VA",
        "study": "fixture",
        "production": False,
        "study_start": "2016-01-01T00:00:00",
        "study_end": "2025-12-31T23:59:59",
        "source_crs": "EPSG:4326",
        "analysis_crs": "EPSG:26918",
        "approved_boundary": {
            "input_id": "norfolk_boundary_2025",
            "expected_geoid": "51710",
            "geometry_crs": "EPSG:4326",
            "inclusion_predicate": "covers",
        },
        "validation_envelope": {
            "name": "fixture",
            "provenance": "test",
            "min_longitude": -76.35,
            "max_longitude": -76.15,
            "min_latitude": 36.80,
            "max_latitude": 36.99,
        },
        "location_unit": {
            "type": "fixed_grid",
            "cell_size_m": 250,
            "assignment_threshold": 0.995,
            "rationale": "fixture",
            "limitations": "fixture",
        },
        "sensitivity": {
            "primary_cell_size_m": 250,
            "alternative_cell_sizes_m": [200, 300],
            "may_replace_primary_automatically": False,
        },
        "random_seed": 1,
        "exposure_enabled": False,
        "school_input_ids": ["schools_primary_early", "schools_secondary"],
        "inputs": [
            {"id": "norfolk_crashes", "path": "data/Norfolk/Traffic_Crashes.csv", "format": "csv"},
            {"id": "schools_primary_early", "path": "data/Norfolk/School_information.csv", "format": "csv"},
            {"id": "schools_secondary", "path": "data/Norfolk/MiddleandHighschool_information.csv", "format": "csv"},
            {"id": "norfolk_boundary_2025", "path": "data/Norfolk/Norfolk_Census_Boundary_2025.geojson", "format": "geojson"},
            {"id": "norfolk_adt_transfer_limited", "path": "data/Norfolk/Traffic Volums ADT.json", "format": "geojson"},
        ],
    }
    for item in config["inputs"]:
        item.update(
            {
                "source_owner": "fixture",
                "acquisition_date": "2026-07-12",
                "acquisition_method": "test",
                "provenance_status": "test-only",
                "license_status": "test-only",
                "known_limitations": "test-only",
            }
        )
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return tmp_path, config_path


def test_schema_contract_rejects_missing_required_column() -> None:
    with pytest.raises(ValueError, match="Datetime"):
        _require_columns(pd.DataFrame(columns=sorted(CRASH_REQUIRED_COLUMNS - {"Datetime"})), CRASH_REQUIRED_COLUMNS, "crash")


def test_crs_round_trip_is_stable() -> None:
    forward = Transformer.from_crs("EPSG:4326", "EPSG:26918", always_xy=True)
    inverse = Transformer.from_crs("EPSG:26918", "EPSG:4326", always_xy=True)
    x, y = forward.transform(-76.25, 36.88)
    longitude, latitude = inverse.transform(x, y)
    assert longitude == pytest.approx(-76.25, abs=1e-8)
    assert latitude == pytest.approx(36.88, abs=1e-8)


def test_end_to_end_phase0_to_phase3_fixture(fixture_project: tuple[Path, Path]) -> None:
    root, config_path = fixture_project
    source_hashes_before = {path.name: path.read_bytes() for path in (root / "data" / "Norfolk").iterdir()}
    run_dir = execute(root, config_path, "fixture-run", 0, 3)

    exclusions = pd.read_csv(run_dir / "phase2" / "crash_exclusions.csv")
    assert set(exclusions["exclusion_reason"]) == {
        "duplicate_or_null_document_number",
        "invalid_or_out_of_window_datetime",
        "invalid_coordinate",
        "outside_validation_envelope",
    }
    quality2 = json.loads((run_dir / "phase2" / "quality_report.json").read_text(encoding="utf-8"))
    assert quality2["crash_input_rows"] == quality2["crash_retained_rows"] + quality2["crash_excluded_rows"]
    assert quality2["school_input_rows"] == quality2["school_primary_k12_rows"] + quality2["school_audit_rows"]

    primary = pd.read_csv(run_dir / "phase2" / "schools_primary_k12.csv")
    audit = pd.read_csv(run_dir / "phase2" / "schools_audit.csv")
    assert {"elementary", "middle", "high", "k12"} <= set(primary["school_classification"])
    assert {"preschool", "kindergarten"} <= set(audit["school_classification"])
    assert "closed" in set(audit["status_normalized"])
    duplicate_ledger = pd.read_csv(run_dir / "phase2" / "duplicate_name_ledger.csv")
    assert len(duplicate_ledger) == 2
    assert duplicate_ledger["adjudication"].str.startswith("retain_distinct_coordinates").all()
    assert {"source_row_id", "run_id", "transformation_version"} <= set(
        pd.read_csv(run_dir / "phase2" / "crashes_clean.csv", nrows=1).columns
    )

    membership = pd.read_csv(run_dir / "phase3" / "crash_membership.csv")
    features = pd.read_csv(run_dir / "phase3" / "location_features.csv")
    candidates = pd.read_csv(run_dir / "phase3" / "candidate_locations.csv")
    quality3 = json.loads((run_dir / "phase3" / "quality_report.json").read_text(encoding="utf-8"))
    sensitivity = json.loads((run_dir / "phase3" / "sensitivity_config.json").read_text(encoding="utf-8"))
    assert membership["assignment_status"].eq("assigned").all()
    assert quality3["assignment_rate"] == 1.0
    assert len(features) == len(candidates)
    assert features["nearest_school_distance_m"].notna().all()
    assert features["exposure_adjusted_metric_available"].eq(False).all()
    assert features["exposure_limitation"].eq("EXPOSURE_ADJUSTMENT_NOT_APPLIED").all()
    assert sensitivity["primary_cell_size_m"] == 250
    assert sensitivity["may_replace_primary_automatically"] is False
    location_decision = (run_dir / "phase3" / "location_decision.md").read_text(encoding="utf-8")
    assert not any(line.startswith("+") for line in location_decision.splitlines())

    for phase in range(4):
        handoff = json.loads((run_dir / f"phase{phase}" / "handoff.json").read_text(encoding="utf-8"))
        assert handoff["handoff_decision"] == "GO"
        for artifact in handoff["deliverables"]:
            artifact_path = root / artifact["path"]
            assert artifact_path.exists()
            assert sha256_file(artifact_path) == artifact["sha256"]

    for source in (root / "data" / "Norfolk").iterdir():
        assert source.read_bytes() == source_hashes_before[source.name]


def test_changed_configuration_cannot_resume_existing_run(fixture_project: tuple[Path, Path]) -> None:
    root, config_path = fixture_project
    execute(root, config_path, "resume-run", 0, 0)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["location_unit"]["cell_size_m"] = 300
    config_path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match="configuration changed"):
        execute(root, config_path, "resume-run", 1, 1)
