# Preserved original work

`system/` is the original application, raw inputs, saved artifacts, and dependency list. `notebooks/` contains all nine supplied notebooks with their original names and contents. Files are for provenance and comparison; they are **not** the production entry point and are excluded from tests, linting, and the container image.

The old virtual environment, macOS metadata/cache files, and duplicate ZIP were omitted. Use the root README and `streamlit_app.py` for the upgraded project. Original ML evaluation outputs contain the methodological defects documented in `../docs/AUDIT.md` and must not be used as validated accuracy claims.
