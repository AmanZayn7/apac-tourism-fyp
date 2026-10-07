"""Reproduce targeted notebook defects without training models or altering notebooks.

Run from any directory: python scripts/audit_notebooks.py
The Singapore missing input is reported, never silently replaced.
"""

import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
raw = root / "raw"
results = {}
bkk = pd.read_csv(raw / "bangkok_2015_2024_final.csv", parse_dates=["date"]).set_index("date")
filtered = bkk.loc[(bkk.index.year >= 2016) & (bkk.index.year <= 2019) | (bkk.index.year.isin([2023, 2024]))]
i = filtered.index.get_loc("2023-01-01")
results["ridge_calendar"] = {
    "target": "2023-01-01",
    "lag1_source": str(filtered.index[i - 1].date()),
    "lag12_source": str(filtered.index[i - 12].date()),
}
logs = np.log(filtered.visitor_arrivals)
changed = logs.copy()
changed.loc["2024-06-01"] += np.log(2)
results["ridge_current_target_leak"] = {
    "roll3_change_when_current_target_doubled": float(
        changed.rolling(3).mean().loc["2024-06-01"] - logs.rolling(3).mean().loc["2024-06-01"]
    )
}
yoy = (bkk.visitor_arrivals / bkk.visitor_arrivals.shift(12) - 1) * 100
results["bangkok_yoy"] = {
    "infinite_dates": [str(x.date()) for x in yoy.index[np.isinf(yoy)]],
    "nan_count": int(yoy.isna().sum()),
}
finite = yoy.replace([np.inf, -np.inf], np.nan)
results["bangkok_yoy"]["finite_99pct"] = float(finite.quantile(0.99))
with np.errstate(invalid="ignore"):
    q = yoy.dropna().quantile(0.99)
results["bangkok_yoy"]["original_99pct"] = float(q) if np.isfinite(q) else str(q)
hk = pd.read_csv(raw / "hongkong_2015_2024_final_filled.csv", parse_dates=["date"]).set_index("date")
yoyhk = (hk.visitor_arrivals / hk.visitor_arrivals.shift(12) - 1) * 100
mut = yoyhk.copy()
mut.loc[mut.index.year == 2024] = 1e9
results["full_series_winsorization"] = {
    "original_q99": float(yoyhk.quantile(0.99)),
    "q99_after_only_test_targets_changed": float(mut.quantile(0.99)),
    "training_values_changed": int(
        (
            yoyhk.clip(yoyhk.quantile(0.01), yoyhk.quantile(0.99)).loc[:"2023-12-01"]
            != yoyhk.clip(mut.quantile(0.01), mut.quantile(0.99)).loc[:"2023-12-01"]
        )
        .loc[yoyhk.loc[:"2023-12-01"].notna()]
        .sum()
    ),
}
p = root / "legacy/notebooks/HK RF AND XGB (4).ipynb"
code = "".join(json.loads(p.read_text())["cells"][0]["source"])
node = next(n for n in ast.parse(code).body if isinstance(n, ast.FunctionDef) and n.name == "build_features")
scope = {"pd": pd, "np": np}
exec(compile(ast.Module(body=[node], type_ignores=[]), str(p), "exec"), scope)
for enabled in [True, False]:
    d = scope["build_features"](hk.reset_index(), use_exogenous=enabled)
    cols = [c for c in d.columns if c.startswith(("log_lag", "log_roll", "m_", "hotel", "google"))]
    results[f"exogenous_enabled_{enabled}"] = {
        "selected_exogenous_columns": [c for c in cols if c.startswith(("hotel", "google"))]
    }
results["singapore_required_input_in_supplied_folder"] = any(
    (root / "legacy").rglob("singapore_with_recovery_index.csv")
)
(root / "docs/notebook-audit-evidence.json").write_text(json.dumps(results, indent=2, allow_nan=False) + "\n")
print(json.dumps(results, indent=2))
