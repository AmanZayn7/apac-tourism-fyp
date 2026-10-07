"""Atomic JSON artifact publishing and stale-artifact detection. No pickle loading."""

import hashlib
import json
import os
import tempfile
from pathlib import Path

from .config import BUNDLE_PATH, CANDIDATES, CITIES, HORIZON, RAW_DIR, ROOT, SCHEMA_VERSION, VALIDATION_FOLDS


class ArtifactError(ValueError):
    """The app cannot safely serve this artifact."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_fingerprints(raw_dir: Path = RAW_DIR) -> dict:
    return {
        "raw": {spec["file"]: sha256(Path(raw_dir) / spec["file"]) for spec in CITIES.values()},
        "code": {p.name: sha256(p) for p in sorted((ROOT / "stis").glob("*.py"))},
    }


def write_bundle(bundle: dict, path: Path = BUNDLE_PATH) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(bundle, indent=2, allow_nan=False, ensure_ascii=False)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def load_bundle(path: Path = BUNDLE_PATH, *, raw_dir: Path = RAW_DIR) -> dict:
    try:
        bundle = json.loads(Path(path).read_text(encoding="utf-8"))
        # json.loads accepts NaN/Infinity by default; strict reserialization rejects them.
        json.dumps(bundle, allow_nan=False)
        if not all(key in bundle for key in ("generated_at", "runtime", "project_version")):
            raise ArtifactError("Artifact metadata is incomplete.")
        if bundle["schema_version"] != SCHEMA_VERSION:
            raise ArtifactError("Unsupported artifact schema.")
        if set(bundle["cities"]) != set(CITIES):
            raise ArtifactError("Artifact is missing destinations.")
        if bundle["fingerprints"] != source_fingerprints(raw_dir):
            raise ArtifactError("Artifacts are stale: source data or forecasting code changed.")
        for city in CITIES:
            item = bundle["cities"][city]
            required = (
                "selected_model",
                "holdout",
                "outlook",
                "history",
                "holdout_metrics",
                "leaderboard",
                "folds",
                "validation",
                "training_start",
                "development_end",
                "data_end",
                "holdout_start",
                "history_rows",
                "development_rows",
                "fit_rows_ml_development",
                "fit_rows_ml_final",
            )
            if not all(k in item for k in required):
                raise ArtifactError(f"Incomplete artifact for {city}.")
            if item["selected_model"] not in CANDIDATES:
                raise ArtifactError(f"Invalid selected model for {city}.")
            for key, length in (
                ("holdout", len(CANDIDATES) * HORIZON),
                ("outlook", len(CANDIDATES) * HORIZON),
                ("validation", len(CANDIDATES) * HORIZON * VALIDATION_FOLDS),
                ("folds", len(CANDIDATES) * VALIDATION_FOLDS),
                ("holdout_metrics", len(CANDIDATES)),
                ("leaderboard", len(CANDIDATES)),
            ):
                if not isinstance(item[key], list) or len(item[key]) != length:
                    raise ArtifactError(f"Incomplete {key} records for {city}.")
                if set(row["model"] for row in item[key]) != set(CANDIDATES):
                    raise ArtifactError(f"Invalid {key} models for {city}.")
        return bundle
    except ArtifactError:
        raise
    except (OSError, KeyError, TypeError, ValueError) as error:
        raise ArtifactError(
            "Artifacts are missing or invalid. Run: python -m stis.build_artifacts"
        ) from error
