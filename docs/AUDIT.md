# Audit and upgrade record

## Baseline established

The supplied folder contained a small Python/Streamlit application, three 120-row CSVs, nine notebook experiments, nine saved CSV/JSON outputs, a machine-specific virtual environment, and a large duplicate ZIP. There was no Git metadata, test suite, deployment configuration, or data provenance manifest in the supplied application.

The original requirements were installed into a separate Python 3.11 environment. Running `python -m stis.build_artifacts` on a workspace copy succeeded and reproduced **all three original metric JSON files exactly**. Those saved metrics therefore reflect the supplied implementation; they are not merely stale fabricated outputs. The original chart/export/model-card UI was also exercised in Streamlit's AppTest with its `app/` import directory supplied. A bare AppTest invocation fails on the unqualified `components` import, illustrating the original path sensitivity; this does not by itself establish that every normal Streamlit CLI invocation fails.

Original raw data, application source, saved outputs, and notebooks are archived under `legacy/`. Raw data is duplicated unchanged into the new runnable app. The original Downloads folder was not edited.

## Findings and resolutions

| Finding | Consequence | Resolution |
|---|---|---|
| `add_log_feats` rolling means include the current target | Direct target leakage in train/test features | Rolling inputs shifted by one month; mutation regression test |
| COVID rows deleted before `shift` | False adjacency between December 2019 and January 2023 | Preserve continuous calendar; reject missing months |
| Test-year feature matrix contains earlier test-year actuals | One-step-like predictions described alongside a recursive annual outlook | Evaluate complete recursive 12-month paths from a fixed origin |
| Outlook predicts from the last observed feature row | Forecast month's lags/calendar terms misaligned | Append future date before creating features; explicit recursion test |
| Default RidgeCV leave-one-out selection with outer scaling | Temporal validation unsuitable; scaling not independently fit in inner folds | Explicit chronological candidate selection, per-origin pipelines |
| City “best” models hardcoded | No comparable selection evidence in application | Same candidates/folds, documented MAE rule, holdout-independent selection |
| 2024/2025 hardcoded | Wrong dates after a data refresh | Derive origin, holdout, validation, and forecast dates from history |
| Exogenous backward fill; duplicate dates dropped silently | Potential lookahead and masked input problems | Exogenous variables excluded; strict target/date contract |
| Hong Kong duplicate year/month renaming | Duplicate column names | Calendar derived only from date |
| Seasonal-naïve training count includes test rows | Misleading model metadata | Report observed/context/supervised counts explicitly |
| MAPE and R² lack denominator handling | Undefined/infinite metrics for zeros/constants | Explicit nulls and MAPE count; WAPE and MAE emphasized |
| Confidence stars inferred from MAPE | Unsupported uncertainty claim | Remove stars; descriptive error bands and observed coverage with limitations |
| Notebooks use different split periods and transformations | Results cannot be compared as if same task | Preserve as historical experiments; new single protocol |
| Notebook full-series winsorization and contemporaneous exogenous values | Further lookahead risks | Not imported into new pipeline |
| Old dependency pins, no tests, fragile entry path | Harder to maintain or deploy reproducibly | Tested runtime lock, canonical root entry point, tests/CI/container |
| Original “Bangkok / Thailand proxy” wording absent from UI | Potentially misleading geographic claim | Visible proxy label and data qualification |

Corrected recursive validation also exposed extreme Ridge extrapolation. A documented bound derived exclusively from each origin's training history now prevents numerical explosions and exports activation flags. This is a transparent operational heuristic, not an accuracy claim.

## Preserved valid work

The project retains its three-destination tourism forecasting purpose, monthly arrival inputs, log-target ML approach, seasonal baseline, offline artifact approach, and interactive Streamlit charts/downloads. Ridge and random forest remain inspectable alternatives. Seasonal naïve correctly repeats the same calendar month last year. The original saved seasonal-naïve 2024 predictions remain numerically meaningful under that baseline, although its metadata and cross-model comparisons were flawed.

## Evidence boundary

Do not compare the old leaky ML scores with the new annual forecast scores as if this were a controlled model upgrade. The upgrade establishes a more defensible evaluation and maintainable application. Actual accuracy and remaining failures are in `VERIFICATION.md` and the bundle. Upstream data filling, provenance, and dataset reuse limit any generalization claim.
