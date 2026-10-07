import numpy as np
import pandas as pd
import pytest

from stis.features import make_features
from stis.io import validate_history


def test_features_cannot_see_current_or_future_targets(history):
    original = make_features(history)
    altered = history.copy()
    altered.loc[72:, "visitor_arrivals"] = 1e9
    pd.testing.assert_frame_equal(original.iloc[:73], make_features(altered).iloc[:73])
    assert original.loc[72, "log_roll3"] == pytest.approx(
        np.log1p(history.loc[69:71, "visitor_arrivals"]).mean()
    )


def test_calendar_lag_does_not_jump_pandemic(history):
    row = history.index[history["date"] == "2023-01-01"][0]
    features = make_features(history)
    assert features.loc[row, "log_lag1"] == pytest.approx(np.log1p(history.loc[row - 1, "visitor_arrivals"]))
    assert history.loc[row - 1, "date"] == pd.Timestamp("2022-12-01")


@pytest.mark.parametrize(
    "mutation", ["duplicate", "gap", "negative", "infinite", "missing", "midmonth", "nat", "timezone"]
)
def test_invalid_inputs_fail_explicitly(history, mutation):
    if mutation == "duplicate":
        history = pd.concat([history, history.tail(1)])
    elif mutation == "gap":
        history = history.drop(index=60)
    elif mutation == "midmonth":
        history.loc[0, "date"] += pd.Timedelta(days=1)
    elif mutation == "nat":
        history.loc[0, "date"] = pd.NaT
    elif mutation == "timezone":
        history["date"] = history["date"].dt.tz_localize("UTC")
    else:
        history.loc[0, "visitor_arrivals"] = {"negative": -1, "infinite": np.inf, "missing": np.nan}[mutation]
    with pytest.raises(ValueError):
        validate_history(history)


def test_zero_is_a_valid_observation_and_sorting_is_stable(history):
    history.loc[60, "visitor_arrivals"] = 0
    result = validate_history(history.sample(frac=1, random_state=42))
    assert result.loc[60, "visitor_arrivals"] == 0
    assert np.isfinite(make_features(result).iloc[61]).all()
