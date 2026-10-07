# Initial release verification record

**Historical record:** this page describes the 30 September release. For the current seven-model, forecast-only dashboard and executed notebooks, see [7 October revision](UPDATE_2026-10-07.md).

Run on **30 September 2026** using macOS arm64 and Python **3.11.0**. These are observed results, not an assertion that all production environments have been tested.

## Checks completed

| Check | Outcome |
|---|---|
| Original pinned environment + original batch build | Passed; all three saved metric JSON files reproduced exactly |
| Original UI through AppTest with its app import path | No exceptions; Plotly chart element present |
| New runtime lock installed into a separate clean environment | Passed |
| Linux x86_64 Python 3.11 binary dependency resolution, including watchdog | Passed in pip dry-run; not a Linux runtime test |
| `python -m pip check` in clean runtime environment | No broken requirements |
| Full batch build, three destinations × six candidates | Passed |
| Second full build using the clean runtime environment | All city predictions, scores, bands, selections, and fingerprints exactly equal |
| `python -m stis.build_artifacts --check` | Schema and source fingerprints verified |
| `ruff check .` and `ruff format --check .` | Passed |
| `pytest -q` | **45 passed** |
| `pip-audit -r requirements.txt` | No known vulnerabilities among 42 audited dependencies; platform-inapplicable entries may be skipped |
| Running Streamlit health endpoint | HTTP 200, body `ok` |
| Original-file preservation | 37 archived files and three active raw CSVs byte-identical to supplied files |

The dependency audit is a point-in-time advisory check, not a guarantee of security. The numerical packages used in the bundle are NumPy 2.4.6, pandas 2.3.3, and scikit-learn 1.9.1. The UI uses Streamlit 1.64.0 and Plotly 6.9.0. The full runtime closure is in `requirements.txt`; audit output is preserved in `dependency-audit.json`.

## What the regression tests establish

- Modifying current/future target values cannot alter a current feature row.
- January 2023's one-month lag remains December 2022, not December 2019.
- Duplicate/missing months, invalid dates, negative targets, NaN, and infinities are rejected; valid zero-arrival months are retained.
- All six models produce finite, nonnegative forecasts at dates relative to the last observation, without modifying caller data.
- Recursive feature rows use the future month's calendar and the model's own preceding prediction.
- The training-derived operational bound flags extreme predictions; non-finite model outputs fail explicitly.
- Altering the final 12 actuals changes holdout errors but not candidate selection, validation scores, or the fixed-origin holdout predictions.
- MAPE denominators, zero-total WAPE, zero-variance R², and zero-scale MASE behave explicitly.
- Failed artifact serialization preserves the prior file; source changes and malformed bundles are rejected.
- Streamlit loads all three destinations, all six models, horizon and band/baseline controls, and the missing-artifact recovery state without exceptions.

## Measured final-holdout results

All rows below concern **January–December 2024**, forecast from the end of December 2023. Selection used only the six earlier annual windows. Counts are rounded here; `data/bundle.json` and `holdout-results.csv` contain full-precision results for every candidate.

| Destination | Validation-selected model | MAE, arrivals | WAPE | R² | Seasonal-naïve MAE |
|---|---|---:|---:|---:|---:|
| Bangkok / Thailand proxy | Random forest | 220,825 | 7.45% | 0.184 | 616,308 |
| Singapore | Last observation | 156,054 | 11.32% | −15.635 | 243,992 |
| Hong Kong | Random forest | 534,424 | 14.41% | −1.316 | 875,261 |

The selected candidate has lower MAE than seasonal naïve on each of these three holdouts. That does **not** establish a reliable improvement on unseen future years. In particular, random forest has slightly lower 2024 MAE than the selected last-observation model in Singapore, and last observation has lower MAE than the selected random forest in Hong Kong. We keep the validation selections instead of selecting retrospectively on 2024.

All three selected models' historical error reference bands cover all 12 holdout observations. Their large widths reflect pandemic-era validation errors; 100% observed coverage is not a confidence rating or a nominal coverage guarantee. Singapore's unusually negative R² is retained: its final-year actuals have low variation relative to the forecast bias. No baseline/outlook value is silently replaced to make metrics look better.

The original ML figures were produced by a leaky pipeline with a different protocol. They are preserved for audit, not used as evidence of an old-versus-new accuracy gain. The 2024 observations were already present in the original research and audit; see the evidence boundary in `METHODOLOGY.md`.

## Checks not completed here

- **Browser screenshot/visual review:** the native browser automation runtime failed to start. A Playwright launch of installed Chrome also failed because its process/crash-reporting initialization was denied by the environment. Streamlit's application tests passed, but pixel layout, mobile appearance, and actual browser downloads have not been visually verified. No fabricated screenshot is included.
- **Docker build/Compose runtime:** Docker is not installed in this environment. The configuration and Linux CI smoke test are provided, but have not been executed on a Docker host.
- **Remote CI and live deployment:** no Git remote or authenticated hosting target is configured. No public URL is claimed. Connect a GitHub repository to Streamlit Community Cloud, or supply a container-hosting target, as detailed in `DEPLOYMENT.md`.
- **External statistical validity:** original source provenance, upstream Hong Kong imputation, geographic definitions, and fresh post-2024 observations are unavailable. The software's leakage safeguards cannot certify undocumented input preparation or future forecasting skill.
