"""One forecasting path for validation, holdout evaluation, and final outlooks."""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .config import CANDIDATES, MIN_HISTORY, RANDOM_STATE
from .features import make_features
from .io import validate_history


def make_estimator(candidate: str):
    if candidate == "xgb":
        # Lazy import keeps read-only serving independent of native training libraries.
        from xgboost import XGBRegressor

        return XGBRegressor(
            n_estimators=200,
            max_depth=3,
            learning_rate=0.05,
            min_child_weight=2,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.0,
            objective="reg:squarederror",
            tree_method="hist",
            n_jobs=1,
            random_state=RANDOM_STATE,
        )
    if candidate.startswith("ridge_") and candidate in CANDIDATES:
        return make_pipeline(StandardScaler(), Ridge(alpha=float(candidate.split("_")[1])))
    if candidate == "rf":
        return RandomForestRegressor(
            n_estimators=200,
            min_samples_leaf=3,
            max_depth=8,
            n_jobs=1,
            random_state=RANDOM_STATE,
        )
    raise ValueError(f"No fitted estimator for candidate: {candidate}")


def forecast(history: pd.DataFrame, candidate: str, horizon: int = 12) -> pd.DataFrame:
    if candidate not in CANDIDATES:
        raise ValueError(f"Unknown candidate: {candidate}")
    if isinstance(horizon, bool) or not isinstance(horizon, int) or not 1 <= horizon <= 12:
        raise ValueError("Horizon must be an integer between 1 and 12 months.")
    work = validate_history(history, min_rows=MIN_HISTORY)
    # A predeclared operational bound, derived only from this origin's history.
    # It limits recursive extrapolation under regime changes, not statistical uncertainty.
    upper_limit = 2.0 * float(work["visitor_arrivals"].max())
    clipped = [False] * horizon
    dates = pd.date_range(work["date"].iloc[-1] + pd.offsets.MonthBegin(), periods=horizon, freq="MS")
    if candidate == "snaive":
        values = work["visitor_arrivals"].iloc[-12:].to_numpy()[:horizon]
    elif candidate == "naive":
        values = np.repeat(work["visitor_arrivals"].iloc[-1], horizon)
    else:
        features = make_features(work)
        valid = features.notna().all(axis=1)
        estimator = make_estimator(candidate)
        estimator.fit(features.loc[valid], np.log1p(work.loc[valid, "visitor_arrivals"]))
        values = []
        for step, date in enumerate(dates):
            # Construct t before prediction, so lags and month features belong to t.
            work.loc[len(work), "date"] = date
            row = make_features(work).iloc[[-1]]
            log_prediction = float(estimator.predict(row)[0])
            if not np.isfinite(log_prediction):
                raise ValueError(f"Non-finite log forecast from {candidate} at {date}.")
            bounded_log = float(np.clip(log_prediction, 0.0, np.log1p(upper_limit)))
            clipped[step] = bounded_log != log_prediction
            value = float(np.expm1(bounded_log))
            if not np.isfinite(value):
                raise ValueError(f"Non-finite forecast from {candidate} at {date}.")
            values.append(value)
            work.loc[work.index[-1], "visitor_arrivals"] = value
    return pd.DataFrame(
        {
            "date": dates,
            "forecast": values,
            "model": candidate,
            "guardrail_applied": clipped,
            "training_upper_bound": upper_limit,
        }
    )
