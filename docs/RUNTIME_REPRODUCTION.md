# Reproduction and serving environments

The published forecasts and model definitions are unchanged. The numerical reproduction environment for this release is **macOS arm64, Python 3.11**, with the pinned numerical libraries. The website serving environment is Linux. Serving reads the published JSON and does not refit models.

## Measured platform comparison

[Diagnostic run](https://github.com/AmanZayn7/apac-tourism-fyp/actions/runs/37606740838) compared GitHub macOS 14 arm64 (Python 3.11.9) and Ubuntu x86_64 (Python 3.11.16). Both used NumPy 2.4.6, pandas 2.3.3 and scikit-learn 1.9.1. XGBoost 3.2.0 uses the standard macOS distribution and the CPU-only Linux distribution.

All 21 macOS forecasts and all validation MAEs matched the committed bundle within rtol=1e-8. Repeated forecasts were identical within each tested environment. All validation-selected winners matched across environments.

| Destination | Linux RF maximum monthly difference | Linux XGBoost maximum monthly difference | Linux XGBoost validation MAE change |
|---|---:|---:|---:|
| Bangkok / Thailand proxy | 0.05194% | 5.26473% | +37.01369% |
| Singapore | 0.09688% | 0.88753% | +3.79934% |
| Hong Kong | 0.10734% | 5.76708% | +0.49415% |

Baseline and Ridge forecast differences were numerically negligible. Some computed input features differ at the last binary digits across platforms. These observations establish platform-dependent numerical results; they do not isolate a single cause among numerical libraries, architecture, native binaries and algorithm implementations. Do not describe the larger XGBoost differences as harmless display rounding or widen tolerances to hide them.

Full per-model forecasts, validation scores and repeatability indicators are in [runtime-reproduction.json](runtime-reproduction.json). The manual diagnostic workflow can be rerun after numerical dependencies change.

## Release checks

- Linux: install/consistency, lint/formatting, artifact freshness, tests, dependency audit, build the actual Compose configuration, health check, and exercise all 21 city/model combinations inside its non-root read-only container.
- macOS arm64: independently execute all nine corrected notebooks against the unchanged published bundle. Every forecast and validation MAE uses rtol=1e-8; dates and selected model must match.
- Executed notebooks are retained as a GitHub Actions artifact.

This arrangement validates what the website actually does while preserving the project's recorded experiment. It does **not** claim Linux retraining reproduces the release. To adopt Linux as the training environment in a future release, explicitly version a new bundle, notebook outputs and results; do not silently replace this release's evidence.
