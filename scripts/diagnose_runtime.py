"""Compare recomputed results with the release bundle without modifying either."""

import argparse
import importlib.metadata
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from stis.artifacts import load_bundle  # noqa: E402
from stis.config import CANDIDATES, CITIES  # noqa: E402
from stis.evaluate import evaluate_city  # noqa: E402
from stis.features import make_features  # noqa: E402
from stis.forecast import forecast  # noqa: E402
from stis.io import load_city_raw  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    published = load_bundle()
    report = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "versions": {p: importlib.metadata.version(p) for p in ("numpy", "pandas", "scikit-learn")},
        "cities": {},
    }
    for city in CITIES:
        history = load_city_raw(city)
        current = evaluate_city(history)
        saved = published["cities"][city]
        details = {
            "selected": current["selected_model"],
            "published_selected": saved["selected_model"],
            "features_hex": [
                [float(value).hex() for value in row] for row in make_features(history).to_numpy()
            ],
            "models": {},
        }
        for model in CANDIDATES:
            values = np.array([r["forecast"] for r in current["outlook"] if r["model"] == model])
            reference = np.array([r["forecast"] for r in saved["outlook"] if r["model"] == model])
            repeated = forecast(history, model)["forecast"].to_numpy()
            score = next(r["validation_mae"] for r in current["leaderboard"] if r["model"] == model)
            saved_score = next(r["validation_mae"] for r in saved["leaderboard"] if r["model"] == model)
            delta = float(np.max(np.abs(values - reference) / np.maximum(np.abs(reference), 1e-12)))
            details["models"][model] = {
                "max_relative_forecast_difference": delta,
                "repeat_identical": bool(np.array_equal(values, repeated)),
                "forecast": values.tolist(),
                "validation_mae": score,
                "published_validation_mae": saved_score,
            }
            print(
                f"{city} {model}: difference={delta:.8%}, repeat={np.array_equal(values, repeated)}",
                flush=True,
            )
        report["cities"][city] = details
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
