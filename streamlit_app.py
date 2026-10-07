"""Twelve-month forecasts with directly reconcilable cards, charts and exports."""

import json
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from app.charts import forecast_chart, ranking_chart
from app.design import DESTINATIONS, hero
from app.values import forecast_view
from stis.artifacts import ArtifactError, load_bundle
from stis.config import CANDIDATES, CITIES

st.set_page_config(page_title="APAC · City Forecasts", page_icon="✦", layout="wide")
st.markdown(f"<style>{(Path(__file__).parent / 'app/theme.css').read_text()}</style>", unsafe_allow_html=True)
CONFIG = {"displaylogo": False, "scrollZoom": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}
try:
    bundle = load_bundle()
except ArtifactError as error:
    st.title("APAC City Forecasts")
    st.error(str(error))
    st.code("python -m stis.build_artifacts", language="bash")
    st.stop()


def switch_city(value):
    st.session_state["destination"] = value


def reset():
    st.session_state.update(destination="Bangkok", band=False)
    for name, item in bundle["cities"].items():
        st.session_state[f"model_{name}"] = item["selected_model"]


def month_label(months):
    if len(months) == 12:
        return "Same estimate in all 12 months"
    return ", ".join(months) if len(months) <= 2 else f"Tied across {len(months)} months"


st.sidebar.markdown("### Forecast settings")
st.sidebar.caption("One destination. One model. Twelve months.")
city = st.sidebar.selectbox(
    "Destination", list(CITIES), key="destination", format_func=lambda key: CITIES[key]["label"]
)
data = bundle["cities"][city]
chosen = data["selected_model"]
identity = DESTINATIONS[city]
model = st.sidebar.selectbox(
    "Forecast model",
    list(CANDIDATES),
    index=list(CANDIDATES).index(chosen),
    format_func=lambda key: CANDIDATES[key] + (" · validation choice" if key == chosen else ""),
    key=f"model_{city}",
)
show_band = st.sidebar.checkbox(
    "Show error reference band",
    value=False,
    key="band",
    help="Past validation errors, not a calibrated prediction interval. Off by default to keep the predicted path clear.",
)
st.sidebar.button("Reset forecast", on_click=reset, width="stretch")
st.sidebar.divider()
st.sidebar.caption(
    f"Data cutoff: {pd.Timestamp(data['data_end']):%B %Y}.\n\nThe forecast starts the following month. Updating the dates requires new observed data and a rebuilt model."
)
st.sidebar.caption("Abdul Muhaimin Aman · APAC tourism research")
try:
    outlook, kpi = forecast_view(data["outlook"], model, data["data_end"])
except ValueError as error:
    st.error(str(error))
    st.stop()
start, end = outlook["date"].iloc[0], outlook["date"].iloc[-1]
st.markdown(
    '<div class="brand-row"><div class="brand"><span class="brand-mark">✦</span>APAC / CITY FORECASTS</div><div class="edition">TWELVE MONTHS, CLEARLY PREDICTED</div></div>',
    unsafe_allow_html=True,
)
for col, name in zip(st.columns(3), CITIES):
    col.button(
        name,
        key=f"visit_{name}",
        on_click=switch_city,
        args=(name,),
        width="stretch",
        type="primary" if name == city else "secondary",
    )
st.markdown(hero(city, f"{pd.Timestamp(data['data_end']):%B %Y}", len(CANDIDATES)), unsafe_allow_html=True)
if date.today() > end.date():
    st.markdown(
        f'<div class="archive-note"><strong>Historical forecast: {start:%b %Y}–{end:%b %Y}.</strong> Trained through {pd.Timestamp(data["data_end"]):%B %Y}. Newer observations are required for a current forecast.</div>',
        unsafe_allow_html=True,
    )
st.caption(CITIES[city]["note"])
if city == "Singapore":
    st.caption(
        "Research note: Singapore forecasts and scores use the supplied preprocessed "
        "historical dataset. Full preprocessing details are not available."
    )
forecast_tab, compare_tab, evidence_tab = st.tabs(
    ["12-month forecast", "Compare forecasts", "Model evidence"]
)

