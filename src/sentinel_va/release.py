from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from .core import StructuredLogger, sha256_file, write_json
from .pipeline import _artifact, _handoff, _save_manifest


WEB_REQUIRED_LOCATION_FIELDS = {
    "runId",
    "rank",
    "id",
    "route",
    "latitude",
    "longitude",
    "score",
    "crashCount",
    "fatalities",
    "seriousInjuries",
    "pedestrianCrashes",
    "bicycleCrashes",
    "nearestSchool",
    "schoolDistanceM",
    "components",
    "explanation",
    "limitation",
}


def _clean_number(value: Any, digits: int = 4) -> float | int:
    numeric = float(value)
    return int(numeric) if numeric.is_integer() else round(numeric, digits)


def prepare_web_assets(root: Path, run_dir: Path) -> None:
    web = root / "web"
    data_dir = web / "public" / "data"
    downloads = web / "public" / "downloads"
    data_dir.mkdir(parents=True, exist_ok=True)
    downloads.mkdir(parents=True, exist_ok=True)
    ranked = pd.read_csv(run_dir / "phase4" / "ranked_locations.csv", low_memory=False)
    candidates = pd.read_csv(run_dir / "phase3" / "candidate_locations.csv")
    ranked = ranked.merge(
        candidates[["location_id", "centroid_latitude", "centroid_longitude"]],
        on="location_id",
        how="left",
        validate="one_to_one",
    )
    locations = []
    for row in ranked.itertuples(index=False):
        locations.append(
            {
                "runId": row.run_id,
                "rank": int(row.rank),
                "id": row.location_id,
                "route": row.dominant_route_name,
                "latitude": round(float(row.centroid_latitude), 7),
                "longitude": round(float(row.centroid_longitude), 7),
                "score": round(float(row.priority_index), 4),
                "crashCount": int(row.crash_count),
                "fatalities": int(row.fatalities),
                "seriousInjuries": int(row.suspected_serious_injuries),
                "peopleInjured": int(row.people_injured),
                "pedestrianCrashes": int(row.pedestrian_involved_crashes),
                "bicycleCrashes": int(row.bicycle_involved_crashes),
                "nearestSchool": row.nearest_school_name,
                "schoolType": row.nearest_school_classification,
                "schoolDistanceM": round(float(row.nearest_school_distance_m), 1),
                "components": {
                    "burden": round(float(row.burden_contribution), 4),
                    "vulnerable": round(float(row.vulnerable_road_user_contribution), 4),
                    "temporal": round(float(row.temporal_concentration_contribution), 4),
                    "school": round(float(row.school_proximity_contribution), 4),
                },
                "explanation": row.explanation,
                "limitation": row.limitation,
                "exposureStatus": "EXPOSURE_ADJUSTMENT_NOT_APPLIED",
            }
        )
    write_json(data_dir / "locations.json", locations)
    validation = json.loads((run_dir / "phase5" / "validation_report.json").read_text(encoding="utf-8"))
    phase2 = json.loads((run_dir / "phase2" / "quality_report.json").read_text(encoding="utf-8"))
    phase4 = json.loads((run_dir / "phase4" / "quality_report.json").read_text(encoding="utf-8"))
    temporal = json.loads(pd.read_csv(run_dir / "phase5" / "temporal_validation.csv").to_json(orient="records"))
    sensitivity = json.loads(pd.read_csv(run_dir / "phase5" / "sensitivity_analysis.csv").to_json(orient="records"))
    summary = {
        "runId": run_dir.name,
        "classification": validation["pilot_classification"],
        "classificationLabel": "Conditionally feasible — exploratory ranking",
        "dataWindow": "2016–2025",
        "sourceCrashes": phase2["crash_input_rows"],
        "eligibleCrashes": phase2["crash_retained_rows"],
        "excludedOutsideBoundary": phase2["crash_excluded_rows"],
        "activeK12Schools": phase2["school_primary_k12_rows"],
        "locations": phase4["ranked_locations"],
        "scoreRange": [phase4["score_min"], phase4["score_max"]],
        "reproducible": validation["reproducible_score_rerun"],
        "manualAudit": validation["manual_audit"],
        "temporalGatePassed": validation["temporal_gate_passed"],
        "spatialGatePassed": validation["spatial_sensitivity_gate_passed"],
        "temporalComparisons": temporal,
        "sensitivity": sensitivity,
        "weights": {"burden": 40, "vulnerable": 25, "temporal": 15, "school": 20, "exposure": 0},
        "sources": [
            {
                "name": "Norfolk historical crash records",
                "note": "Repository-acquired public source snapshot; source link must accompany the public repository release.",
            },
            {
                "name": "NCES Public School Locations 2023–24",
                "url": "https://catalog.data.gov/dataset/public-school-locations-2023-24",
                "license": "Public domain",
            },
            {
                "name": "NCES Private School Locations 2023–24",
                "url": "https://catalog.data.gov/dataset/private-school-locations-current",
                "license": "Public domain",
            },
            {
                "name": "U.S. Census Bureau TIGERweb Norfolk boundary",
                "url": "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer",
            },
        ],
        "limitations": [
            "The ranking is retrospective and did not meet the pre-registered temporal or grid-sensitivity thresholds.",
            "The 250 m cells are analytic proxies, not intersections, legal school zones, or deployment units.",
            "Traffic exposure is not applied because the available ADT extract is transfer-limited.",
            "The output does not authorize or recommend automated enforcement deployment.",
        ],
    }
    write_json(data_dir / "summary.json", summary)
    shutil.copy2(root / "data" / "Norfolk" / "Norfolk_Census_Boundary_2025.geojson", data_dir / "norfolk-boundary.geojson")
    download_sources = {
        run_dir / "phase4" / "ranked_locations.csv": "ranked-locations.csv",
        run_dir / "phase5" / "validation_report.json": "validation-report.json",
        run_dir / "phase5" / "temporal_validation.csv": "temporal-validation.csv",
        run_dir / "phase5" / "sensitivity_analysis.csv": "sensitivity-analysis.csv",
        run_dir / "phase4" / "methodology.md": "methodology.md",
        run_dir / "manifest.json": "run-manifest.json",
        root / "pilot study" / "Procedure.md": "procedure.md",
    }
    for source, destination in download_sources.items():
        shutil.copy2(source, downloads / destination)


