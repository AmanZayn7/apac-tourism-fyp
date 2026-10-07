"""Metrics in arrival units, with explicit zero-denominator behavior."""

import numpy as np


def metrics(actual, predicted, training) -> dict:
    y, p, train = [np.asarray(v, dtype=float) for v in (actual, predicted, training)]
    if y.ndim != 1 or y.shape != p.shape or len(y) == 0:
        raise ValueError("Actual and predicted must be non-empty, aligned vectors.")
    if not all(np.isfinite(v).all() for v in (y, p, train)):
        raise ValueError("Metrics require finite values.")
    error = np.abs(y - p)
    nonzero = y != 0
    total = float(np.abs(y).sum())
    variation = float(((y - y.mean()) ** 2).sum())
    scale = float(np.mean(np.abs(train[12:] - train[:-12]))) if len(train) > 12 else 0.0
    return {
        "n": len(y),
        "mae": float(error.mean()),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "wape_pct": float(error.sum() / total * 100) if total else None,
        "mape_pct": float(np.mean(error[nonzero] / np.abs(y[nonzero])) * 100) if nonzero.any() else None,
        "mape_n": int(nonzero.sum()),
        "r2": float(1 - np.sum((y - p) ** 2) / variation) if variation else None,
        "mase": float(error.mean() / scale) if scale else None,
    }
