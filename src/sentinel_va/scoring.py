from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .core import StructuredLogger, config_hash, utc_now, write_json
from .pipeline import _artifact, _handoff, _save_manifest, _write_dataframe


REQUIRED_FEATURES = {
    "location_id",
    "crash_count",
    "fatalities",
    "suspected_serious_injuries",
    "people_injured",
    "pedestrian_involved_crashes",
    "bicycle_involved_crashes",
    "pedestrian_fatalities",
    "pedestrians_injured",
    "hour_bin_concentration",
    "weekday_concentration",
    "nearest_school_distance_m",
    "nearest_school_name",
    "nearest_school_classification",
}


def load_execution_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not config.get("frozen_before_rank_inspection"):
        raise ValueError("Phase 4–7 specification must be frozen before rank inspection")
    weights = config["scoring"]["weights"]
    if not math.isclose(sum(float(value) for value in weights.values()), 1.0, abs_tol=1e-12):
        raise ValueError("scoring weights must sum to 1.0")
    if float(weights.get("exposure", -1)) != 0.0:
        raise ValueError("exposure weight must be zero while ADT is transfer-limited")
    return config


def percentile_rank(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="raise").astype(float)
    if len(numeric) <= 1:
        return pd.Series(np.zeros(len(numeric)), index=series.index, dtype=float)
    return (numeric.rank(method="average") - 1.0) / (len(numeric) - 1.0)


def score_features(features: pd.DataFrame, specification: dict[str, Any], run_id: str) -> pd.DataFrame:
    missing = sorted(REQUIRED_FEATURES - set(features.columns))
    if missing:
        raise ValueError(f"score input missing required features: {', '.join(missing)}")
    result = features.copy()
    result["burden_raw"] = (
        result["crash_count"]
        + 10.0 * result["fatalities"]
        + 5.0 * result["suspected_serious_injuries"]
        + result["people_injured"]
    )
    result["vulnerable_road_user_raw"] = (
        4.0 * result["pedestrian_involved_crashes"]
        + 3.0 * result["bicycle_involved_crashes"]
        + 10.0 * result["pedestrian_fatalities"]
        + 2.0 * result["pedestrians_injured"]
    )
    result["temporal_concentration_raw"] = (
        0.5 * result["hour_bin_concentration"] + 0.5 * result["weekday_concentration"]
    )
    result["school_proximity_raw"] = np.exp(-result["nearest_school_distance_m"].astype(float) / 500.0)
    result["burden_normalized"] = percentile_rank(result["burden_raw"])
    result["vulnerable_road_user_normalized"] = percentile_rank(result["vulnerable_road_user_raw"])
    result["temporal_concentration_normalized"] = percentile_rank(result["temporal_concentration_raw"])
    result["school_proximity_normalized"] = percentile_rank(result["school_proximity_raw"])
    weights = specification["scoring"]["weights"]
    scale = float(specification["scoring"]["score_scale"])
    result["burden_contribution"] = scale * float(weights["burden"]) * result["burden_normalized"]
    result["vulnerable_road_user_contribution"] = (
        scale * float(weights["vulnerable_road_user"]) * result["vulnerable_road_user_normalized"]
    )
    result["temporal_concentration_contribution"] = (
        scale * float(weights["temporal_concentration"]) * result["temporal_concentration_normalized"]
    )
    result["school_proximity_contribution"] = (
        scale * float(weights["school_proximity"]) * result["school_proximity_normalized"]
    )
    result["exposure_contribution"] = 0.0
    contribution_columns = [
        "burden_contribution",
        "vulnerable_road_user_contribution",
        "temporal_concentration_contribution",
        "school_proximity_contribution",
        "exposure_contribution",
    ]
    result["priority_index"] = result[contribution_columns].sum(axis=1)
    numeric_output = [
        "burden_raw",
        "vulnerable_road_user_raw",
        "temporal_concentration_raw",
        "school_proximity_raw",
        "burden_normalized",
        "vulnerable_road_user_normalized",
        "temporal_concentration_normalized",
        "school_proximity_normalized",
        *contribution_columns,
        "priority_index",
    ]
    result[numeric_output] = result[numeric_output].round(10)
    result = result.sort_values(
        ["priority_index", "crash_count", "location_id"],
        ascending=[False, False, True],
        kind="mergesort",
    ).reset_index(drop=True)
    result.insert(0, "rank", np.arange(1, len(result) + 1, dtype=np.int64))
    result["explanation"] = result.apply(
        lambda row: (
            f"Historical burden {row['burden_contribution']:.2f}/40; vulnerable-road-user evidence "
            f"{row['vulnerable_road_user_contribution']:.2f}/25; temporal concentration "
            f"{row['temporal_concentration_contribution']:.2f}/15; active K-12 proximity "
            f"{row['school_proximity_contribution']:.2f}/20. Nearest school: "
            f"{row['nearest_school_name']} ({row['nearest_school_distance_m']:.0f} m)."
        ),
        axis=1,
    )
    result["limitation"] = specification["publication"]["limitation"]
    result["run_id"] = run_id
    result["scoring_specification_version"] = specification["specification_version"]
    return result


