from __future__ import annotations

import json
from pathlib import Path

import pytest

from sentinel_va import core


def complete_manifest() -> dict:
    return {
        "run_id": "test-run",
        "project": "Sentinel-VA",
        "study": "Norfolk pilot",
        "created_at_utc": "2026-07-12T00:00:00+00:00",
        "config_hash": "abc",
        "source_crs": "EPSG:4326",
        "analysis_crs": "EPSG:26918",
        "location_unit": {"type": "fixed_grid"},
        "random_seed": 1,
        "exposure_enabled": False,
        "environment": {},
        "inputs": [],
        "outputs": [],
        "state": "PREPARED",
    }


def test_manifest_contract_rejects_missing_and_accepts_complete() -> None:
    manifest = complete_manifest()
    core.validate_manifest(manifest)
    del manifest["run_id"]
    with pytest.raises(ValueError, match="run_id"):
        core.validate_manifest(manifest)


def test_config_hash_changes_for_material_setting() -> None:
    first = {"source_crs": "EPSG:4326", "cell_size": 250}
    second = {"source_crs": "EPSG:4326", "cell_size": 300}
    assert core.config_hash(first) != core.config_hash(second)
    assert core.config_hash(first) == core.config_hash(dict(reversed(list(first.items()))))


def test_run_ids_are_unique() -> None:
    config = {"a": 1}
    assert core.generate_run_id(config) != core.generate_run_id(config)


def test_structured_log_has_required_fields(tmp_path: Path) -> None:
    path = tmp_path / "run.jsonl"
    logger = core.StructuredLogger(path, "run-1")
    logger.emit("smoke", "ACTIVE", "ok", input_rows=2, retained_rows=1, excluded_rows=1)
    logger.emit("smoke", "ABORTED", "controlled failure", schema_errors=1)
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    required = {
        "timestamp_utc",
        "run_id",
        "stage",
        "state",
        "message",
        "input_rows",
        "retained_rows",
        "excluded_rows",
        "assignment_rate",
        "schema_errors",
        "hash_status",
    }
    assert all(required <= record.keys() for record in records)
    assert records[1]["state"] == "ABORTED"


def test_atomic_write_cleans_partial_on_replace_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    destination = tmp_path / "final.txt"

    def fail_replace(source: Path, target: Path) -> None:
        raise OSError("injected")

    monkeypatch.setattr(core.os, "replace", fail_replace)
    with pytest.raises(OSError, match="injected"):
        core.atomic_write_text(destination, "content")
    assert not destination.exists()
    assert list(tmp_path.iterdir()) == []


def test_snapshot_detects_integrity_and_preserves_content(tmp_path: Path) -> None:
    source = tmp_path / "source.csv"
    destination = tmp_path / "raw" / "source.csv"
    source.write_bytes(b"a,b\n1,2\n")
    digest = core.snapshot_file(source, destination)
    assert digest == core.sha256_file(source) == core.sha256_file(destination)
    assert source.read_bytes() == destination.read_bytes()


def test_production_configuration_rejects_fixture_input() -> None:
    config = {"production": True, "inputs": [{"path": "tests/fixtures/crashes.csv"}]}
    with pytest.raises(ValueError, match="test fixtures"):
        core.ensure_production_paths(config)

