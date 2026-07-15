from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import stat
import sys
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MANIFEST_REQUIRED = {
    "run_id",
    "project",
    "study",
    "created_at_utc",
    "config_hash",
    "source_crs",
    "analysis_crs",
    "location_unit",
    "random_seed",
    "exposure_enabled",
    "environment",
    "inputs",
    "outputs",
    "state",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def config_hash(config: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(config).encode("utf-8"))


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def generate_run_id(config: dict[str, Any]) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"norfolk-{stamp}-{config_hash(config)[:8]}-{uuid.uuid4().hex[:6]}"


def validate_manifest(manifest: dict[str, Any]) -> None:
    missing = sorted(MANIFEST_REQUIRED - manifest.keys())
    if missing:
        raise ValueError(f"manifest missing required fields: {', '.join(missing)}")
    if not manifest["run_id"] or not isinstance(manifest["inputs"], list):
        raise ValueError("manifest run_id and inputs are invalid")


def atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def atomic_write_text(path: Path, content: str) -> None:
    atomic_write_bytes(path, content.encode("utf-8"))


def write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def snapshot_file(source: Path, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    source_hash = sha256_file(source)
    if destination.exists():
        if sha256_file(destination) != source_hash:
            raise ValueError(f"existing snapshot hash mismatch for {destination}")
        return source_hash
    temporary = destination.with_suffix(destination.suffix + ".partial")
    if temporary.exists():
        temporary.unlink()
    shutil.copy2(source, temporary)
    copied_hash = sha256_file(temporary)
    if copied_hash != source_hash:
        temporary.unlink(missing_ok=True)
        raise ValueError(f"snapshot hash mismatch for {source}")
    os.replace(temporary, destination)
    destination.chmod(stat.S_IREAD)
    return source_hash


def environment_record() -> dict[str, str]:
    packages: dict[str, str] = {}
    for name in ("pandas", "numpy", "pyproj", "shapely", "pytest"):
        try:
            from importlib.metadata import version

            packages[name] = version(name)
        except Exception:
            packages[name] = "not-installed"
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        **packages,
    }


@dataclass
class StructuredLogger:
    path: Path
    run_id: str

    def emit(self, stage: str, state: str, message: str, **metrics: Any) -> None:
        record = {
            "timestamp_utc": utc_now(),
            "run_id": self.run_id,
            "stage": stage,
            "state": state,
            "message": message,
            "input_rows": metrics.pop("input_rows", None),
            "retained_rows": metrics.pop("retained_rows", None),
            "excluded_rows": metrics.pop("excluded_rows", None),
            "assignment_rate": metrics.pop("assignment_rate", None),
            "schema_errors": metrics.pop("schema_errors", 0),
            "hash_status": metrics.pop("hash_status", None),
            **metrics,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(canonical_json(record) + "\n")


def ensure_production_paths(config: dict[str, Any]) -> None:
    if not config.get("production"):
        return
    for item in config.get("inputs", []):
        normalized = item["path"].replace("\\", "/").lower()
        if "fixture" in normalized or normalized.startswith("tests/"):
            raise ValueError("production configuration may not reference test fixtures")


def new_manifest(config: dict[str, Any], run_id: str) -> dict[str, Any]:
    manifest = {
        "run_id": run_id,
        "project": config["project"],
        "study": config["study"],
        "created_at_utc": utc_now(),
        "config_hash": config_hash(config),
        "source_crs": config["source_crs"],
        "analysis_crs": config["analysis_crs"],
        "location_unit": config["location_unit"],
        "random_seed": config["random_seed"],
        "exposure_enabled": config["exposure_enabled"],
        "environment": environment_record(),
        "inputs": [],
        "outputs": [],
        "state": "PREPARED",
    }
    validate_manifest(manifest)
    return manifest