with forecast_tab:
    st.subheader(f"{start:%B %Y} — {end:%B %Y}")
    st.caption(f"{CITIES[city]['label']} · {CANDIDATES[model]} · exactly 12 predicted months")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Total arrivals",
        f"{kpi['total']:,}",
        help="Exact sum of the twelve rounded monthly model estimates shown in the table and chart.",
    )
    c2.metric(
        "Monthly average",
        f"{kpi['average']:,.0f}",
        help="Total divided by 12, displayed to the nearest arrival. The calculation panel shows the unrounded average.",
    )
    c3.metric("Highest estimate", f"{kpi['maximum']:,}", help=month_label(kpi["peak_months"]))
    c4.metric("Lowest estimate", f"{kpi['minimum']:,}", help=month_label(kpi["low_months"]))
    st.caption(
        "All four cards are calculated from the same twelve predicted monthly values below. These are model estimates, not observed visitor counts."
    )
    st.plotly_chart(
        forecast_chart([outlook], [CANDIDATES[model]], identity["accent"], band=show_band),
        width="stretch",
        config=CONFIG,
        key="main_forecast",
    )
    if show_band:
        st.caption(
            "Shading uses historical validation errors. It is not a confidence interval or guaranteed future range; pandemic errors can make it wide."
        )
    if outlook["guardrail_applied"].any():
        st.warning(
            "This model reached the documented 0–2× training-maximum bound. The affected months are flagged in the table; treat these estimates cautiously."
        )
    table = outlook[["date", "forecast_arrivals"]].rename(
        columns={"date": "Month", "forecast_arrivals": "Predicted arrivals"}
    )
    if outlook["guardrail_applied"].any():
        table["Operational bound used"] = outlook["guardrail_applied"].values
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        column_config={
            "Month": st.column_config.DateColumn(format="MMM YYYY"),
            "Predicted arrivals": st.column_config.NumberColumn(format="%,d"),
        },
    )
    export = outlook.assign(
        destination=CITIES[city]["label"],
        forecast_origin=data["data_end"],
        display_rule="nearest_integer_per_month; KPI_total=sum(forecast_arrivals)",
        band_type="historical_error_reference_not_confidence_interval",
    )
    st.download_button(
        "Download the 12-month forecast",
        export.to_csv(index=False),
        file_name=f"{city.lower().replace(' ', '_')}_{model}_{start:%Y%m}_12_months.csv",
        mime="text/csv",
    )
    with st.expander("Verify these calculations"):
        st.write(f"**Total:** sum of the 12 displayed monthly estimates = **{kpi['total']:,}** arrivals.")
        st.write(
            f"**Monthly average:** {kpi['total']:,} ÷ 12 = **{kpi['average']:,.6f}** arrivals, rounded only for the card."
        )
        st.write(f"**Highest:** {kpi['maximum']:,} — {month_label(kpi['peak_months'])}.")
        st.write(f"**Lowest:** {kpi['minimum']:,} — {month_label(kpi['low_months'])}.")
        st.caption(
            "Monthly model outputs are rounded once to whole arrivals. The CSV includes both full-precision forecast and displayed forecast_arrivals. Counts represent arrival events, not necessarily unique people."
        )
        st.caption(
            f"Source: {CITIES[city]['file']} · SHA-256: {bundle['fingerprints']['raw'][CITIES[city]['file']]}"
        )

with compare_tab:
    st.subheader("Different models. The same twelve months.")
    models = st.multiselect(
        "Compare up to three forecast models",
        list(CANDIDATES),
        max_selections=3,
        default=list(dict.fromkeys([model, "snaive"])),
        format_func=lambda key: CANDIDATES[key],
        key=f"compare_{city}_{model}",
    )
    if models:
        frames = [forecast_view(data["outlook"], m, data["data_end"])[0] for m in models]
        st.plotly_chart(
            forecast_chart(frames, [CANDIDATES[m] for m in models], identity["accent"]),
            width="stretch",
            config=CONFIG,
            key="comparison_forecast",
        )
        comparison = pd.DataFrame(
            {
                "Month": outlook["date"],
                **{CANDIDATES[m]: f["forecast_arrivals"] for m, f in zip(models, frames)},
            }
        )
        st.dataframe(
            comparison,
            hide_index=True,
            width="stretch",
            column_config={"Month": st.column_config.DateColumn(format="MMM YYYY")},
        )
    else:
        st.info("Choose a model to compare its twelve-month forecast.")
    st.caption(
        "These are alternative predictions, not observed outcomes. Model disagreement is not a calibrated uncertainty interval."
    )

