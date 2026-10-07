"""Strict input contracts. Never silently drop, interpolate, or backfill targets."""

from pathlib import Path

import numpy as np
import pandas as pd

from .config import CITIES, RAW_DIR


def validate_history(frame: pd.DataFrame, *, min_rows: int = 1) -> pd.DataFrame:
    required = {"date", "visitor_arrivals"}
    if not required.issubset(frame.columns):
        raise ValueError("Required columns: date, visitor_arrivals.")
    out = frame[["date", "visitor_arrivals"]].copy()
    out["date"] = pd.to_datetime(out["date"], errors="raise")
    if out["date"].isna().any() or out["date"].dt.tz is not None:
        raise ValueError("Dates must be non-null and timezone-naive.")
    if not (out["date"].dt.is_month_start & (out["date"] == out["date"].dt.normalize())).all():
        raise ValueError("Each date must be a month start at midnight.")
    if out["date"].duplicated().any():
        raise ValueError("Duplicate months are not allowed.")
    out = out.sort_values("date").reset_index(drop=True)
    if len(out) < min_rows:
        raise ValueError(f"At least {min_rows} contiguous monthly observations are required.")
    expected = pd.date_range(out["date"].iloc[0], periods=len(out), freq="MS")
    if not np.array_equal(out["date"].values, expected.values):
        raise ValueError("Missing months: supply a complete monthly calendar; targets are not imputed.")
    out["visitor_arrivals"] = pd.to_numeric(out["visitor_arrivals"], errors="raise").astype(float)
    values = out["visitor_arrivals"].to_numpy()
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Arrivals must be finite, nonnegative numbers; missing targets are not imputed.")
    return out


def load_city_raw(city: str, raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    if city not in CITIES:
        raise ValueError(f"Unknown destination: {city}")
    return validate_history(pd.read_csv(Path(raw_dir) / CITIES[city]["file"]))
