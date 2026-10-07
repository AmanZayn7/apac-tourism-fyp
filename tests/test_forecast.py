import numpy as np
import pandas as pd
import pytest

from stis.config import CANDIDATES
from stis.forecast import forecast


@pytest.mark.parametrize("candidate", list(CANDIDATES))
def test_all_candidates_have_dynamic_dates_finite_output_and_no_mutation(history, candidate):
    before = history.copy(deep=True)
    result = forecast(history.iloc[:-5], candidate, 6)
    assert result["date"].iloc[0] == pd.Timestamp("2024-08-01")
    assert result["date"].iloc[-1] == pd.Timestamp("2025-01-01")
    assert np.isfinite(result["forecast"]).all()
    assert (result["forecast"] >= 0).all()
    pd.testing.assert_frame_equal(history, before)


def test_seasonal_naive_repeats_exact_calendar_months(history):
    result = forecast(history, "snaive")
    np.testing.assert_array_equal(result["forecast"], history["visitor_arrivals"].tail(12))


def test_recursion_uses_future_month_and_its_own_predictions(history, monkeypatch):
    captured = []

    class Recorder:
        def fit(self, x, y):
            return self

        def predict(self, x):
            captured.append(x.copy())
            return np.array([np.log1p(1234)])

    monkeypatch.setattr("stis.forecast.make_estimator", lambda _: Recorder())
    forecast(history, "ridge_1", 2)
    assert captured[0].iloc[0]["log_lag1"] == pytest.approx(np.log1p(history["visitor_arrivals"].iloc[-1]))
    assert captured[0].iloc[0]["month_sin"] == pytest.approx(np.sin(2 * np.pi / 12))
    assert captured[1].iloc[0]["log_lag1"] == pytest.approx(np.log1p(1234))
    assert captured[1].iloc[0]["month_sin"] == pytest.approx(np.sin(4 * np.pi / 12))


@pytest.mark.parametrize("horizon", [0, -1, 13, True, 1.5])
def test_invalid_horizon(history, horizon):
    with pytest.raises(ValueError, match="Horizon"):
        forecast(history, "snaive", horizon)


def test_unknown_model_and_short_history(history):
    with pytest.raises(ValueError, match="Unknown"):
        forecast(history, "magic")
    with pytest.raises(ValueError, match="At least"):
        forecast(history.head(24), "rf")


def test_repeated_random_forest_forecast_is_deterministic(history):
    pd.testing.assert_frame_equal(forecast(history, "rf"), forecast(history, "rf"))


def test_extreme_log_prediction_is_bounded_and_flagged(history, monkeypatch):
    class Explosive:
        def fit(self, x, y):
            return self

        def predict(self, x):
            return np.array([1000.0])

    monkeypatch.setattr("stis.forecast.make_estimator", lambda _: Explosive())
    result = forecast(history, "ridge_1")
    np.testing.assert_allclose(result["forecast"], 2 * history["visitor_arrivals"].max())
    assert result["guardrail_applied"].all()


def test_nonfinite_estimator_output_fails_instead_of_becoming_zero(history, monkeypatch):
    class Invalid:
        def fit(self, x, y):
            return self

        def predict(self, x):
            return np.array([np.nan])

    monkeypatch.setattr("stis.forecast.make_estimator", lambda _: Invalid())
    with pytest.raises(ValueError, match="Non-finite"):
        forecast(history, "ridge_1")