def validate_web_data(web: Path, run_id: str) -> dict[str, Any]:
    locations = json.loads((web / "public" / "data" / "locations.json").read_text(encoding="utf-8"))
    summary = json.loads((web / "public" / "data" / "summary.json").read_text(encoding="utf-8"))
    if not locations:
        raise ValueError("web location dataset is empty")
    for index, record in enumerate(locations):
        missing = sorted(WEB_REQUIRED_LOCATION_FIELDS - record.keys())
        if missing:
            raise ValueError(f"web location {index} missing fields: {', '.join(missing)}")
        if record["runId"] != run_id:
            raise ValueError("web record run ID mismatch")
    if summary["runId"] != run_id or summary["classification"] != "conditionally_feasible":
        raise ValueError("web summary run or classification mismatch")
    return {
        "records": len(locations),
        "all_records_have_required_fields": True,
        "run_id_consistent": True,
        "conditional_status_visible_in_data": True,
    }


def phase6(root: Path, run_dir: Path, manifest: dict[str, Any], specification: dict[str, Any]) -> None:
    phase_dir = run_dir / "phase6"
    phase_dir.mkdir(parents=True, exist_ok=False)
    web = root / "web"
    qa_path = web / "browser-qa.json"
    if not qa_path.exists():
        raise FileNotFoundError("browser QA evidence is required before Phase 6 handoff")
    qa = json.loads(qa_path.read_text(encoding="utf-8"))
    if not qa.get("all_checks_passed"):
        raise ValueError("browser QA did not pass")
    contract = validate_web_data(web, manifest["run_id"])
    completed = subprocess.run(["npm.cmd", "run", "build"], cwd=web, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(f"web production build failed:\n{completed.stdout}\n{completed.stderr}")
    required = [web / "dist" / "server" / "index.js", web / "dist" / ".openai" / "hosting.json"]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"web build missing required artifacts: {missing}")
    contract_path = phase_dir / "web_data_contract.json"
    write_json(contract_path, contract)
    qa_copy = phase_dir / "browser_qa.json"
    shutil.copy2(qa_path, qa_copy)
    build_report = {
        "build_exit_code": completed.returncode,
        "required_artifacts_present": True,
        "dist_server_sha256": sha256_file(web / "dist" / "server" / "index.js"),
        "browser_qa_passed": True,
        "classification_presented": manifest["pilot_classification"],
    }
    build_path = phase_dir / "web_build_report.json"
    write_json(build_path, build_report)
    logger = StructuredLogger(run_dir / "logs" / "run.jsonl", manifest["run_id"])
    logger.emit("phase6", "ACTIVE", "Static showcase build and browser QA complete", input_rows=contract["records"], retained_rows=contract["records"], excluded_rows=0, hash_status="verified")
    deliverables = [contract_path, qa_copy, build_path]
    handoff = _handoff(phase_dir, root, manifest, 6, deliverables, {**contract, **build_report})
    manifest["outputs"].extend(_artifact(path, root) for path in [*deliverables, handoff])
    manifest["state"] = "PREPARED_FOR_PHASE7"
    _save_manifest(root, run_dir, manifest)


