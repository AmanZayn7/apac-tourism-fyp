# Deployment guide

## Local launch, verified

From the project root, create a Python 3.11 virtual environment, install `requirements.txt`, verify `python -m stis.build_artifacts --check`, then run:

```bash
python -m streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

Health endpoint: `http://127.0.0.1:8501/_stcore/health` (expected HTTP 200 and `ok`). Health only establishes that Streamlit is running; artifact verification and UI tests separately establish application readiness.

## Streamlit Community Cloud

1. Create a GitHub repository containing this directory's contents at the repository root, including `raw/`, `data/bundle.json`, `stis/`, `app/`, `.streamlit/`, `requirements.txt`, and `streamlit_app.py`.
2. Sign in to Streamlit Community Cloud and grant access to that repository.
3. Create an app from the repository/branch, use main file `streamlit_app.py`, and choose Python **3.11** in advanced settings. No application secrets or API keys are required.
4. Deploy and verify all destinations, the comparison tab, and CSV downloads. The committed JSON bundle is served directly; no training needs to run during web startup.
5. After updates, rebuild locally, run checks, commit the changed source/data/bundle together, and redeploy. Source fingerprints intentionally reject stale bundles.

See the official [Community Cloud deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) and [dependency guidance](https://docs.streamlit.io/deploy/concepts/dependencies). Hosting/account permissions are managed by the provider; they were not available to this workspace. Confirm source data coverage and redistribution terms before representing the public app as an authoritative operational feed.

## Docker

```bash
docker build -t apac-tourism:2.0 .
docker run --rm -p 127.0.0.1:8501:8501 apac-tourism:2.0
```

Or use `docker compose up --build -d`. The Compose configuration binds the host port to loopback, drops capabilities, applies a read-only filesystem, and supplies temporary writable locations. Stop with `docker compose down`.

The image uses Python 3.11, installs the runtime lock, verifies the included bundle at image-build time, and runs as UID 10001. A Python-based health probe checks `/_stcore/health`; curl is not required inside the image. The application listens on 8501. The base image tag tracks Python 3.11 patch/security updates; for immutable production releases, resolve and pin an approved image digest in your release process.

Docker was **not installed in the execution environment**, so image build and Compose behavior were not tested locally. The included GitHub Actions workflow builds the image and probes a running container on Linux after all Python checks. That workflow is prepared but has not been run on a remote repository.

For a managed container host, configure port 8501 and health path `/_stcore/health`, WebSocket support, and HTTPS at the ingress. If a host mandates its own `$PORT`, override the container startup with a shell command that passes that port to `--server.port`; the included image uses 8501 by default. Do not disable CORS/XSRF protection as a deployment workaround. There are no application write operations or arbitrary upload features; it is a public research dashboard without user accounts. Introduce authentication before adding private data.

## Updates and troubleshooting

- **Stale-artifact message:** run `python -m stis.build_artifacts`; commit the new bundle alongside the source change. Even a backend formatting change affects source fingerprints.
- **Missing month/invalid target:** correct the data with documented provenance; do not bypass validation or silently interpolate targets.
- **Artifact build error:** the previous bundle remains on disk. Fix the input/code and rebuild before redeployment.
- **Unavailable port:** choose `--server.port 8502` locally and open that port instead.
- **Imports fail:** launch from the checked-out project root using the installed environment and the root `streamlit_app.py`.
- **Very wide error bands/negative R²:** these are model/data findings, not UI failures. Consult the full validation tables and methodology.
- **Dependencies change:** update `requirements.in`, resolve and pin the complete runtime closure (including platform-specific watchdog), run pip check/audit and tests, rebuild artifacts, and review changed metrics. Do not silently regenerate a lock with unrelated development packages.

## Remaining live-deployment action

No public deployment was attempted: there is no configured Git remote or authenticated target hosting account for this project. To publish, supply a GitHub repository plus authenticated Streamlit Community Cloud access, or an authenticated container hosting target. The code, data bundle, runtime lock, runbook, and deployment configuration are complete; the account/repository connection and provider deployment are the remaining external steps.

## XGBoost and corrected notebook dependencies (7 October revision)

`requirements.txt` uses XGBoost 3.2.0 and its smaller CPU-only distribution on Linux x86_64; other platforms use the standard distribution. No GPU is used. The Dockerfile installs `libgomp1` for its native runtime. On macOS, a discoverable OpenMP library is needed for training; `brew install libomp` is the normal setup. This local verification used the already-installed `/opt/anaconda3/lib/libomp.dylib` with `DYLD_FALLBACK_LIBRARY_PATH=/opt/anaconda3/lib` for model execution. That machine-specific path is not embedded in application code. [Official XGBoost installation guidance](https://xgboost.readthedocs.io/en/stable/install.html).

Notebook reproduction additionally requires `python -m pip install -r requirements-notebooks.txt`, then `python scripts/build_notebooks.py --execute` after rebuilding artifacts. Notebook tooling is deliberately excluded from the serving image. Artifact building records the XGBoost version alongside other numerical-library versions.
