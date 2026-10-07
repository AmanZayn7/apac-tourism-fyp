# Live website verification — 7 October 2026

Public URL: https://apac-tourism.streamlit.app/

Verified in a fresh Chrome browser session with no existing account/profile:

- Dashboard rendered with title APAC · City Forecasts · Streamlit, forecast chart, four KPI cards and the historical 2025 forecast notice.
- Switching Singapore, Hong Kong and Bangkok changed the displayed forecast values.
- All seven model options appeared; selecting XGBoost changed the Bangkok total to 37,887,531.
- The historical error-band control enabled successfully.
- Comparison and model-evidence tabs opened successfully.
- The live download returned `bangkok_xgb_202501_12_months.csv`, containing exactly twelve rows from January through December 2025. Its displayed-arrival sum was 37,887,531, matching the live KPI.
- No application exception elements appeared. Initial page loading produced no browser page errors.
- At a 390 × 844 viewport the chart and KPI layout rendered. Month labels are crowded at this narrow width and could be improved; this is a presentation issue.

This is a point-in-time smoke check, not a guarantee of uptime, all possible interactions, or forecasting accuracy. All 21 city/model combinations were previously checked inside the Linux deployment container; the live browser check sampled city switching and XGBoost selection rather than exhaustively repeating every combination.

The hosting gateway requires normal cookie handling and JavaScript. A plain HTTP request returned the hosting shell even at the health path; that response was not treated as proof of application health. The browser-based checks above established the rendered application behavior.
