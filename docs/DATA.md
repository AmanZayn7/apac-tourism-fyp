# Data inventory and provenance limits

The three CSVs in `raw/` are preserved byte-for-byte from the supplied project. Each contains 120 monthly rows from January 2015 to December 2024. Checksums appear in `data/bundle.json` and `docs/source-inventory.json`.

| File | Supplied fields | Important qualification |
|---|---|---|
| bangkok_2015_2024_final.csv | date, year, month, visitor_arrivals, hotel_occupancy, google_trends | Original Ridge notebook calls it “Bangkok / Thailand proxy”; city-level scope is unverified. Six zero-arrival months exist. |
| singapore_2015_2024_final.csv | Same six fields | Original collection/source metadata is absent. |
| hongkong_2015_2024_final_filled.csv | date, year_x/month_x, year_y/month_y, visitor_arrivals, hotel_occupancy, google_trends | File name indicates prior filling; which values were filled, how, and with what information is undocumented. |

The loader uses only `date` and `visitor_arrivals`. It derives calendar features from the date, avoiding duplicate renamed year/month columns. It does not silently drop records, fill targets, or consume contemporaneous external variables. The raw files retain all original columns for investigation.

The project owner confirmed the publisher links below on 7 October 2026. Original extraction dates, collection scripts, release calendars, revision history, and preparation records remain unavailable. Confirmed source references do not establish that every supplied CSV value matches the publisher series. Upstream revisions, interpolation, or filling may already contain information from later months; the new code prevents its own lookahead but cannot undo undocumented upstream leakage.

Cross-destination volume comparisons are limited by unresolved geographic definitions. The dashboard does not add the three series into an “APAC total,” and arrival events should not be interpreted as unique travelers. The included outlook is a historical 2025 scenario, not an up-to-date forecast for the date of use.

Before presenting the work as a current operational data product, document the exact publisher, geographic coverage, definition, release lag, revision policy, missing-value treatment, and redistribution terms for each series. Then update observations and rebuild; the date-driven protocol will advance automatically. No retrieval or licensing history was invented during this upgrade.

## Owner-confirmed arrivals sources — 7 October 2026

These links were supplied in the FYP report screenshot and explicitly confirmed by the project owner. Verification below concerns the accessible publisher pages and their stated terms; a row-by-row reconciliation with the supplied CSVs has not been performed. The verification date is not the original dataset download date.

| Project series | Source reference | Verification and remaining limits |
|---|---|---|
| Singapore | [SingStat TableBuilder, table M550241](https://tablebuilder.singstat.gov.sg/table/TS/M550241) | Owner-confirmed source. TableBuilder requires JavaScript; the precise table title, units and selected series were not independently retrieved in this review. |
| Hong Kong | [Hong Kong Tourism Board, Tourism Statistics](https://www.discoverhongkong.com/eng/hktb/newsroom/tourism-statistics.html) | Official visitor-arrivals publication page. It directs users to PartnerNet for 2025 and earlier; the exact historical download used and subsequent filling still need documentation. |
| Bangkok-labelled Thailand proxy | [Bank of Thailand, Tourism Indicators, report 875](https://app.bot.or.th/BTWS_STAT/statistics/ReportPage.aspx?reportID=875&language=eng) | The report explicitly measures foreign tourists visiting **Thailand**, in **thousands**. Its credited source is the Economic Tourism and Sports Division, Ministry of Tourism and Sports. This is not a Bangkok-only arrivals series. Document and verify the conversion to individual arrivals in the supplied CSV; do not multiply the existing CSV again without reconciliation. |

### Reuse terms reviewed

- **Singapore:** [SingStat terms](https://www.singstat.gov.sg/terms-of-use) place datasets under the [Singapore Open Data Licence](https://data.gov.sg/open-data-licence). The licence permits reuse and distribution with source acknowledgement and a conspicuous licence link, subject to its exclusions and conditions. Confirm the selected table/series and original access details before completing the attribution notice. The project's forecasts and transformations are its own research, not official agency outputs or endorsements.
- **Hong Kong:** [HKTB terms](https://www.discoverhongkong.com/eng/terms-of-use.html), especially sections 4 and 10, permit personal non-commercial downloading but restrict reproduction/distribution of protected information absent a separate licence or permission. General website access is not evidence of an open-data grant. Dataset-specific terms or permission covering a public repository/dashboard remain unconfirmed.
- **Thailand:** [BOT terms](https://www.bot.or.th/en/terms-and-condition.html) permit downloading and copying for user use, subject to specific restrictions. They do not provide an explicit open-data redistribution licence for this project. The tourism series credits another ministry; verify the applicable dataset-specific reuse terms rather than assuming an unrestricted licence.

The repository remains private while public redistribution is unresolved. No source-data ownership or broad licence is claimed for the combined CSVs. Their hotel occupancy and Google Trends columns are outside the scope of these three arrivals references and need separate provenance if redistributed. The legacy copies and the full downloadable evidence bundle also contain historical data; removing only `raw/` would not remove all redistributed observations.
