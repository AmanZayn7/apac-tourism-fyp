"""Generate corrected, independently executable counterparts to the nine legacy notebooks."""

import argparse
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = [
    (
        "BANGKOK RIDGE LOG (5)",
        "Bangkok",
        "ridge",
        "Removed current-target rolling leakage and preserved pandemic months so lags remain calendar-correct. Replaced leave-one-out Ridge selection with chronological annual windows.",
    ),
    (
        "HONG KONG RIDGE LOG (4)",
        "Hong Kong",
        "ridge",
        "Removed current-target rolling leakage and the deletion of 2020–2022 before shifts. Scaling now fits separately inside each training window.",
    ),
    (
        "RF BANGKOK (3)",
        "Bangkok",
        "tree",
        "Replaced the original YoY formulation: zero denominators created infinite targets. Removed full-series winsorization and contemporaneous target rolling means. This is a new log-level experiment, not a reproduction of the old score.",
    ),
    (
        "RF SINGAPORE (4)",
        "Singapore",
        "tree",
        "Removed full-series winsorization and contemporaneous YoY rolling leakage. The original recovery-index input was not supplied; this new log-level experiment explicitly uses singapore_2015_2024_final.csv and does not reproduce the original input.",
    ),
    (
        "HK RF (3)",
        "Hong Kong",
        "tree",
        "Removed full-series winsorization and contemporaneous YoY rolling leakage. This new log-level experiment evaluates untouched arrival counts, not clipped YoY targets.",
    ),
    (
        "SG RF AND XGB (5)",
        "Singapore",
        "tree",
        "Removed current-month hotel/search columns accidentally admitted by broad prefix selection. Availability at forecast origin is unverified. The missing recovery-index input is explicitly replaced with the supplied final Singapore CSV.",
    ),
    (
        "HK RF AND XGB (4)",
        "Hong Kong",
        "tree",
        "Removed current-month external predictors admitted by prefix selection, corrected the Singapore heading, and replaced rolling one-step testing with a fixed-origin twelve-month recursive forecast.",
    ),
    (
        "BKK SN (4)",
        "Bangkok",
        "baseline",
        "Corrected the Hong Kong heading and expanded the baseline evaluation from four months to the same complete annual windows used for every model. Seasonal lag 12 itself was valid.",
    ),
    (
        "HK SN (5)",
        "Hong Kong",
        "baseline",
        "Preserved the valid seasonal lag-12 baseline and replaced the four-month reporting window with the same full-year windows used by the other models.",
    ),
]


