# Data inventory and provenance limits

The three CSVs in `raw/` are preserved byte-for-byte from the supplied project. Each contains 120 monthly rows from January 2015 to December 2024. Checksums appear in `data/bundle.json` and `docs/source-inventory.json`.

| File | Supplied fields | Important qualification |
|---|---|---|
| bangkok_2015_2024_final.csv | date, year, month, visitor_arrivals, hotel_occupancy, google_trends | Original Ridge notebook calls it “Bangkok / Thailand proxy”; city-level scope is unverified. Six zero-arrival months exist. |
| singapore_2015_2024_final.csv | Same six fields | Original collection/source metadata is absent. |
| hongkong_2015_2024_final_filled.csv | date, year_x/month_x, year_y/month_y, visitor_arrivals, hotel_occupancy, google_trends | File name indicates prior filling; which values were filled, how, and with what information is undocumented. |

The loader uses only `date` and `visitor_arrivals`. It derives calendar features from the date, avoiding duplicate renamed year/month columns. It does not silently drop records, fill targets, or consume contemporaneous external variables. The raw files retain all original columns for investigation.

The publisher links below were recorded in the project materials on 7 October 2026. Original extraction dates, collection scripts, release calendars, revision history, and preparation records remain unavailable. Confirmed source references do not establish that every supplied CSV value matches the publisher series. Upstream revisions, interpolation, or filling may already contain information from later months; the new code prevents its own lookahead but cannot undo undocumented upstream leakage.

Cross-destination volume comparisons are limited by unresolved geographic definitions. The dashboard does not add the three series into an “APAC total,” and arrival events should not be interpreted as unique travelers. The included outlook is a historical 2025 scenario, not an up-to-date forecast for the date of use.

Before presenting the work as a current operational data product, document the exact publisher, geographic coverage, definition, release lag, revision policy, missing-value treatment, and redistribution terms for each series. Then update observations and rebuild; the date-driven protocol will advance automatically. Original retrieval and licensing records are not available.

## Documented arrivals sources — 7 October 2026

These references are recorded in the FYP materials. Checks cover accessible publisher pages and their stated terms, plus the Singapore row-by-row reconciliation below. The Hong Kong and Thailand inputs have not been fully reconciled. The verification date is not the original dataset download date.

| Project series | Source reference | Verification and remaining limits |
|---|---|---|
| Singapore | [SingStat TableBuilder, table M550241](https://tablebuilder.singstat.gov.sg/table/TS/M550241) | Metadata retrieved from the official API identifies International Visitor Arrivals By A) Sex And B) Age Group, Monthly; provider Singapore Tourism Board; Total series 1; unit Number. All 120 supplied values differ from the current Total series; see reconciliation below. |
| Hong Kong | [Hong Kong Tourism Board, Tourism Statistics](https://www.discoverhongkong.com/eng/hktb/newsroom/tourism-statistics.html) | Official visitor-arrivals publication page. It directs users to PartnerNet for 2025 and earlier; the exact historical download used and subsequent filling still need documentation. |
| Bangkok-labelled Thailand proxy | [Bank of Thailand, Tourism Indicators, report 875](https://app.bot.or.th/BTWS_STAT/statistics/ReportPage.aspx?reportID=875&language=eng) | The report explicitly measures foreign tourists visiting **Thailand**, in **thousands**. Its credited source is the Economic Tourism and Sports Division, Ministry of Tourism and Sports. This is not a Bangkok-only arrivals series. Document and verify the conversion to individual arrivals in the supplied CSV; do not multiply the existing CSV again without reconciliation. |

### Reuse terms reviewed

- **Singapore:** [SingStat terms](https://www.singstat.gov.sg/terms-of-use) place datasets under the [Singapore Open Data Licence](https://data.gov.sg/open-data-licence). The licence permits reuse and distribution with source acknowledgement and a conspicuous licence link, subject to its exclusions and conditions. Confirm the selected table/series and original access details before completing the attribution notice. The project's forecasts and transformations are its own research, not official agency outputs or endorsements.
- **Hong Kong:** [HKTB terms](https://www.discoverhongkong.com/eng/terms-of-use.html), especially sections 4 and 10, permit personal non-commercial downloading but restrict reproduction/distribution of protected information absent a separate licence or permission. General website access is not evidence of an open-data grant. Dataset-specific terms or permission covering a public repository/dashboard remain unconfirmed.
- **Thailand:** [BOT terms](https://www.bot.or.th/en/terms-and-condition.html) permit downloading and copying for user use, subject to specific restrictions. They do not provide an explicit open-data redistribution licence for this project. The tourism series credits another ministry; verify the applicable dataset-specific reuse terms rather than assuming an unrestricted licence.

The repository presents a public historical portfolio/research demonstration. Dataset-specific redistribution terms remain unconfirmed; publication is not a claim that these datasets have a verified open licence. No source-data ownership or broad licence is claimed for the combined CSVs. Their hotel occupancy and Google Trends columns are outside the scope of these three arrivals references and need separate provenance if redistributed. The legacy copies and the full downloadable evidence bundle also contain historical data; removing only `raw/` would not remove all redistributed observations.

## Singapore source reconciliation — 7 October 2026

The official TableBuilder public API returned metadata for M550241 and all monthly observations. The table title is **International Visitor Arrivals By A) Sex And B) Age Group, Monthly**, data provider **Singapore Tourism Board**, Total series **1**, unit **Number**. The publisher last-updated date is 5 October 2026. API references: [metadata](https://tablebuilder.singstat.gov.sg/api/table/metadata/M550241) and [table data](https://tablebuilder.singstat.gov.sg/api/table/tabledata/M550241).

An exact numeric comparison of January 2015–December 2024 found **0 matching months out of 120** between the supplied Singapore CSV and the current Total series. January 2015 is 1,208,332 in the supplied CSV versus 1,252,608 in the current publisher table. December 2024 is 1,387,147 versus 1,390,641. The complete per-month differences are in [singapore-source-reconciliation.json](singapore-source-reconciliation.json).

This establishes a mismatch with the current referenced series, not the cause of the mismatch. An earlier export, documented revisions, a different series selection, or preprocessing could explain differences. The original export and transformation record are needed before claiming the supplied targets are official unmodified counts. Data and saved forecasts have not been replaced. Current performance scores describe the supplied research dataset and should not be asserted as verified forecasting performance on the official series.

A potentially reusable alternative for Hong Kong is [C&SD visitor-arrivals table 650-80001](https://www.censtatd.gov.hk/en/web_table.html?id=650-80001), listed on [DATA.GOV.HK](https://data.gov.hk/en-data/dataset/hk-censtatd-tablechart-650-80001/resource/00ba3cb2-e426-487d-ab00-fb27f677efee). [C&SD's notice](https://www.censtatd.gov.hk/en/page_31.html) permits specified statistical information reuse subject to attribution, modification disclosure and third-party exclusions. This is an investigation lead, not a replacement source already reconciled with the project's filled HKTB-based CSV.

### Singapore preprocessing

Project records dated 7 October 2026 identify preprocessing transformations of the Singapore arrival values. The numerical mismatch therefore must not be presented as proof of an unexplained copying error. The exact transformations, their parameters, order, time windows and use of future observations remain to be documented. This is necessary to interpret the target units and establish whether upstream preprocessing itself introduced lookahead. The original source values, supplied preprocessed targets, and log1p transformations performed later by the model are distinct stages. Model definitions and saved results remain unchanged.
