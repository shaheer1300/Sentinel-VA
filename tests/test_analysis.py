from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import pytest

from sentinel_va.scoring import load_execution_config, percentile_rank, score_features
from sentinel_va.validation import benjamini_hochberg, bootstrap_spearman_ci, jaccard, wilson_interval


def specification() -> dict:
    return {
        "specification_version": "test-v1",
        "frozen_before_rank_inspection": True,
        "scoring": {
            "method": "transparent_weighted_percentile_index",
            "score_scale": 100,
            "normalization": "empirical_percentile_rank_average_ties",
            "tie_break": ["priority_index_desc", "crash_count_desc", "location_id_asc"],
            "weights": {
                "burden": 0.40,
                "vulnerable_road_user": 0.25,
                "temporal_concentration": 0.15,
                "school_proximity": 0.20,
                "exposure": 0.0,
            },
        },
        "publication": {"limitation": "test limitation"},
    }


def feature_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "location_id": ["b", "a", "c"],
            "crash_count": [10, 20, 5],
            "fatalities": [0, 1, 0],
            "suspected_serious_injuries": [0, 2, 0],
            "people_injured": [1, 4, 0],
            "pedestrian_involved_crashes": [0, 2, 0],
            "bicycle_involved_crashes": [1, 1, 0],
            "pedestrian_fatalities": [0, 0, 0],
            "pedestrians_injured": [0, 2, 0],
            "hour_bin_concentration": [0.4, 0.6, 0.5],
            "weekday_concentration": [0.2, 0.4, 0.3],
            "nearest_school_distance_m": [500.0, 100.0, 1000.0],
            "nearest_school_name": ["B", "A", "C"],
            "nearest_school_classification": ["middle", "elementary", "high"],
        }
    )


def test_percentile_rank_average_ties() -> None:
    actual = percentile_rank(pd.Series([1, 2, 2, 4])).tolist()
    assert actual == pytest.approx([0.0, 0.5, 0.5, 1.0])


def test_score_is_deterministic_explainable_and_reconciled() -> None:
    first = score_features(feature_fixture(), specification(), "run")
    second = score_features(feature_fixture(), specification(), "run")
    pd.testing.assert_frame_equal(first, second)
    assert first.iloc[0]["location_id"] == "a"
    contributions = [column for column in first.columns if column.endswith("_contribution")]
    assert first[contributions].sum(axis=1).to_numpy() == pytest.approx(first["priority_index"].to_numpy())
    assert first["explanation"].str.len().gt(0).all()
    assert first["limitation"].eq("test limitation").all()
    assert first["exposure_contribution"].eq(0.0).all()


def test_invalid_weight_or_exposure_specification_is_rejected(tmp_path) -> None:
    invalid = specification()
    invalid["scoring"]["weights"]["exposure"] = 0.1
    path = tmp_path / "invalid.json"
    import json

    path.write_text(json.dumps(invalid), encoding="utf-8")
    with pytest.raises(ValueError, match="sum to 1.0|exposure weight"):
        load_execution_config(path)


def test_validation_statistics_known_results() -> None:
    assert jaccard({"a", "b"}, {"b", "c"}) == pytest.approx(1 / 3)
    low, high = wilson_interval(100, 100)
    assert low > 0.96
    assert high <= 1.0 + 1e-12
    adjusted = benjamini_hochberg([0.01, 0.04, 0.03])
    assert adjusted == pytest.approx([0.03, 0.04, 0.04])
    ci_low, ci_high = bootstrap_spearman_ci(
        np.arange(20, dtype=float), np.arange(20, dtype=float), iterations=100, seed=7
    )
    assert ci_low == pytest.approx(1.0)
    assert ci_high == pytest.approx(1.0)
