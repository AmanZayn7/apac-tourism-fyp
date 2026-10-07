# First remote verification — 7 October 2026

[GitHub Actions run](https://github.com/AmanZayn7/apac-tourism-fyp/actions/runs/37604162561), initial commit on `main`, Ubuntu runner with Python 3.11.16.

Passed: runtime/development dependency installation, pip consistency check, Ruff lint and formatting, committed artifact freshness, and the supplied pytest suite.

Failed: execution of corrected notebooks against the published macOS-generated bundle. The forecast comparison failed at `rtol=0.001` with all twelve months outside tolerance and maximum relative difference 0.05264733 (approximately 5.26%). This is materially larger than the previously documented small cross-platform illustration. The available failure excerpt does not identify the loop's current candidate, so no specific model or root cause is asserted here.

The runtime advisory audit and Docker build/smoke test were skipped after this failure. Earlier local audit results do not substitute for the skipped remote steps.

Models, saved forecasts, model selections and comparison tolerances remain unchanged. Investigate per-candidate results, runtime/build differences and repeatability before choosing a canonical build environment or changing reconciliation policy. Do not conceal the difference by simply increasing tolerances. A live deployment may serve the saved bundle without training, but full numerical reproduction across environments is not yet established.

## Superseding successful release check

[Run 37607133619](https://github.com/AmanZayn7/apac-tourism-fyp/actions/runs/37607133619) passed both jobs on 7 October 2026 after separating supported release reproduction from deployment serving:

- macOS arm64 executed all nine notebooks against the unchanged saved bundle with rtol=1e-8 for all model forecasts and validation MAEs. The executed notebooks were downloaded from the successful run into the repository.
- Linux passed dependency consistency, lint, formatting, artifact freshness, the supplied tests, runtime dependency audit, Docker Compose build/start/health and all 21 city/model combinations inside the non-root read-only container.
- Protobuf 5.29.6 is used to respect Community Cloud's currently documented below-6 range. No model definitions, raw inputs or numerical bundle outputs were changed.

The earlier Linux retraining discrepancy remains a documented limitation, not a claim of cross-platform model equivalence. Later source-attribution/UI edits trigger the same checks again.
