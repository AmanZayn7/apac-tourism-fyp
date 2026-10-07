import json
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
import pytest

from app.charts import forecast_chart, ranking_chart
from app.design import DESTINATIONS, skyline_svg
from app.values import forecast_view
from stis.config import BUNDLE_PATH, CANDIDATES, CITIES


@pytest.mark.parametrize("city", CITIES)
@pytest.mark.parametrize("model", CANDIDATES)
def test_forecast_dates_values_cards_and_chart_reconcile(city, model):
    data = json.loads(BUNDLE_PATH.read_text())["cities"][city]
    frame, kpi = forecast_view(data["outlook"], model, data["data_end"])
    assert len(frame) == 12
    assert frame.date.min() == pd.Timestamp("2025-01-01")
    assert frame.date.max() == pd.Timestamp("2025-12-01")
    assert kpi["total"] == frame.forecast_arrivals.sum()
    assert kpi["average"] == kpi["total"] / 12
    assert kpi["maximum"] == frame.forecast_arrivals.max()
    assert kpi["minimum"] == frame.forecast_arrivals.min()
    np.testing.assert_array_equal(frame.forecast_arrivals, np.rint(frame.forecast))
    figure = forecast_chart([frame], [CANDIDATES[model]], "#168B80")
    assert len(figure.data) == 1
    assert list(figure.data[0].y) == frame.forecast_arrivals.tolist()
    assert len(figure.layout.xaxis.tickvals) == 12
    assert figure.layout.xaxis.type == "category"
    assert figure.layout.xaxis.tickvals[-1] == "Dec 2025"
    assert len(figure.data[0].x) == 12


def test_forecast_contract_rejects_missing_month_and_wrong_origin():
    data = json.loads(BUNDLE_PATH.read_text())["cities"]["Bangkok"]
    records = [r for r in data["outlook"] if r["model"] == "rf"]
    with pytest.raises(ValueError, match="twelve months"):
        forecast_view(records[:-1], "rf", data["data_end"])
    with pytest.raises(ValueError, match="twelve months"):
        forecast_view(records, "rf", "2025-01-01")


def test_comparison_and_reference_band_are_only_forecasts():
    data = json.loads(BUNDLE_PATH.read_text())["cities"]["Hong Kong"]
    frames = [forecast_view(data["outlook"], m, data["data_end"])[0] for m in ["rf", "xgb"]]
    figure = forecast_chart(frames, ["RF", "XGB"], "#6266AD", band=True)
    assert len(figure.data) == 4
    assert all(len(trace.x) == 12 for trace in figure.data)
    assert list(figure.data[-1].y) == frames[-1].forecast_arrivals.tolist()
    comparison = pd.DataFrame(data["holdout_metrics"])
    figure = ranking_chart(comparison, "r2", "Holdout R²", "rf", CANDIDATES, "#6266AD")
    assert list(figure.data[0].x) == sorted(comparison["r2"], reverse=True)


def test_all_destination_art_is_valid_local_svg():
    for city in DESTINATIONS:
        root = ET.fromstring(skyline_svg(city))
        assert root.attrib["aria-label"] == f"Stylized {city} skyline"
        assert "http" not in skyline_svg(city).replace("http://www.w3.org/2000/svg", "")
