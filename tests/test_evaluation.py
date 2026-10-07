import numpy as np
import pandas as pd
import pytest

from stis.evaluate import error_band_radius, evaluate_city, evaluate_window, select_model, validation_origins
from stis.metrics import metrics


def test_validation_windows_end_before_holdout(history):
    assert validation_origins(108) == [36, 48, 60, 72, 84, 96]
    with pytest.raises(ValueError, match="120"):
        validation_origins(107)


def test_selection_never_receives_holdout(history, monkeypatch):
    actual_select = select_model
    selections = []

    def spy(development):
        assert development["date"].max() == pd.Timestamp("2023-12-01")
        result = actual_select(development)
        selections.append(result[:2])
        return result

    monkeypatch.setattr("stis.evaluate.select_model", spy)
    # Keep this regression fast while exercising the actual chronological selector.
    monkeypatch.setattr("stis.evaluate.CANDIDATES", {"snaive": "Seasonal", "ridge_10": "Ridge"})
    original = evaluate_city(history)
    history.loc[108:, "visitor_arrivals"] *= 50
    changed = evaluate_city(history)
    assert selections[0] == selections[1]
    assert original["holdout_metrics"] != changed["holdout_metrics"]
    np.testing.assert_array_equal(
        [r["predicted"] for r in original["holdout"]], [r["predicted"] for r in changed["holdout"]]
    )


def test_evaluation_rejects_misaligned_dates(history):
    with pytest.raises(ValueError, match="immediately follow"):
        evaluate_window(history.head(60), history.iloc[61:73], "snaive")


def test_metrics_report_zero_denominators_and_keep_negative_r2():
    zeros = metrics([0, 0], [1, 1], np.zeros(24))
    assert zeros["mae"] == 1
    assert all(zeros[k] is None for k in ("r2", "mase", "mape_pct", "wape_pct"))
    mixed = metrics([0, 10], [2, 8], np.arange(24))
    assert mixed["mape_n"] == 1
    assert mixed["mape_pct"] == 20
    assert mixed["wape_pct"] == 40
    assert metrics([1, 2], [100, 100], np.arange(24))["r2"] < 0
    with pytest.raises(ValueError):
        metrics([1], [np.nan], np.arange(24))


def test_error_radius_is_finite_sample_order_statistic():
    assert error_band_radius(np.arange(1, 73)) == 59