def _dominant_route_table(run_dir: Path) -> pd.DataFrame:
    crashes = pd.read_csv(
        run_dir / "phase2" / "crashes_clean.csv",
        usecols=["source_row_id", "Route or Street Name"],
        low_memory=False,
    )
    membership = pd.read_csv(run_dir / "phase3" / "crash_membership.csv", usecols=["source_row_id", "location_id"])
    joined = membership.merge(crashes, on="source_row_id", how="left", validate="one_to_one")

    def stable_mode(values: pd.Series) -> str:
        counts = values.fillna("Unknown roadway").astype(str).value_counts()
        maximum = counts.max()
        return sorted(counts[counts.eq(maximum)].index.tolist())[0]

    return joined.groupby("location_id", sort=True)["Route or Street Name"].agg(stable_mode).rename("dominant_route_name").reset_index()


def phase4(root: Path, run_dir: Path, manifest: dict[str, Any], specification: dict[str, Any]) -> None:
    phase_dir = run_dir / "phase4"
    phase_dir.mkdir(parents=True, exist_ok=False)
    manifest["phase4_7_specification_hash"] = config_hash(specification)
    manifest["phase4_7_specification_path"] = "configs/norfolk_phase4_7.json"
    features = pd.read_csv(run_dir / "phase3" / "location_features.csv", low_memory=False)
    scores = score_features(features, specification, manifest["run_id"])
    routes = _dominant_route_table(run_dir)
    scores = scores.merge(routes, on="location_id", how="left", validate="one_to_one")
    column_order = ["rank", "location_id", "dominant_route_name"] + [
        column for column in scores.columns if column not in {"rank", "location_id", "dominant_route_name"}
    ]
    scores = scores[column_order]
    score_components_path = phase_dir / "score_components.csv"
    ranked_path = phase_dir / "ranked_locations.csv"
    top10_path = phase_dir / "top10_locations.csv"
    _write_dataframe(score_components_path, scores.drop(columns=["rank", "dominant_route_name"]))
    _write_dataframe(ranked_path, scores)
    _write_dataframe(top10_path, scores.head(10))
    specification_path = phase_dir / "score_specification.json"
    write_json(specification_path, specification)
    methodology_path = phase_dir / "methodology.md"
    methodology_path.write_text(
        "# Phase 4 Explainable Scoring Methodology\n\n"
        "The Norfolk pilot uses a transparent weighted percentile index on a 0–100 scale. "
        "Historical burden contributes 40 points, vulnerable-road-user evidence 25, temporal concentration 15, "
        "and proximity to a validated active K–12 school 20. Exposure contributes zero because the available ADT "
        "extract is incomplete. Empirical percentile ranks use average ranks for ties. The index is a retrospective "
        "prioritization aid, not a crash probability, legal determination, or camera recommendation.\n",
        encoding="utf-8",
    )
    contribution_columns = [column for column in scores.columns if column.endswith("_contribution")]
    recomputed = scores[contribution_columns].sum(axis=1).round(10)
    explainable = scores["explanation"].notna().all() and scores[contribution_columns].notna().all().all()
    quality = {
        "ranked_locations": int(len(scores)),
        "score_min": float(scores["priority_index"].min()),
        "score_max": float(scores["priority_index"].max()),
        "weights_sum": float(sum(specification["scoring"]["weights"].values())),
        "exposure_weight": float(specification["scoring"]["weights"]["exposure"]),
        "component_reconciliation_max_absolute_difference": float((scores["priority_index"] - recomputed).abs().max()),
        "all_rows_explainable": bool(explainable),
        "top10_explainable": bool(scores.head(10)["explanation"].notna().all()),
        "deterministic_tie_break": specification["scoring"]["tie_break"],
    }
    if not explainable or quality["component_reconciliation_max_absolute_difference"] > 1e-8:
        raise ValueError("Phase 4 explainability or component reconciliation failed")
    quality_path = phase_dir / "quality_report.json"
    write_json(quality_path, quality)
    logger = StructuredLogger(run_dir / "logs" / "run.jsonl", manifest["run_id"])
    logger.emit("phase4", "ACTIVE", "Explainable scoring and ranking complete", input_rows=len(features), retained_rows=len(scores), excluded_rows=0, hash_status="verified")
    deliverables = [score_components_path, ranked_path, top10_path, specification_path, methodology_path, quality_path]
    handoff = _handoff(phase_dir, root, manifest, 4, deliverables, quality)
    manifest["outputs"].extend(_artifact(path, root) for path in [*deliverables, handoff])
    manifest["state"] = "PREPARED_FOR_PHASE5"
    _save_manifest(root, run_dir, manifest)
