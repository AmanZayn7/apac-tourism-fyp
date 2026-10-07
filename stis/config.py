"""Central, immutable project configuration; importing never writes to disk."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "raw"
BUNDLE_PATH = ROOT / "data" / "bundle.json"
SCHEMA_VERSION = 1
HORIZON = 12
MIN_HISTORY = 36
VALIDATION_FOLDS = 6
RANDOM_STATE = 42
CITIES = {
    "Bangkok": {
        "file": "bangkok_2015_2024_final.csv",
        "label": "Bangkok / Thailand proxy",
        "note": "The original notebook describes this series as a Thailand proxy. City-level coverage is unverified.",
    },
    "Singapore": {
        "file": "singapore_2015_2024_final.csv",
        "label": "Singapore",
        "note": "Visitor-arrival definitions and source provenance require verification with the original publisher.",
    },
    "Hong Kong": {
        "file": "hongkong_2015_2024_final_filled.csv",
        "label": "Hong Kong",
        "note": "The supplied file is labelled 'filled'; upstream imputation methods are undocumented.",
    },
}

# Small, predeclared search space. Every candidate uses the same temporal folds.
CANDIDATES = {
    "snaive": "Seasonal naïve",
    "naive": "Last observation",
    "ridge_1": "Ridge · α = 1",
    "ridge_10": "Ridge · α = 10",
    "ridge_100": "Ridge · α = 100",
    "rf": "Random forest",
    "xgb": "XGBoost",
}
