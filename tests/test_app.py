from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app.values import forecast_view
from stis.artifacts import load_bundle
from stis.config import CANDIDATES, CITIES, ROOT


@pytest.mark.parametrize("city", list(CITIES))
def test_dashboard_destinations_and_controls(city):
    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
    app.sidebar.selectbox[0].select(city).run()
    assert not app.exception
    assert len(app.tabs) == 3
    assert len(app.metric) == 4
    assert len(app.sidebar.slider) == 0
    assert len(app.sidebar.radio) == 0
    data = load_bundle()["cities"][city]
    for model in CANDIDATES:
        app.sidebar.selectbox[1].select(model).run()
        assert not app.exception
        _, values = forecast_view(data["outlook"], model, data["data_end"])
        assert app.metric[0].value == f"{values['total']:,}"
        assert app.metric[1].value == f"{values['average']:,.0f}"
        assert app.metric[2].value == f"{values['maximum']:,}"
        assert app.metric[3].value == f"{values['minimum']:,}"
        assert len(app.dataframe[0].value) == 12
    app.sidebar.checkbox[0].check().run()
    assert not app.exception


def test_missing_bundle_shows_actionable_error(monkeypatch):
    from stis.artifacts import ArtifactError

    def fail():
        raise ArtifactError("Artifacts are missing.")

    monkeypatch.setattr("stis.artifacts.load_bundle", fail)
    app = AppTest.from_file(str(Path(ROOT) / "streamlit_app.py"), default_timeout=30).run()
    assert not app.exception
    assert "missing" in app.error[0].value
    assert "python -m stis.build_artifacts" in app.code[0].value


def test_city_shortcuts_empty_comparison_and_reset():
    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
    app.button(key="visit_Singapore").click().run()
    assert app.sidebar.selectbox[0].value == "Singapore"
    assert not app.exception
    app.multiselect[0].set_value([]).run()
    assert "Choose a model" in app.info[0].value
    assert not app.exception
    app.sidebar.checkbox[0].check().run()
    app.sidebar.button[0].click().run()
    assert app.sidebar.selectbox[0].value == "Bangkok"
    assert app.sidebar.checkbox[0].value is False
    assert not app.exception
