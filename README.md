# APAC Travel Observatory

**Live demo:** [APAC Tourism](https://apac-tourism.streamlit.app/)

**A reproducible tourism forecasting portfolio project by Abdul Muhaimin Aman.**

Explore monthly visitor arrivals for Singapore, Hong Kong, and a Bangkok-labelled Thailand proxy. Compare seven forecasting candidates, inspect chronological validation and final holdout results, and export forecasts with their assumptions attached.

**7 October revision:** the main dashboard now shows exactly twelve predicted months, with matching integer arrival values in cards, charts and exports. A jade, coral, indigo and gold theme combines original city skyline artwork with clearer controls. All nine notebooks have corrected, executed counterparts in [notebooks](notebooks/README.md), alongside the unchanged originals and the [original-code audit](docs/NOTEBOOK_AUDIT.md). XGBoost now participates in the same deployment and validation protocol. See the [latest verification](docs/UPDATE_2026-10-07.md).

The supplied observations cover January 2015–December 2024. The included outlook is **January–December 2025**, generated from that historical snapshot. It is not a live 2026 forecast. The owner-confirmed arrivals sources are recorded in [data notes](docs/DATA.md). The Thailand source covers national arrivals rather than Bangkok alone; The owner confirmed that Singapore arrival values were preprocessed; all 120 supplied values differ from the current official Total series. Exact preprocessing steps and public redistribution terms remain to be documented; results describe the supplied preprocessed research dataset.

## Run locally

Use **Python 3.11** from the project directory. The exact runtime dependency set is pinned in `requirements.txt`.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m stis.build_artifacts --check
python -m streamlit run streamlit_app.py
```

Open http://localhost:8501. On Windows, activate with `.venv\Scripts\activate` instead. The precomputed JSON bundle is included, so startup does not train models. Run commands from the repository root; no absolute personal paths are required. A missing or stale bundle produces a recovery message in the app.

On macOS, install OpenMP (`brew install libomp`) before training XGBoost if it is not already available. See [deployment notes](docs/DEPLOYMENT.md).

To reproduce all results or refresh artifacts after changing data or forecasting code:

```bash
python -m stis.build_artifacts
python -m stis.build_artifacts --check
```

All destinations are completed in memory before one JSON file is atomically published. Invalid input or a failed build leaves the previous file intact. Source fingerprints prevent the app from serving a bundle built with different input data or backend code.

## What the project demonstrates

- One calendar-preserving feature builder for evaluation and inference, with lagged and shifted rolling log1p arrivals.
- Six expanding annual validation windows and a final year excluded from model selection; complete 12-month recursive forecasts at every origin.
- Seasonal naïve and last-observation baselines, scaled Ridge candidates, a reproducible random forest, and XGBoost.
- Arrival-unit MAE/RMSE, WAPE, zero-aware MAPE, seasonal MASE, negative R² when warranted, and observed historical-band coverage.
- A read-only Streamlit interface with model comparisons, provenance, forecast dates, data limitations, and CSV downloads.
- Tests for leakage, temporal alignment, recursion, zero targets, artifact freshness, and every destination/model control; locked dependencies, CI, and container configuration.

**Accuracy is evidence, not a product claim.** The validation-selected models do not uniformly win on the final holdout. Historical error bands are wide and are not calibrated confidence intervals. The original project's leaky scores are archived, not presented as comparable performance gains.

## Verification

```bash
python -m pip install -r requirements-dev.txt
python -m pip check
ruff check .
ruff format --check .
pytest -q
pip-audit -r requirements.txt
```

See [latest verification](docs/UPDATE_2026-10-07.md) and the [initial release record](docs/VERIFICATION.md) for actual run records and [audit](docs/AUDIT.md) for original defects and what was preserved. Dependency audit results are time-sensitive; rerun them before release.

## Deploy

For a container-capable host:

```bash
docker compose up --build -d
curl --fail http://localhost:8501/_stcore/health
```

For Streamlit Community Cloud, push this directory as a repository and choose `streamlit_app.py`, Python 3.11. The committed bundle and `requirements.txt` are sufficient. Full steps, security defaults, update procedure, and the remaining live-deployment action are in [deployment instructions](docs/DEPLOYMENT.md).

## Project map

```text
streamlit_app.py        Dashboard entry point
app/                   Forecast-only charts, reconciled KPI calculations, and theme
notebooks/             Nine corrected notebooks with executed outputs
stis/                  Input contracts, features, models, evaluation, artifacts, CLI
raw/                   Original supplied CSVs, preserved byte-for-byte
data/bundle.json       Reproducible forecasts, errors, selection record, source hashes
tests/                 Statistical, data, artifact, and UI regression checks
docs/                  Method, provenance, audit, deployment, verification
legacy/                Original application, saved results, and nine notebooks
.github/workflows/     CI checks plus Linux container smoke test
```

See [methodology](docs/METHODOLOGY.md) for exact folds and model settings and [architecture](docs/ARCHITECTURE.md) for the build/serve boundary. The archived virtual environment and 240 MB duplicate ZIP were deliberately excluded; the original Downloads folder remains unchanged.

## Portfolio demonstration

This public project demonstrates historical tourism forecasting and model comparison using supplied preprocessed research data. Forecasts cover January–December 2025; it is not a live tourism feed. Full preparation records are not available, and source links identify the reported publishers rather than certify every prepared value. Models and their mixed results are retained for educational comparison.

## Source references and release status

The project owner confirmed arrivals references from [SingStat](https://tablebuilder.singstat.gov.sg/table/TS/M550241), [Hong Kong Tourism Board](https://www.discoverhongkong.com/eng/hktb/newsroom/tourism-statistics.html), and [Bank of Thailand report 875](https://app.bot.or.th/BTWS_STAT/statistics/ReportPage.aspx?reportID=875&language=eng). These identify the reported sources; they do not certify the preparation of the supplied CSVs. See [data provenance and reuse notes](docs/DATA.md).

The initial Linux notebook reproduction failure is documented in [remote verification](docs/REMOTE_VERIFICATION_2026-10-07.md). A subsequent platform comparison reproduced the saved forecasts on macOS arm64 and measured materially different Linux tree-model retraining results. CI checks release reproduction on macOS arm64 and tests serving the unchanged bundle in Linux Docker Compose; see [reproduction environments](docs/RUNTIME_REPRODUCTION.md).
