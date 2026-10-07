# Architecture

```text
raw CSVs → strict validation → shared features + candidate forecasters
                             → chronological selection + final evaluation
                             → all-history outlooks
                             → atomic data/bundle.json
                                       ↓
                    fingerprint/schema check → read-only Streamlit UI → CSV exports
```

`stis/io.py` owns the input contract. `features.py` defines one immutable feature schema. `forecast.py` owns candidate construction, recursive inference, and operational bounds. `evaluate.py` owns the annual windows, selection, and historical error bands. `metrics.py` owns denominator behavior. None of those modules writes artifacts or imports Streamlit.

`build_artifacts.py` is the batch entry point. It evaluates all destinations before committing anything, records Python/numerical-library versions and SHA-256 fingerprints for raw CSVs and every `stis` source file, checks that sources did not change mid-build, serializes strict JSON, and publishes with a same-directory temporary file plus atomic replace. Failed builds leave the previous bundle intact. A single build should run at a time; there is no distributed scheduler or writer coordination.

`artifacts.py` performs freshness and schema checks. The dashboard reads the small bundle on each rerun, so replacing it is reflected immediately; there is no cache that can hide changed inputs. It never trains models, writes artifacts, deserializes pickle files, accepts arbitrary model paths, or exposes uploaded code. Data and forecasting modules are served as a read-only deployment image. Model parameters and errors remain auditable without loading binary estimators.

The backend is a reusable Python service layer and CLI, not a separate HTTP service. An extra API/database would add operational complexity to a three-series static portfolio dashboard without improving its current use case. If authenticated uploads, live ingestion, or remote model consumers become requirements, keep the same pure forecasting contract behind a queued service and introduce versioned artifact storage.

The small fixed search (six candidates × six validation origins, plus holdout and refit) makes batch computation inexpensive. Random forest runs with one worker and a fixed seed to avoid uncontrolled web-host resource usage and improve reproducibility. Exact bitwise equality across BLAS implementations/platforms is not promised; numeric cross-platform comparisons should use appropriate tolerances.

`legacy/` contains untouched source and notebooks for provenance. It is excluded from lint/test discovery and the container image, and is not imported by the new app. The original local virtual environment was not transferred. Project code runs from the checked-out root; this is an application repository, not a standalone wheel containing its datasets.
