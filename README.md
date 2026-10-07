# APAC Travel Observatory

## Comparative Tourism Forecasting Across Three APAC Markets

**An analytical research and deployment portfolio by Abdul Muhaimin Aman**

[Explore the live dashboard](https://apac-tourism.streamlit.app/) · [Forecasting methodology](docs/METHODOLOGY.md) · [Full evaluation results](docs/holdout-results.csv) · [Data documentation](docs/DATA.md)

## Executive Summary

APAC Travel Observatory evaluates how statistical baselines and machine learning models forecast monthly visitor arrivals across Singapore, Hong Kong, and a Bangkok-labelled Thailand proxy. The project combines chronological model evaluation, a shared forecasting pipeline, and an interactive Streamlit dashboard that makes the results accessible for comparison and review.

The analysis uses **120 monthly observations per series, covering January 2015–December 2024**. Seven model candidates are evaluated on six expanding annual validation windows, followed by a separate 2024 reporting holdout. The published outlook covers **January–December 2025**, generated after refitting on the complete supplied history.

The principal finding is that **forecasting performance varies by market and evaluation period**. Tree models outperform both simple baselines on the Thailand proxy's 2024 holdout. For Singapore and Hong Kong, the results demonstrate the continuing value of simple benchmarks and the limits of selecting models from earlier periods. The dashboard retains these differences so that users can examine the evidence behind each forecast.

This is a historical research demonstration using supplied, partly preprocessed datasets. It is not a live tourism feed. Findings describe the datasets and evaluation protocol documented in this repository.

## 1. Analytical Objective

The project addresses the following question:

> Given the monthly arrivals available at a forecast origin, how effectively can different models predict the next twelve months without access to intervening observations?

The analysis has four objectives:

1. **Establish credible benchmarks:** compare machine learning against seasonal-naïve and last-observation forecasts.
2. **Evaluate performance through time:** use chronological, multi-step validation spanning pre-pandemic, disruption, and recovery periods.
3. **Make model selection transparent:** retain the validation-selected model while reporting every candidate's subsequent holdout performance.
4. **Deliver usable analytical outputs:** provide comparable forecast charts, reconciled summary measures, and downloadable monthly estimates.

The practical contribution is a reproducible framework for comparing forecast behaviour under a common information set. Results support research and portfolio discussion; they do not establish that a single model is suitable for every tourism market or future disruption.

## 2. Data Scope and Sources

| Research series | Supplied file | Coverage | Reported arrivals source |
|---|---|---|---|
| Bangkok / Thailand proxy | `raw/bangkok_2015_2024_final.csv` | 120 months, 2015–2024 | [Bank of Thailand — Tourism Indicators, report 875](https://app.bot.or.th/BTWS_STAT/statistics/ReportPage.aspx?reportID=875&language=eng) |
| Singapore | `raw/singapore_2015_2024_final.csv` | 120 months, 2015–2024 | [SingStat — table M550241](https://tablebuilder.singstat.gov.sg/table/TS/M550241), supplied by Singapore Tourism Board |
| Hong Kong | `raw/hongkong_2015_2024_final_filled.csv` | 120 months, 2015–2024 | [Hong Kong Tourism Board — Tourism Statistics](https://www.discoverhongkong.com/eng/hktb/newsroom/tourism-statistics.html) |

The active pipeline uses **date and visitor arrivals**. It derives calendar features from the date. Hotel occupancy and Google Trends columns remain in the supplied files but are excluded from forecasting because their availability at each forecast origin has not been established.

Data interpretation requires three distinctions:

- **Geographic scope:** the cited Thailand arrivals series is national. The Bangkok label is retained as a research proxy, not a claim of city-only arrivals.
- **Preparation history:** the owner confirmed preprocessing of Singapore arrival values; the exact steps are not available. Hong Kong's supplied file is labelled as filled, but its filling procedure is undocumented.
- **Source attribution:** the links identify the owner-reported publishers. They do not certify that the prepared CSVs reproduce the original series without alteration. A comparison against the current SingStat Total series found differences in all 120 supplied months.

The `raw/` directory contains the **as-supplied inputs**, not a guarantee of unprocessed publisher downloads. Source reconciliation, units, and reuse terms are detailed in [Data Documentation](docs/DATA.md). The Singapore source's [Open Data Licence](https://data.gov.sg/open-data-licence) and other publishers' terms should be considered separately from the project's code.

## 3. Forecasting Methodology

### Feature construction and inference

A shared feature builder serves both evaluation and future forecasting. For each target month, the fitted models use:

| Feature group | Definition |
|---|---|
| Lagged arrivals | Log-transformed arrivals at lags 1, 3, 6, and 12 months |
| Recent level | Three- and six-month rolling means of prior log-transformed arrivals |
| Annual seasonality | Sine and cosine of the target month's calendar month |

The target transformation is `log1p(arrivals)`, with forecasts returned through `expm1`. Rolling features are shifted before calculation, so they exclude the current target. Pandemic months remain in the calendar, preserving the meaning of monthly lags.

Fitted models generate the twelve-month path recursively: each prediction becomes an input for later forecast months. Actual observations from within the forecast window are not fed back into the model. Recursive machine learning predictions are bounded between zero and twice the maximum observed value in the corresponding training history; affected months are flagged. This bound is a numerical safeguard, not a statistical confidence limit.

### Model candidates

Seven candidates represent five model families:

| Model family | Candidates | Main specification | Analytical role |
|---|---:|---|---|
| Seasonal naïve | 1 | Repeat the latest twelve observed months | Seasonal benchmark |
| Last observation | 1 | Repeat the latest observed value | Level benchmark |
| Ridge regression | 3 | Training-window standardisation; α = 1, 10, or 100 | Regularised linear alternatives |
| Random forest | 1 | 200 trees; maximum depth 8; minimum leaf size 3 | Nonlinear ensemble |
| XGBoost | 1 | 200 trees; maximum depth 3; learning rate 0.05 | Boosted nonlinear alternative |

The tree models use a fixed seed of 42 and one worker. Full parameters are defined in [`stis/forecast.py`](stis/forecast.py).

### Temporal evaluation design

| Stage | Training information | Forecast window | Purpose |
|---|---|---|---|
| Six expanding validation folds | Each fold uses only observations before its forecast year | Full years 2018–2023 | Select the lowest mean validation MAE |
| Final reporting holdout | January 2015–December 2023 | January–December 2024 | Evaluate all candidates after selection |
| Published outlook | January 2015–December 2024 | January–December 2025 | Produce the dashboard's twelve-month forecasts |

Every candidate receives the same forecast dates and horizon. The selected model is not changed to whichever candidate later scores best on the holdout. The 2024 observations were already available in earlier project work, so this is a holdout excluded from the current selector—not a newly collected blind test.

### Evaluation measures

**MAE** is the primary selection measure. **RMSE** captures larger errors, while **WAPE** expresses total absolute error relative to total observed arrivals. **R²**, seasonal **MASE**, and zero-aware **MAPE** provide additional diagnostics.

WAPE is an error percentage, not an accuracy percentage. Negative R² values are retained and indicate worse squared error than the reporting period's mean. Raw arrival-unit errors should be compared within each series rather than treated as a ranking of differently sized markets.

See [Methodology](docs/METHODOLOGY.md) for the exact folds, metric definitions, zero-denominator handling, and error-band construction.

## 4. Results and Interpretation

### Validation-selected models: 2024 holdout

The following values come from the committed release bundle. MAE and RMSE are rounded to whole arrivals in the supplied target scale; the downloadable evidence retains full precision.

| Research series | Validation-selected model | MAE | RMSE | WAPE | R² |
|---|---|---:|---:|---:|---:|
| Bangkok / Thailand proxy | Random forest | 220,825 | 277,195 | 7.45% | 0.184 |
| Singapore | Last observation | 156,054 | 160,967 | 11.32% | −15.635 |
| Hong Kong | Random forest | 534,424 | 652,345 | 14.41% | −1.316 |

### All-candidate comparison: 2024 holdout WAPE

Lower values indicate less total absolute error relative to observed volume. Bold identifies the lowest holdout WAPE within each series; it does not change the validation-selected defaults above.

| Candidate | Thailand proxy | Singapore | Hong Kong |
|---|---:|---:|---:|
| Seasonal naïve | 20.81% | 17.70% | 23.60% |
| Last observation | 12.67% | 11.32% | **10.83%** |
| Ridge, α = 1 | 76.11% | 51.77% | 33.90% |
| Ridge, α = 10 | 74.52% | 51.43% | 42.19% |
| Ridge, α = 100 | 73.70% | 52.96% | 61.66% |
| Random forest | 7.45% | **10.98%** | 14.41% |
| XGBoost | **7.00%** | 11.43% | 29.34% |

### Analyst's interpretation

**Thailand proxy.** Random forest and XGBoost outperform both baselines on the reporting holdout. XGBoost records the lowest holdout error, while random forest remains the deployed default because it had lower mean validation MAE.

**Singapore.** Last observation wins the earlier validation comparison. Random forest achieves a slightly lower holdout WAPE, but all candidates have negative holdout R². The selected baseline's flat twelve-month outlook is an intentional consequence of repeating the latest observed level. Results apply to the supplied preprocessed target series.

**Hong Kong.** Random forest is the validation choice, but last observation performs better on the holdout. This illustrates that success across earlier windows does not guarantee the best result in a later period. The result should be interpreted alongside the uncertain upstream filling process.

**Across models.** Ridge variants perform poorly on this holdout under the chosen log-level, recursive specification. That finding concerns this setup and these data; it does not establish that regularised regression is generally unsuitable for tourism forecasting. The broader evidence supports retaining simple benchmarks and reviewing performance across regimes rather than assuming greater model complexity ensures better forecasts.

Complete scores are available in [`docs/holdout-results.csv`](docs/holdout-results.csv) and [`data/bundle.json`](data/bundle.json).

## 5. Dashboard and Analytical Outputs

The [live Streamlit application](https://apac-tourism.streamlit.app/) provides:

- Three destination controls and seven forecast candidates.
- Exactly twelve predicted months for the selected model.
- Total, average, highest, and lowest monthly estimates calculated from the same displayed values.
- Comparisons of up to three models on a common forecast window.
- Optional historical error reference bands and validation/holdout evidence.
- CSV forecast downloads and a downloadable evidence bundle.

Monthly forecasts are rounded once for display. KPI totals, chart points, and exported `forecast_arrivals` values reconcile to those rounded estimates; the CSV also retains full-precision forecasts. The error bands summarise past validation errors and are **not calibrated prediction intervals**.

## 6. System Design and Repository Structure

The project separates batch model computation from website serving:

```text
Supplied monthly CSVs
        ↓
Input validation → shared features → candidate models
        ↓
Chronological evaluation and model selection
        ↓
Final refit → atomic publication of data/bundle.json
        ↓
Artifact validation → Streamlit dashboard → charts and downloads
```

The website reads the committed JSON bundle and does not train models at startup. Source fingerprints detect changes to the input files or forecasting code. Artifact publication is atomic, so a failed build preserves the previous bundle.

```text
apac-tourism-fyp/
├── streamlit_app.py             Dashboard entry point
├── app/                        Charts, KPI calculations, artwork and styling
├── stis/
│   ├── config.py               Destinations, candidates and evaluation constants
│   ├── io.py                   Monthly input validation and loading
│   ├── features.py             Shared past-only feature construction
│   ├── forecast.py             Model definitions and recursive inference
│   ├── metrics.py              Evaluation measures
│   ├── evaluate.py             Validation, selection and holdout evaluation
│   ├── artifacts.py            Bundle validation and atomic writing
│   └── build_artifacts.py      Batch build/check command
├── raw/                        Three as-supplied research datasets
├── data/bundle.json            Published forecasts, metrics and fingerprints
├── notebooks/                  Nine corrected, executed research notebooks
├── legacy/                     Archived original code, notebooks and results
├── scripts/                    Notebook generation, audit and runtime diagnostics
├── tests/                      Data, forecasting, artifact and dashboard checks
├── docs/                       Method, sources, results and verification evidence
├── .github/workflows/          CI and platform-reproduction diagnostics
├── .streamlit/config.toml      Dashboard configuration
├── .devcontainer/              Development-container configuration
├── Dockerfile                  Linux serving image
├── compose.yaml                Container runtime configuration
├── pyproject.toml              Project, lint and test configuration
├── requirements.in             Direct dependency specifications
├── requirements.txt            Pinned runtime dependencies
├── requirements-dev.txt        Testing, linting and dependency-audit tools
├── requirements-notebooks.txt  Notebook execution dependencies
└── packages.txt                Community Cloud system dependency
```

**Technology stack:** Python 3.11, pandas, NumPy, scikit-learn, XGBoost, Streamlit, Plotly, pytest, Ruff, Docker, and GitHub Actions.

## 7. Run and Reproduce

### Run the dashboard locally

From the repository root, using Python 3.11:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m stis.build_artifacts --check
python -m streamlit run streamlit_app.py
```

Open [localhost:8501](http://localhost:8501). On Windows, activate the environment with `.venv\Scripts\activate` instead. The included bundle is sufficient to serve the dashboard.

### Rebuild the analytical results

```bash
python -m stis.build_artifacts
python -m stis.build_artifacts --check
```

The supported reproduction environment for the **published numerical results** is macOS arm64 with Python 3.11 and the pinned numerical libraries. Install OpenMP with `brew install libomp` before XGBoost training if needed.

Measured Linux retraining produces different tree-model results, even though within-environment reruns are repeatable and the selected winners remain the same. Linux serving uses the unchanged published bundle and is tested independently. See [Runtime Reproduction](docs/RUNTIME_REPRODUCTION.md) before rebuilding or comparing outputs across platforms.

To generate and execute the corrected notebooks in the reproduction environment:

```bash
python -m pip install -r requirements-notebooks.txt
python scripts/build_notebooks.py --execute
```

### Run verification

```bash
python -m pip install -r requirements-dev.txt
python -m pip check
ruff check .
ruff format --check .
pytest -q
pip-audit -r requirements.txt
```

The recorded suite contains **72 passing tests**, covering temporal alignment, feature causality, recursive inference, zero targets, stale artifacts, dashboard controls, and forecast/KPI reconciliation. CI also executes all nine notebooks on macOS arm64 and exercises all 21 destination/model combinations inside the Linux serving container.

[Remote verification](docs/REMOTE_VERIFICATION_2026-10-07.md) and [live browser verification](docs/LIVE_VERIFICATION_2026-10-07.md) record the checks performed. These are dated evidence, not a guarantee of future uptime or unchanged dependency security.

## 8. Deployment

The public application is hosted on **Streamlit Community Cloud** at [apac-tourism.streamlit.app](https://apac-tourism.streamlit.app/).

| Deployment setting | Value |
|---|---|
| Repository | `AmanZayn7/apac-tourism-fyp` |
| Branch | `main` |
| Entrypoint | `streamlit_app.py` |
| Python version | `3.11` |
| Application secrets | None required |

For a local container deployment:

```bash
docker compose up --build -d
curl --fail http://localhost:8501/_stcore/health
```

Compose binds the service to local port 8501 and runs with a read-only filesystem, temporary writable mounts, and reduced privileges. Public container hosting requires an appropriate ingress configuration. See [Deployment Guide](docs/DEPLOYMENT.md) for updates and troubleshooting.

## 9. Limitations and Further Work

The principal analytical limitations are the incomplete preprocessing record, the national scope of the Thailand proxy, the previously inspected 2024 holdout, and the difficulty of extrapolating across pandemic-related regime changes. Log inversion is not an unbiased conditional-mean estimate, recursive errors can accumulate, and the operational bound may suppress genuine growth. Historical error-band coverage should not be interpreted as guaranteed future coverage.

Priorities for a future research release are to document the full preparation pipeline, reconcile publisher series and units, evaluate on fresh observations, and assess horizon-specific performance and calibrated uncertainty. Updating observations should produce a newly versioned experiment with refreshed results and a clearly stated forecast origin.

## Author

**Abdul Muhaimin Aman**

Final Year Project and analytical portfolio.

The project combines time-series feature engineering, comparative model evaluation, reproducibility controls, and deployment into an accessible research dashboard.
