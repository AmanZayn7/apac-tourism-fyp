"""Identical calendar-aligned feature construction for fitting and inference."""

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "log_lag1",
    "log_lag3",
    "log_lag6",
    "log_lag12",
    "log_roll3",
    "log_roll6",
    "month_sin",
    "month_cos",
]


def make_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Input is a validated monthly calendar, optionally with one future NaN row.

    The feature row for t uses only targets before t. Calendar terms describe t.
    No pandemic rows are removed: one row always represents one calendar month.
    """
    log_y = np.log1p(frame["visitor_arrivals"])
    out = pd.DataFrame(index=frame.index)
    for lag in (1, 3, 6, 12):
        out[f"log_lag{lag}"] = log_y.shift(lag)
    for window in (3, 6):
        out[f"log_roll{window}"] = log_y.shift(1).rolling(window).mean()
    month = pd.to_datetime(frame["date"]).dt.month
    out["month_sin"] = np.sin(2 * np.pi * month / 12)
    out["month_cos"] = np.cos(2 * np.pi * month / 12)
    return out[FEATURE_COLUMNS]
