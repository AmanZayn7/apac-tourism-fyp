# Forecasting methodology

## The question

At the end of a given observed month, forecast the next 12 monthly arrival counts using only information available up to that origin. This project is an arrival-demand explorer, not a travel recommendation engine. Every candidate answers the same question with the same evaluation dates.

## Inputs and features

The input contract is a continuous monthly calendar of nonnegative, finite arrivals. Dates must be unique month starts. Input may be unsorted; sorting is explicit. Missing months, duplicate dates, missing targets, infinities, and negative targets fail validation. Zero arrivals are valid and are retained.

Pandemic months remain in the calendar and training data. Deleting them before shifting would turn a one-row lag into a multi-year jump. The full-history design also exposes shock/recovery failures instead of hiding them. It does not assert that a stationary model can predict border closures.

For target month t, ML features are `log1p(y[t-1])`, `log1p(y[t-3])`, `log1p(y[t-6])`, `log1p(y[t-12])`, three- and six-month means of **previous** log1p arrivals, plus sine/cosine of t's month. All eight feature definitions are shared by fit and inference. The first 12 training rows provide context and are excluded from supervised fitting.

The model predicts log1p arrivals, inverted with expm1. No smearing correction is applied: this is a point forecast and not a guaranteed unbiased conditional mean. Observed hotel occupancy and Google Trends are retained in the original files but excluded because future availability, release delays, and source filling are unverified. Their values are never forward/back-filled by the new pipeline.

## Predeclared candidate set

| Candidate | Definition |
|---|---|
| Seasonal naïve | Repeat the last 12 observations by calendar month |
| Last observation | Repeat the latest known arrival count |
| Ridge α = 1, 10, 100 | StandardScaler fitted within each origin's training data, then Ridge on log1p targets |
| Random forest | 200 trees; min_samples_leaf=3; max_depth=8; seed=42; n_jobs=1; log1p targets |
| XGBoost | 200 trees; max_depth=3; learning_rate=0.05; min_child_weight=2; subsample=0.9; colsample_bytree=0.9; reg_lambda=1; squared-error objective; hist tree method; seed=42; n_jobs=1; log1p targets |

No randomized split or RidgeCV is used. Ridge regularization and the final candidate are chosen by the same chronological, multi-step validation protocol. The pipeline scaler is refitted independently at each origin. Random forest uses a fixed, modest configuration, not a test-year hyperparameter search.

ML forecasts are recursive: append a future row dated t, build features using the known history, predict t, append that prediction, and continue. No actual observation from within that 12-month test window is fed back into the path.

### Explicit operational bound

Recursive Ridge produced extreme extrapolation in the initial corrected validation runs, particularly across shutdown/reopening transitions. Every recursive ML prediction is now constrained in log space to **0 through twice the maximum observed target in that origin's training history**. The bound is computed once per fit, never from validation/test targets, and never moves in response to generated forecasts. A non-finite model output still fails explicitly.

This is a heuristic to limit numerical instability, not a physical population constraint or a confidence statement. It may suppress real growth. Forecast and validation exports retain `guardrail_applied` and `training_upper_bound`; score records include `guardrail_months`. The dashboard warns when the displayed outlook activates the bound. The bound was fixed after inspecting validation instability, not optimized against holdout accuracy.

## Exact temporal protocol

For the supplied 120 months:

| Stage | Latest training month | Forecast/evaluation window | History rows |
|---|---|---|---:|
| Validation 1 | Dec 2017 | Jan–Dec 2018 | 36 |
| Validation 2 | Dec 2018 | Jan–Dec 2019 | 48 |
| Validation 3 | Dec 2019 | Jan–Dec 2020 | 60 |
| Validation 4 | Dec 2020 | Jan–Dec 2021 | 72 |
| Validation 5 | Dec 2021 | Jan–Dec 2022 | 84 |
| Validation 6 | Dec 2022 | Jan–Dec 2023 | 96 |
| Final holdout | Dec 2023 | Jan–Dec 2024 | 108 |
| Refit outlook | Dec 2024 | Jan–Dec 2025 | 120 |

Select the smallest mean validation MAE across the six equally sized annual windows. All candidates receive identical dates. Ties use candidate declaration order, beginning with seasonal naïve. The final holdout is not passed to the selection function. All candidates are reported on the holdout; the selection does **not** change to the best holdout model. Refit all candidates on the complete history for exploration, retaining the pre-holdout selection as the default.

Dates are relative to the last observation, not hardcoded to 2024/2025. The last 12 months are always the holdout and the six preceding annual windows are validation; at least 120 continuous months are required. New data therefore changes the split. Version inputs and interpret successive releases as different experiments.

The 2024 data was already used in the original research notebooks and was inspected during the audit. It is a *protocol holdout excluded from the new selector*, not newly collected independent evidence. Assessing generalization beyond this historical dataset requires fresh observations. No claim of a pristine, never-before-seen scientific test set is made.

## Metrics and interpretation

- **MAE:** mean absolute arrival error; primary selection metric. Comparable across candidates within one destination, not across destination scales.
- **RMSE:** square root of mean squared arrival error; emphasizes larger misses.
- **WAPE:** 100 × total absolute error / total absolute actual arrivals. Null if the actual total is zero. Does not require excluding individual zero months.
- **MAPE:** mean absolute percentage error across nonzero actuals only. `mape_n` reports the denominator count. It can explode for tiny pandemic arrivals and is not used for selection.
- **Seasonal MASE:** MAE divided by mean |y[t]−y[t−12]| calculated on that origin's training series. Null for zero scale. A value below 1 is relative to that training scale, not proof of beating the seasonal baseline on the holdout.
- **R²:** 1 − SSE/SST, null for constant actuals. Negative values are preserved. A nearly constant holdout can yield very negative R² even with a moderate percentage error.

Metrics use full-precision predictions. Only visual display rounds counts. No confidence stars are inferred from MAPE, and no old/new metric comparison is framed as a measured accuracy improvement: the old pipeline used leaked features and a different evaluation protocol.

## Historical error reference bands

Pool a model's 72 absolute validation errors. Sort them and choose order statistic min(n, ceil((n+1)×0.8)), which is the 59th value for n=72. Display prediction ± this constant radius, clipping the lower limit at zero. Use only pre-holdout validation errors for both holdout bands and final outlook bands. Report the actual fraction of holdout months inside the band.

These are **descriptive historical error bands**, not calibrated prediction/confidence intervals. Errors are dependent; the same validation data selects the model; major regime changes invalidate exchangeability; and uncertainty is not separately estimated for each horizon. Wide pandemic-driven bands can have 100% holdout coverage while being uninformative. Do not sum monthly bounds into an annual interval. A probabilistic replacement requires more forecast origins, proper calibration separation, and coverage diagnostics on fresh data.

## Reference documentation

The design follows the information-availability principle in [scikit-learn's leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html) and chronological splitting rationale in [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html). The implementation uses explicit annual origins to evaluate recursive multi-step paths; it does not claim that a generic tabular cross-validation score is a 12-month forecast score.

## Display integrity

The dashboard always shows all twelve forecast months immediately after the data cutoff, without historical observations or auto-generated extra date ticks. Each monthly point is rounded once to an integer. The total is the exact sum of these twelve displayed points; average is that sum divided by twelve (rounded only on the card); high and low use the same points, with ties disclosed. CSV exports retain both full-precision outputs and displayed integers. Evaluation metrics continue to use full precision.

Corrected notebooks in `notebooks/` independently recompute the shared pipeline and assert agreement with deployment; original notebooks remain in `legacy/`. Family comparisons and the overall deployment choice are explicitly distinguished.
