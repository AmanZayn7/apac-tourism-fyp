"""Auditable presentation: cards, charts and CSVs share the same twelve estimates."""

import numpy as np
import pandas as pd


def forecast_view(records, model, origin):
    frame = pd.DataFrame(records)
    frame = frame.loc[frame["model"] == model].copy().sort_values("date").reset_index(drop=True)
    frame["date"] = pd.to_datetime(frame["date"])
    expected = pd.date_range(pd.Timestamp(origin) + pd.offsets.MonthBegin(), periods=12, freq="MS")
    if len(frame) != 12 or not np.array_equal(frame["date"].values, expected.values):
        raise ValueError("Forecast must contain exactly the twelve months immediately after the data cutoff.")
    if not np.isfinite(frame["forecast"]).all() or (frame["forecast"] < 0).any():
        raise ValueError("Forecasts must be finite and nonnegative.")
    # Round once per month. Every displayed aggregate reconciles to this same series.
    frame["forecast_arrivals"] = np.rint(frame["forecast"]).astype("int64")
    values = frame["forecast_arrivals"]
    summary = {
        "total": int(values.sum()),
        "average": float(values.mean()),
        "maximum": int(values.max()),
        "minimum": int(values.min()),
        "peak_months": frame.loc[values == values.max(), "date"].dt.strftime("%b %Y").tolist(),
        "low_months": frame.loc[values == values.min(), "date"].dt.strftime("%b %Y").tolist(),
    }
    return frame, summary