def notebook(name, city, family, correction):
    md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
    focus = {"ridge": ["ridge_1", "ridge_10", "ridge_100"], "tree": ["rf", "xgb"], "baseline": ["snaive"]}[
        family
    ]
    cells = [
        md(
            f"# {city}: corrected {family} forecasting study\n\nOriginal: `legacy/notebooks/{name}.ipynb`. The original is preserved unchanged. This executable counterpart uses the shared deployment implementation; it is a corrected experiment, not a claim that the original results were reproduced.\n\n**Critical corrections:** {correction}"
        ),
        md(
            "## Forecasting contract and reasoning\n\nPredict the next **12 monthly arrival counts from one fixed origin**, with no intervening actual observations. Keep the complete calendar, including pandemic months: deleting rows changes the meaning of lags. Model log1p arrivals so zero is defined; invert with expm1. This inversion is not an unbiased conditional-mean estimate. Never clip evaluation targets or impute missing targets. Only past arrival lags and known calendar terms are permitted; external predictors are excluded because their publication timing is not established.\n\nAll seven candidates use identical annual splits. Ridge α ∈ {1,10,100} is selected temporally, with scaling fit on training rows only. Random forest uses a fixed seed and modest fixed settings; XGBoost likewise uses 200 depth-3 trees, learning rate 0.05 and regularization, without holdout tuning. These choices limit the search and establish reproducible comparisons, not optimality."
        ),
        code("""from pathlib import Path
import sys

ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "stis/config.py").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
from stis.config import CANDIDATES, CITIES
from stis.io import load_city_raw
from stis.features import make_features
from stis.evaluate import evaluate_city, validation_origins
from stis.artifacts import load_bundle, source_fingerprints
from app.values import forecast_view
"""),
        code(f"""CITY = {city!r}
FOCUS_MODELS = {focus!r}
frame = load_city_raw(CITY)
print("Input:", CITIES[CITY]["file"])
print(CITIES[CITY]["note"])
print("Rows:", len(frame), "| Data:", frame.date.min().date(), "to", frame.date.max().date())
print("Python:", sys.executable)
display(frame.describe(include="all"))
"""),
        md(
            "## Prove features cannot see the current or future target\n\nChanging every target from a chosen month onward must leave that month's feature row unchanged. The deployed feature function is tested directly below. The first twelve rows are warm-up rows; they are not removed before constructing calendar lags."
        ),
        code("""cut = 60
original_features = make_features(frame)
altered = frame.copy()
altered.loc[cut:, "visitor_arrivals"] += 1234567
pd.testing.assert_series_equal(original_features.iloc[cut], make_features(altered).iloc[cut])
assert np.isclose(original_features.loc[cut, "log_lag12"], np.log1p(frame.loc[cut - 12, "visitor_arrivals"]))
assert np.isclose(original_features.loc[cut, "log_roll3"], np.log1p(frame.loc[cut-3:cut-1, "visitor_arrivals"]).mean())
print("PASS: feature causality and calendar lag/rolling identities.")
"""),
        md(
            "## Chronological model selection, then an untouched reporting year\n\nSix expanding annual windows (2018–2023 for this supplied dataset) select lowest mean MAE. Each window recursively predicts all twelve months without using that year's actuals as later lags. The final year (2024) is excluded from model selection and hyperparameter fitting. It is a reporting holdout; this audit already exposed its outcomes, so it cannot be claimed as a fresh blind experiment. After evaluation, refit on all available observations to forecast January–December 2025. Newer data is required for a current forecast."
        ),
        code("""development = frame.iloc[:-12]
plan = []
for stop in validation_origins(len(development)):
    plan.append({"train_end": development.date.iloc[stop-1], "test_start": development.date.iloc[stop], "test_end": development.date.iloc[stop+11]})
display(pd.DataFrame(plan))
print("Reporting holdout:", frame.date.iloc[-12].date(), "to", frame.date.iloc[-1].date())
"""),
        md(
            "## Recompute the experiment\n\nThis cell actually refits and evaluates all candidates using the same backend as deployment. The family-specific choice below uses validation MAE only. The overall deployment choice can be another family, including a simple baseline. No improvement over the original notebooks is claimed because their protocols and sometimes targets differ."
        ),
        code("""result = evaluate_city(frame)
leaderboard = pd.DataFrame(result["leaderboard"]).sort_values("validation_mae")
focus_choice = leaderboard.loc[leaderboard.model.isin(FOCUS_MODELS), "model"].iloc[0]
print("Family validation choice:", CANDIDATES[focus_choice])
print("Overall validation choice:", CANDIDATES[result["selected_model"]])
display(leaderboard)
reported = pd.DataFrame(result["holdout_metrics"])
display(reported.loc[reported.model.isin(list(dict.fromkeys(FOCUS_MODELS + ["snaive", "naive"]))), ["model", "mae", "rmse", "wape_pct", "r2", "mase", "guardrail_months", "band_coverage_pct"]])
"""),
        md(
            "## Interpret metrics without disguising errors\n\nMAE and RMSE are in arrivals; WAPE is sum absolute error / sum actual arrivals ×100. WAPE is not an accuracy percentage. Negative R² means worse squared error than the evaluation year's mean, and is retained. MASE uses the training seasonal-naïve scale. Zero denominators return unavailable values, never fabricated zeros. Cross-city errors should not be ranked by raw MAE because cities have different scales. Validation includes unusual pandemic periods and cannot guarantee future performance."
        ),
        code("""score = reported.set_index("model").loc[focus_choice]
print(f"{CANDIDATES[focus_choice]} reporting holdout MAE: {score.mae:,.2f} arrivals")
print("Reporting holdout WAPE (%):", score.wape_pct)
print("Reporting holdout R²:", score.r2)
if score.r2 < 0:
    print("Negative R²: worse squared error than the holdout mean; this is not hidden or relabelled as accuracy.")
"""),
        md(
            "## Twelve-month forecast and deployment reconciliation\n\nThe ML recursion has a disclosed numerical bound of 0–2× the training maximum. This is an operational heuristic, not a domain-derived physical limit; affected months are flagged. Error reference bands pool 72 validation errors (finite-sample 80% order statistic). They are **not calibrated prediction intervals**: dependence, selection and regime changes invalidate a guaranteed coverage claim. Main plots show point estimates only.\n\nThe published bundle is reproduced on macOS arm64 with the pinned numerical libraries and Python 3.11. Linux retraining was measured separately and produces materially different tree-model results despite fixed seeds. CI therefore checks notebook reproduction on macOS arm64 at rtol=1e-8 for every model, and verifies Linux serving of the unchanged published bundle in the actual container. Linux retraining is a different numerical experiment, not certified as equivalent to this release. All models must have identical dates and the same validation-selected winner. See docs/RUNTIME_REPRODUCTION.md for the measured comparison."
        ),
        code("""outlook, summary = forecast_view(result["outlook"], focus_choice, result["data_end"])
display(outlook[["date", "forecast", "forecast_arrivals", "guardrail_applied"]])
print("Displayed 12-month total:", f"{summary['total']:,}")
print("Monthly average of displayed estimates:", summary["average"])
print("Highest / lowest:", summary["maximum"], "/", summary["minimum"])
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(outlook.date.dt.strftime("%b %Y"), outlook.forecast_arrivals, marker="o", color="#168B80")
ax.set(title=f"{CITY} | {CANDIDATES[focus_choice]} | 12 predicted months", ylabel="Predicted arrivals")
ax.tick_params(axis="x", rotation=40)
ax.ticklabel_format(axis="y", style="plain")
ax.set_ylim(bottom=0)
ax.grid(axis="y", alpha=0.2)
fig.tight_layout()
plt.show()
plt.close(fig)
"""),
        code("""published = load_bundle()["cities"][CITY]
assert result["selected_model"] == published["selected_model"]
for candidate in CANDIDATES:
    computed, _ = forecast_view(result["outlook"], candidate, result["data_end"])
    deployed, _ = forecast_view(published["outlook"], candidate, published["data_end"])
    forecast_rtol = 1e-8
    score_rtol = 1e-8
    np.testing.assert_allclose(computed.forecast, deployed.forecast, rtol=forecast_rtol, atol=1e-5)
    assert computed.date.equals(deployed.date)
    for key in ("validation_mae",):
        a = next(row[key] for row in result["leaderboard"] if row["model"] == candidate)
        b = next(row[key] for row in published["leaderboard"] if row["model"] == candidate)
        np.testing.assert_allclose(a, b, rtol=score_rtol, atol=1e-5)
print("PASS: all seven forecasts and validation MAEs match the deployment bundle.")
print("Source fingerprints:", source_fingerprints()["raw"])
"""),
        md(
            "## Remaining limits\n\nThe supplied data is not a live tourism feed. Bangkok is a Thailand proxy, city-level coverage is unverified, and Hong Kong's upstream filling is undocumented. Publication delays and source definitions require primary-source verification. This work fixes leakage within the supplied modeling code; it cannot prove the upstream source was leakage-free. Re-run on new observations before claiming present-day forecasting skill. Original saved outputs are historical evidence, not reliable benchmarks for the corrected experiment."
        ),
    ]
    return nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    directory = ROOT / "notebooks"
    directory.mkdir(exist_ok=True)
    for name, city, family, correction in MANIFEST:
        doc = notebook(name, city, family, correction)
        path = directory / f"{name}.ipynb"
        nbf.write(doc, path)
        if args.execute:
            NotebookClient(
                doc, timeout=240, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}
            ).execute()
            nbf.write(doc, path)
        print(f"{'Executed' if args.execute else 'Generated'}: {path.name}", flush=True)


if __name__ == "__main__":
    main()
