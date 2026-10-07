# Corrected, executed research notebooks

These nine notebooks correspond one-to-one to the originals in `legacy/notebooks/`, which remain unchanged. Each explains its original defects, the corrected forecasting contract, feature-causality assertions, temporal splits, model settings, actual recomputed scores, twelve-month forecasts, limitations, and reconciliation with deployment.

| Corrected notebook | Destination | Focus |
|---|---|---|
| [BANGKOK RIDGE LOG (5)](BANGKOK%20RIDGE%20LOG%20(5).ipynb) | Bangkok / Thailand proxy | Three chronological Ridge candidates |
| [HONG KONG RIDGE LOG (4)](HONG%20KONG%20RIDGE%20LOG%20(4).ipynb) | Hong Kong | Three chronological Ridge candidates |
| [RF BANGKOK (3)](RF%20BANGKOK%20(3).ipynb) | Bangkok / Thailand proxy | RF and XGBoost; replaces invalid YoY formulation |
| [RF SINGAPORE (4)](RF%20SINGAPORE%20(4).ipynb) | Singapore | RF and XGBoost; supplied final CSV explicitly substituted |
| [HK RF (3)](HK%20RF%20(3).ipynb) | Hong Kong | RF and XGBoost; removes target leakage and winsorization |
| [SG RF AND XGB (5)](SG%20RF%20AND%20XGB%20(5).ipynb) | Singapore | RF and XGBoost; removes unavailable external predictors |
| [HK RF AND XGB (4)](HK%20RF%20AND%20XGB%20(4).ipynb) | Hong Kong | RF and XGBoost; fixed-origin recursive evaluation |
| [BKK SN (4)](BKK%20SN%20(4).ipynb) | Bangkok / Thailand proxy | Seasonal naïve on common complete annual windows |
| [HK SN (5)](HK%20SN%20(5).ipynb) | Hong Kong | Seasonal naïve on common complete annual windows |

The notebooks intentionally call the shared `stis` implementation, rather than maintaining nine drifting copies of forecasting code. Every notebook independently recomputes all seven candidates for its destination, then reports its relevant model family and baseline comparisons. A family-specific choice need not equal the overall validation winner shown by default in the dashboard.

## Reproduce

From the project root in the Python 3.11 environment:

```bash
python -m pip install -r requirements-notebooks.txt
python -m stis.build_artifacts
python scripts/build_notebooks.py --execute
```

The generator recreates the corrected notebooks, so preserve any manual research extensions before running it. It never changes the originals. Alternatively, open an individual notebook using the same Python environment and run all cells from the project root or `notebooks/`.

On macOS, XGBoost needs a discoverable OpenMP library; install `libomp` with Homebrew if necessary. See [deployment instructions](../docs/DEPLOYMENT.md). This execution environment used its existing Anaconda OpenMP library via a process-local library path, without changing system files.

The executed outputs are corrected experiments, **not reproductions of the original leaky results**. No accuracy gain is claimed against incomparable old scores. The data ends in December 2024, so the outlook is January–December 2025. Singapore's missing original recovery-index file and unresolved source provenance remain limitations.

The deployment-reconciliation assertions allow small cross-platform tree-model variation: 0.1% for monthly RF/XGBoost forecasts and 1% for their validation MAEs. Baseline and Ridge checks remain strict, and forecast months plus the selected winner must match exactly. This tolerance is for reproducibility checks, not a claim of forecast accuracy.
