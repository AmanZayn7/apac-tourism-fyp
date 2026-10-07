# Data inventory and provenance limits

The three CSVs in `raw/` are preserved byte-for-byte from the supplied project. Each contains 120 monthly rows from January 2015 to December 2024. Checksums appear in `data/bundle.json` and `docs/source-inventory.json`.

| File | Supplied fields | Important qualification |
|---|---|---|
| bangkok_2015_2024_final.csv | date, year, month, visitor_arrivals, hotel_occupancy, google_trends | Original Ridge notebook calls it “Bangkok / Thailand proxy”; city-level scope is unverified. Six zero-arrival months exist. |
| singapore_2015_2024_final.csv | Same six fields | Original collection/source metadata is absent. |
| hongkong_2015_2024_final_filled.csv | date, year_x/month_x, year_y/month_y, visitor_arrivals, hotel_occupancy, google_trends | File name indicates prior filling; which values were filled, how, and with what information is undocumented. |

The loader uses only `date` and `visitor_arrivals`. It derives calendar features from the date, avoiding duplicate renamed year/month columns. It does not silently drop records, fill targets, or consume contemporaneous external variables. The raw files retain all original columns for investigation.

The project did not include original publisher URLs, extraction dates, collection scripts, release calendars, revision history, units/definitions beyond field names, or source licensing. Therefore these files cannot be asserted to be verified official statistics. Upstream revisions, interpolation, or filling may already contain information from later months; the new code prevents its own lookahead but cannot undo undocumented upstream leakage.

Cross-destination volume comparisons are limited by unresolved geographic definitions. The dashboard does not add the three series into an “APAC total,” and arrival events should not be interpreted as unique travelers. The included outlook is a historical 2025 scenario, not an up-to-date forecast for the date of use.

Before presenting the work as a current operational data product, document the exact publisher, geographic coverage, definition, release lag, revision policy, missing-value treatment, and redistribution terms for each series. Then update observations and rebuild; the date-driven protocol will advance automatically. No retrieval or licensing history was invented during this upgrade.
