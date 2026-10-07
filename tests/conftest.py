import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def history():
    dates = pd.date_range("2015-01-01", periods=120, freq="MS")
    t = np.arange(len(dates))
    return pd.DataFrame({"date": dates, "visitor_arrivals": 1000 + 2 * t + 100 * np.sin(2 * np.pi * t / 12)})