with evidence_tab:
    st.subheader("What supports this forecast?")
    st.write(
        f"**Validation choice: {CANDIDATES[chosen]}.** Chosen using six earlier 12-month forecast windows, before the final reporting year. Selecting another model in the sidebar does not change that validation result."
    )
    st.write(
        f"**Data cutoff:** {data['data_end']} · **Forecast:** {start:%B %Y} to {end:%B %Y} · **Supplied observations:** {data['history_rows']} monthly rows."
    )
    with st.expander("Validation and holdout scores"):
        scores = pd.DataFrame(data["leaderboard"]).merge(pd.DataFrame(data["holdout_metrics"]), on="model")
        scores["Model"] = scores["model"].map(CANDIDATES)
        st.dataframe(
            scores[["Model", "validation_mae", "mae", "wape_pct", "r2", "mase", "band_coverage_pct"]],
            hide_index=True,
            width="stretch",
        )
        st.caption(
            f"Final reporting window: {data['holdout_start']} to {data['data_end']}. These are historical error scores, not accuracy measurements of the unevaluated outlook. Negative R² is retained."
        )
        st.plotly_chart(
            ranking_chart(
                scores, "validation_mae", "Validation MAE · arrivals", chosen, CANDIDATES, identity["accent"]
            ),
            width="stretch",
            config=CONFIG,
            key="validation_ranking",
        )
    with st.expander("Arrivals source references"):
        st.markdown("""
- **Singapore:** [SingStat table M550241](https://tablebuilder.singstat.gov.sg/table/TS/M550241), International Visitor Arrivals By A) Sex And B) Age Group, Monthly; provider Singapore Tourism Board. [Singapore Open Data Licence](https://data.gov.sg/open-data-licence). Reference checked 7 October 2026; original download date is unknown. The supplied targets differ from the current Total series.
- **Hong Kong:** [Hong Kong Tourism Board tourism statistics](https://www.discoverhongkong.com/eng/hktb/newsroom/tourism-statistics.html). Historical export and filling methods remain undocumented; redistribution terms require confirmation.
- **Thailand proxy:** [Bank of Thailand report 875](https://app.bot.or.th/BTWS_STAT/statistics/ReportPage.aspx?reportID=875&language=eng), sourced from the Ministry of Tourism and Sports. Publisher arrivals cover Thailand nationally and are reported in thousands; the supplied CSV conversion remains unreconciled.

The owner identified these source references. This does not certify that the supplied files reproduce the publisher data. Forecasts and transformations are this project's research and are not endorsed by the publishers.
""")
    with st.expander("Method and limitations"):
        st.markdown("""
- **One shared forecasting implementation:** the corrected notebooks and deployed artifacts use the same date validation, features, models and multi-step evaluation.
- **Past-only features:** log1p arrival lags (1, 3, 6, 12), shifted rolling means (3, 6), and the target month's calendar terms. Pandemic months remain on the calendar. No unavailable same-month external predictors.
- **Chronological selection:** six expanding annual windows choose the lowest mean MAE. The final year is excluded from selection; all models refit on the available history for this outlook.
- **Models:** seasonal naïve, last observation, three scaled Ridge candidates, random forest and XGBoost. Full settings and reasoning are documented in the corrected notebooks.
- **Operational bound:** recursive ML forecasts are constrained to 0–2× that training history's maximum. This numerical safeguard is a disclosed heuristic, not a physical bound; affected months are flagged.
- **Reference bands:** 72 past validation errors per model determine a pooled historical error radius. Dependence, model selection and regime change prevent a calibrated coverage claim.
- **Unresolved data limits:** provenance, release delays and Hong Kong's upstream filling remain unverified. The supplied Singapore CSV is used explicitly; the different original notebook input was not supplied. Log inversion is not an unbiased conditional-mean estimate.
""")
    st.download_button(
        "Download full model evidence",
        json.dumps(bundle, indent=2, allow_nan=False),
        file_name="apac_forecast_evidence.json",
        mime="application/json",
    )
st.markdown(
    '<div class="footer"><span>✦ APAC / CITY FORECASTS</span><span>Calculated from model outputs · No live tourism feed</span></div>',
    unsafe_allow_html=True,
)