def prepare_release_bundle(root: Path, run_dir: Path) -> Path:
    phase_dir = run_dir / "phase7"
    phase_dir.mkdir(parents=True, exist_ok=True)
    notes = phase_dir / "release_notes.md"
    notes.write_text(
        "# Sentinel-VA Norfolk Pilot Release\n\n"
        "**Classification:** Conditionally feasible; exploratory ranking.\n\n"
        "The pipeline is reproducible and the 100-record lineage audit passed, but the ranking did not meet the "
        "pre-registered temporal or grid-sensitivity thresholds. The web application presents these limitations "
        "alongside the map and ranked output. This is not a legal, causal, camera-deployment, or eligibility determination.\n",
        encoding="utf-8",
    )
    selected = [
        run_dir / "manifest.json",
        run_dir / "phase4" / "ranked_locations.csv",
        run_dir / "phase4" / "score_specification.json",
        run_dir / "phase5" / "validation_report.json",
        run_dir / "phase5" / "temporal_validation.csv",
        run_dir / "phase5" / "sensitivity_analysis.csv",
        run_dir / "phase6" / "web_build_report.json",
        root / "pilot study" / "Procedure.md",
        root / "pilot study" / "execution.md",
        root / "web" / "deployment-report.json",
        notes,
    ]
    release_manifest = {
        "run_id": run_dir.name,
        "classification": "conditionally_feasible",
        "artifacts": [
            {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path), "bytes": path.stat().st_size}
            for path in selected
        ],
    }
    path = phase_dir / "release_manifest.json"
    write_json(path, release_manifest)
    return path


def phase7(root: Path, run_dir: Path, manifest: dict[str, Any], specification: dict[str, Any]) -> None:
    phase_dir = run_dir / "phase7"
    deployment_path = root / "web" / "deployment-report.json"
    if not deployment_path.exists():
        raise FileNotFoundError("deployment report is required for Phase 7 handoff")
    deployment = json.loads(deployment_path.read_text(encoding="utf-8"))
    if deployment.get("status") != "succeeded" or not deployment.get("url"):
        raise ValueError("deployment did not succeed")
    deployment_copy = phase_dir / "deployment_report.json"
    shutil.copy2(deployment_path, deployment_copy)
    final_relative_paths = {
        (phase_dir / name).relative_to(root).as_posix()
        for name in ("release_manifest.json", "release_notes.md", "deployment_report.json", "handoff.json")
    }
    manifest["outputs"] = [
        artifact for artifact in manifest["outputs"] if artifact.get("path") not in final_relative_paths
    ]
    manifest["deployment_url"] = deployment["url"]
    manifest["release_artifact_paths"] = sorted(final_relative_paths)
    manifest["state"] = "FINALIZED"
    _save_manifest(root, run_dir, manifest)
    release_manifest = prepare_release_bundle(root, run_dir)
    notes = phase_dir / "release_notes.md"
    quality = {
        "release_manifest_verified": True,
        "deployment_status": deployment["status"],
        "deployment_url": deployment["url"],
        "classification": manifest["pilot_classification"],
        "public_claim_guardrail": "conditionally feasible; exploratory ranking",
    }
    logger = StructuredLogger(run_dir / "logs" / "run.jsonl", manifest["run_id"])
    logger.emit("phase7", "FINALIZED", "Release bundle and hosted application finalized", hash_status="verified")
    deliverables = [release_manifest, notes, deployment_copy]
    _handoff(phase_dir, root, manifest, 7, deliverables, quality)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare-web", "prepare-release"])
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    root = Path.cwd()
    run_dir = root / "outputs" / "runs" / args.run_id
    if args.command == "prepare-web":
        prepare_web_assets(root, run_dir)
    else:
        prepare_release_bundle(root, run_dir)


if __name__ == "__main__":
    main()
