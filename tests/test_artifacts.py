import json
import shutil

import pytest

from stis.artifacts import ArtifactError, load_bundle, write_bundle
from stis.config import BUNDLE_PATH, CANDIDATES, RAW_DIR


def test_published_bundle_loads_and_has_all_predictions():
    bundle = load_bundle()
    for city in bundle["cities"].values():
        assert len(city["history"]) == 120
        assert len(city["outlook"]) == len(CANDIDATES) * 12
        assert len(city["holdout"]) == len(CANDIDATES) * 12
        assert len(city["validation"]) == len(CANDIDATES) * 72
        assert len(city["folds"]) == len(CANDIDATES) * 6


def test_stale_raw_data_is_rejected(tmp_path):
    raw = tmp_path / "raw"
    shutil.copytree(RAW_DIR, raw)
    path = next(raw.glob("*.csv"))
    path.write_text(path.read_text() + "\n")
    with pytest.raises(ArtifactError, match="stale"):
        load_bundle(raw_dir=raw)


def test_missing_and_invalid_artifact(tmp_path):
    with pytest.raises(ArtifactError, match="missing or invalid"):
        load_bundle(tmp_path / "missing.json")
    path = tmp_path / "bad.json"
    path.write_text("not json")
    with pytest.raises(ArtifactError):
        load_bundle(path)


def test_failed_serialization_preserves_previous_artifact(tmp_path):
    path = tmp_path / "bundle.json"
    write_bundle({"good": True}, path)
    with pytest.raises(ValueError):
        write_bundle({"bad": float("nan")}, path)
    assert json.loads(path.read_text()) == {"good": True}
    assert list(tmp_path.iterdir()) == [path]


def test_changed_code_fingerprint_is_rejected(tmp_path):
    bundle = json.loads(BUNDLE_PATH.read_text())
    bundle["fingerprints"]["code"]["forecast.py"] = "different"
    path = tmp_path / "bundle.json"
    write_bundle(bundle, path)
    with pytest.raises(ArtifactError, match="stale"):
        load_bundle(path)


@pytest.mark.parametrize("corruption", ["missing_metadata", "missing_rows", "nan"])
def test_corrupt_bundle_rejected(tmp_path, corruption):
    bundle = json.loads(BUNDLE_PATH.read_text())
    if corruption == "missing_metadata":
        del bundle["generated_at"]
    elif corruption == "missing_rows":
        bundle["cities"]["Bangkok"]["outlook"].pop()
    else:
        bundle["cities"]["Bangkok"]["history"][0]["visitor_arrivals"] = float("nan")
    path = tmp_path / "bundle.json"
    path.write_text(json.dumps(bundle))
    with pytest.raises(ArtifactError):
        load_bundle(path)
