"""Expanding-window model selection, followed by a final window held out of selection."""

import math

import numpy as np
import pandas as pd

from .config import CANDIDATES, HORIZON, MIN_HISTORY, VALIDATION_FOLDS
from .forecast import forecast
from .io import validate_history
from .metrics import metrics


def validation_origins(development_rows: int) -> list[int]:
    origins = list(range(development_rows - VALIDATION_FOLDS * HORIZON, development_rows, HORIZON))
    if origins[0] < MIN_HISTORY:
        raise ValueError(
            f"Need at least {MIN_HISTORY + (VALIDATION_FOLDS + 1) * HORIZON} months for the evaluation protocol."
        )
    return origins


def evaluate_window(history: pd.DataFrame, test: pd.DataFrame, candidate: str):
    prediction = forecast(history, candidate, len(test))
    if not np.array_equal(prediction["date"].values, test["date"].values):
        raise ValueError("Evaluation dates must immediately follow the training window.")
    result = prediction.rename(columns={"forecast": "predicted"})
    result["actual"] = test["visitor_arrivals"].to_numpy()
    result["abs_error"] = (result["actual"] - result["predicted"]).abs()
    result["origin"] = history["date"].iloc[-1]
    result["horizon"] = np.arange(1, len(result) + 1)
    score = metrics(result["actual"], result["predicted"], history["visitor_arrivals"])
    score["guardrail_months"] = int(result["guardrail_applied"].sum())
    return result, score


def select_model(development: pd.DataFrame):
    """Receives no final holdout observations. Ties retain candidate order."""
    folds, predictions, scores = [], [], []
    origins = validation_origins(len(development))
    for candidate in CANDIDATES:
        candidate_mae = []
        for end in origins:
            history, test = development.iloc[:end], development.iloc[end : end + HORIZON]
            pred, score = evaluate_window(history, test, candidate)
            predictions.append(pred)
            folds.append(
                {
                    "model": candidate,
                    "origin": history["date"].iloc[-1],
                    "test_start": test["date"].iloc[0],
                    "test_end": test["date"].iloc[-1],
                    "history_rows": len(history),
                    **score,
                }
            )
            candidate_mae.append(score["mae"])
        scores.append(
            {"model": candidate, "validation_mae": float(np.mean(candidate_mae)), "folds": len(origins)}
        )
    selected = min(scores, key=lambda item: item["validation_mae"])["model"]
    return selected, scores, pd.concat(predictions, ignore_index=True), folds


def error_band_radius(errors, coverage: float = 0.8) -> float:
    """Finite-sample order statistic; descriptive only, no coverage guarantee.

    Overlapping horizon errors are dependent and selection uses these same folds.
    This is a historical error reference band, not a calibrated confidence interval.
    """
    values = np.sort(np.asarray(errors, dtype=float))
    if len(values) == 0 or not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Expected nonnegative finite absolute errors.")
    rank = min(len(values), math.ceil((len(values) + 1) * coverage))
    return float(values[rank - 1])


def evaluate_city(frame: pd.DataFrame) -> dict:
    frame = validate_history(frame)
    development, holdout = frame.iloc[:-HORIZON], frame.iloc[-HORIZON:]
    selected, leaderboard, validation, folds = select_model(development)
    holdout_frames, holdout_scores, outlooks = [], [], []
    for candidate in CANDIDATES:
        pred, score = evaluate_window(development, holdout, candidate)
        errors = validation.loc[validation["model"] == candidate, "abs_error"]
        radius = error_band_radius(errors)
        pred["lower"] = (pred["predicted"] - radius).clip(lower=0)
        pred["upper"] = pred["predicted"] + radius
        score["band_coverage_pct"] = float(
            ((pred["actual"] >= pred["lower"]) & (pred["actual"] <= pred["upper"])).mean() * 100
        )
        holdout_scores.append(
            {"model": candidate, "error_band_radius": radius, "band_sample_n": len(errors), **score}
        )
        holdout_frames.append(pred)
        outlook = forecast(frame, candidate)
        outlook["lower"] = (outlook["forecast"] - radius).clip(lower=0)
        outlook["upper"] = outlook["forecast"] + radius
        outlooks.append(outlook)
    return {
        "selected_model": selected,
        "selection_rule": "Lowest mean MAE across six expanding, non-overlapping 12-month validation windows; ties use declared candidate order.",
        "training_start": frame["date"].iloc[0],
        "development_end": development["date"].iloc[-1],
        "data_end": frame["date"].iloc[-1],
        "holdout_start": holdout["date"].iloc[0],
        "history_rows": len(frame),
        "development_rows": len(development),
        "fit_rows_ml_development": len(development) - 12,
        "fit_rows_ml_final": len(frame) - 12,
        "leaderboard": leaderboard,
        "folds": folds,
        "validation": validation.to_dict("records"),
        "holdout_metrics": holdout_scores,
        "holdout": pd.concat(holdout_frames, ignore_index=True).to_dict("records"),
        "outlook": pd.concat(outlooks, ignore_index=True).to_dict("records"),
        "history": frame.to_dict("records"),
    }
