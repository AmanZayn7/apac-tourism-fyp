"""CLI: build every destination before atomically publishing one artifact."""

import argparse
import importlib.metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from . import __version__
from .artifacts import load_bundle, source_fingerprints, write_bundle
from .config import BUNDLE_PATH, CITIES, RAW_DIR, SCHEMA_VERSION
from .evaluate import evaluate_city
from .io import load_city_raw


def build_bundle(raw_dir: Path = RAW_DIR) -> dict:
    cities = {}
    fingerprints = source_fingerprints(raw_dir)
    for city in CITIES:
        print(f"Evaluating {city}…", flush=True)
        cities[city] = evaluate_city(load_city_raw(city, raw_dir))
    if fingerprints != source_fingerprints(raw_dir):
        raise RuntimeError("Sources changed during evaluation; retry with stable inputs.")
    bundle = {
        "schema_version": SCHEMA_VERSION,
        "project_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime": {
            "python": platform.python_version(),
            "xgboost": __import__("xgboost").__version__,
            **{p: importlib.metadata.version(p) for p in ("numpy", "pandas", "scikit-learn")},
        },
        "fingerprints": fingerprints,
        "cities": cities,
    }
    # Convert timestamps at the serialization boundary, not in numerical code.
    return json.loads(
        json.dumps(
            bundle,
            default=lambda value: (
                value.strftime("%Y-%m-%d") if isinstance(value, pd.Timestamp) else str(value)
            ),
            allow_nan=False,
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--output", type=Path, default=BUNDLE_PATH)
    parser.add_argument("--check", action="store_true", help="Validate artifact freshness without training.")
    args = parser.parse_args()
    if args.check:
        load_bundle(args.output, raw_dir=args.raw_dir)
        print("Artifact schema and source fingerprints verified.")
    else:
        bundle = build_bundle(args.raw_dir)
        write_bundle(bundle, args.output)
        print(f"Published {args.output}")


if __name__ == "__main__":
    main()
