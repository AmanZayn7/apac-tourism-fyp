# Audit of all nine research notebooks

**Correction status (7 October revision):** all nine originals now have corrected, executed counterparts in [notebooks](../notebooks/README.md). This report continues to describe the preserved original code. Corrected experiments use the shared deployment backend and do not claim to reproduce incomparable original results.

**Audit date: 7 October 2026. Scope: all code cells, saved text outputs, and referenced inputs in all nine supplied notebooks.**

The notebooks remain unchanged. This report is an audit and correction specification, not a claim that the original models have been repaired or rerun. Targeted computational probes reproduce individual defects using the supplied Bangkok/Hong Kong data and current project environment. Full original-model execution was not performed. Saved notebook scores are historical outputs, not newly verified results.

## Decision summary

**Do not use the existing notebook scores to choose a production forecasting model.** Five notebooks directly leak their current target through rolling features. Two others correctly shift target rolling features but inadvertently include current-month external predictors. Those predictors require an availability argument that the notebooks do not provide. The two seasonal-naïve notebooks have valid lag-12 baseline logic, but assess only four months, making cross-notebook comparisons inconsistent.

All nine contain one nonempty code cell followed by an empty code cell. None contains a Markdown methodology or discussion section. Comments describe steps, but do not sufficiently justify the forecast origin/horizon, information available at that origin, model selection, data treatment, or conclusions. This observation concerns the submitted evidence, not the author's intentions.

### Inventory and disposition

| Notebook | Actual experiment | Main disposition |
|---|---|---|
| BANGKOK RIDGE LOG (5) | Bangkok/Thailand proxy, log Ridge | Critical target leakage and broken calendar lags; unsuitable alpha validation |
| HONG KONG RIDGE LOG (4) | Hong Kong, log Ridge | Same structural defects; saved results do not support optimistic comments |
| RF BANGKOK (3) | Bangkok, YoY RF **and XGBoost** | Critical rolling/threshold leakage; zero denominators break percentile calculations |
| RF SINGAPORE (4) | Singapore, YoY RF **and XGBoost** | Critical rolling/threshold leakage; exact named input missing |
| HK RF (3) | Hong Kong, YoY RF **and XGBoost** | Critical rolling/threshold leakage; extreme saved errors unexplained |
| SG RF AND XGB (5) | Singapore, log1p RF and XGBoost | Target rolling is correctly shifted; current external variables slip into features; exact input missing |
| HK RF AND XGB (4) | Hong Kong, log1p RF and XGBoost | Same external-variable selection flaw; copied Singapore labels |
| BKK SN (4) | Bangkok, seasonal naïve | Valid baseline calculation; four-month evaluation and unused training mask |
| HK SN (5) | Hong Kong, seasonal naïve | Valid baseline calculation; four-month evaluation and unused training mask |

Nine files do **not** form a complete city × model matrix. For example, there is no dedicated Singapore Ridge or Singapore seasonal-naïve notebook, and filenames beginning “RF” also fit XGBoost. The revised application already implements some combinations absent from the notebooks; it does not currently implement XGBoost.

## Confirmed findings and how to correct them

### F1 — Critical: current target is inside predictors

The two Ridge notebooks use `log_arrivals.rolling(3).mean()` and `.rolling(6).mean()` without shifting. The three YoY notebooks do the same on the current YoY target. A mean that includes y[t] is unavailable before y[t] has occurred. The outer train/test date split does not fix this leakage.

**Probe:** doubling one Bangkok current target changes its own three-month log rolling predictor by **0.231049**, equal to log(2)/3. A legitimate feature for forecasting that month should be invariant to this mutation.

**Correction:** use past-only rolling values, e.g. `log_y.shift(1).rolling(3).mean()`, and assert that changing y[t:] cannot alter X[t]. Do not patch only the evaluation code; training and inference must use the same feature builder.

### F2 — Critical: two Ridge notebooks compress the calendar

Those notebooks retain 2016–2019 and 2023–2024, then call `shift`. In the retained frame, January 2023's lag-1 is **December 2019**, and lag-12 is **January 2019**, not December 2022 and January 2022. Rolling windows cross the same artificial gap.

**Correction:** keep the continuous calendar while constructing lags. If excluding pandemic target rows is a deliberate experiment, apply a training-row mask *after* feature construction, document what lagged pandemic context is still used, and compare with a full-history specification on identical future windows.

This defect does **not** apply to the tree notebooks, which construct features before their training mask. Excluding some training years is not inherently leakage; the undocumented rationale and correct handling of time are separate issues.

### F3 — Critical: full-series winsorization allows test observations to influence training

All three YoY notebooks calculate 1st/99th-percentile cutoffs before splitting. Test-period observations can therefore alter clipped training targets and derived features. They also evaluate YoY predictions against a clipped test target, which changes the question being scored.

**Probe:** changing only Hong Kong's 2024 YoY values changes the global 99th percentile from **61,124.4242** to **1,000,000,000** and changes two earlier clipped values. The mutation is intentionally extreme to test information flow, not a realistic tourism scenario.

**Correction:** estimate any clipping thresholds strictly inside each origin's training data. Justify clipping an actual shock rather than treating it as an error. Evaluate in original arrival units against unmodified observations. If scoring a transformed/clipped target too, label that secondary objective explicitly.

### F4 — High: zero-denominator YoY growth and incomplete numerical checks

Bangkok's zero-arrival observations cause six infinite YoY values in April–September 2021. `dropna()` does not remove infinity. In the current diagnostic environment, the original 99th-percentile calculation returns NaN; the saved Bangkok notebook already contains an invalid-value warning. This does not prove its final estimator always receives infinity—the later masks may remove those rows—but it proves preprocessing is numerically ill-defined and version-sensitive.

**Correction:** define treatment for a zero prior-year baseline before computing growth. Prefer nonnegative level/log1p forecasting for shutdown/recovery data; if YoY is retained, explicitly handle undefined rates, assert all model arrays are finite, and report affected rows. Converting every undefined value to zero would invent “no growth.”

The inverse `lag12 * (1 + predicted_yoy/100)` is mathematically valid for an ordinary rate, but does not recover original actuals from clipped growth. It also permits negative arrivals for predictions below −100%, and very large levels when growth is extreme. These are risks requiring diagnostics and a documented treatment, not evidence that every current prediction is negative.

### F5 — High: intended lagged exogenous features are not the features actually selected

In the two log RF/XGBoost notebooks, `startswith(("log_lag", "log_roll", "m_", "hotel", "google"))` selects raw `hotel_occupancy` and `google_trends`, their current-month log transforms, **and** their lagged versions. Creating lagged columns does not remove the contemporaneous inputs.

**Probe:** the actual Hong Kong feature function selects all six external columns when enabled. Even `use_exogenous=False` leaves the two raw external columns selected. The flag does not actually disable external predictors.

The YoY notebooks explicitly select contemporaneous occupancy/trends growth too. This is a confirmed information-availability flaw for an advance forecast unless those inputs are genuinely available or forecast/scenario-supplied at the origin. It is not automatically wrong for a separately defined nowcast, but no such definition or release calendar is supplied.

**Correction:** use an explicit feature whitelist and test the disabled path. Document each external series' release lag. Either use available lags or build origin-valid forecasts/scenarios for the entire horizon, propagating their uncertainty. Current-year actual external variables must not masquerade as future-known values.

### F6 — High: a test-year feature matrix is not a fixed-origin annual forecast

ML notebooks construct the full series before splitting and predict all 2024 feature rows at once. Apart from F1/F5, later 2024 feature rows contain earlier 2024 actual arrivals. This can be defensible for **rolling one-step prediction**, if earlier arrivals were published and the model's fit/update policy is explicit. It is not the same as predicting January–December in December 2023.

**Correction:** choose and label the task. For an annual outlook, simulate recursive or direct multi-step forecasts with no within-horizon actual feedback. For rolling one-step evaluation, advance the origin and respect release delays. Report the two tasks separately instead of using one-step performance to support a multi-step product.

### F7 — High: Ridge tuning ignores time and preprocessing boundaries

`RidgeCV(cv=None)` uses efficient leave-one-out validation, not a forward-only temporal scheme. Future training observations can inform a nominally earlier validation point. The surrounding scaler is fitted once on all outer-training observations before RidgeCV's internal validation, so it is not refitted for those internal held-out points.

This is an **inner-selection** flaw; the scaler is not directly fitted on 2024 through that pipeline. That distinction matters. Independent chronological validation must own the *whole* preprocessing/model pipeline and match the intended horizon.

**Correction:** fit fresh pipelines at explicit rolling/expanding origins for each alpha, select with a predefined error measure, and evaluate a separate final window. The revised backend already follows this approach.

### F8 — High: comparisons use different test sets and no common selection rule

Seasonal naïve is scored over September–December 2024 (four observations); ML notebooks generally use January–December 2024 (12). Training periods and target definitions also differ. Good performance in the four-month subset cannot establish superiority over a whole-year model. A four-point R² is particularly fragile.

**Correction:** score all candidates against the same actuals, horizons, origins, and target units. Retain the four-month result only as a labelled supplementary slice. Define the selection rule before looking at the reporting holdout.

### F9 — Medium/high: reproducibility and validation gaps

- Both Singapore tree notebooks read `singapore_with_recovery_index.csv`, which is absent from the supplied project. The similarly named final CSV must not silently be treated as the exact original input.
- Other notebooks rely on absolute Downloads paths. They do not run from a clean checkout without path changes.
- Date parsing can silently coerce/drop records; no shared contract rejects duplicate/missing months or invalid targets.
- The log tree notebooks call unrestricted `dropna()` on the whole dataframe. Missing unused columns can change which training/test observations survive.
- No pinned notebook-specific XGBoost/matplotlib environment or input hashes accompany the experiments. Saved execution counts do not establish reproducibility.

**Correction:** provide named, versioned input contracts; explicit feature/target missingness rules; relative project paths; dependency declarations; and clean execution of all cells. Report excluded dates/counts, not just the min/max date.

### F10 — Medium: claims, metrics, and conclusions need evidence

- Bangkok Ridge calls its configuration “Best-for-metrics” and “Best Config” without a comparable selection experiment in the notebook. That wording is unsupported; it does not establish deliberate test-set tuning by the author.
- Hong Kong Ridge comments expect R² around 0.4–0.7 and MAPE around 4–6%, but its saved output is **R² −0.658 and MAPE 13.10%**. The interpretation must follow measured results, not expected targets.
- Hong Kong YoY saved arrival MAPEs of **560.99% (RF)** and **399.95% (XGBoost)** show severe failure, yet no residual/regime diagnosis explains why the experiment fails or whether it should be rejected. These are saved figures, not fresh results.
- Negative R² is **not a programming error**. A low percentage error and negative R² can coexist when actual variation is small; do not “repair” the metric to make it positive.
- Zero-denominator MAPE is unhandled in several notebooks; others silently remove undefined percentages without reporting a denominator count. Zero-pair sMAPE handling also changes the effective sample.
- Six hundred trees and a fixed seed are not inherently illogical. The missing evidence is a chronological benchmark/complexity argument, especially with about 45–48 supervised training rows. A seed does not establish robustness.
- No notebook supplies probabilistic intervals, a coverage assessment, or a clear account of model limitations. Point accuracy alone does not establish confidence.

**Correction:** separate hypothesis, procedure, result, and interpretation; include baseline comparisons, residual plots by time/regime/horizon, explicit metric definitions and denominators, and honest failure conclusions. Avoid unsupported causal explanations from predictive correlations.

## Notebook-by-notebook evidence and recommended edits

All references below mean **cell 1, one-based source lines**, not lines in the JSON encoding. Line-numbered source and saved text output are preserved in `notebook-source/` for review.

### 1. BANGKOK RIDGE LOG (5).ipynb

- **L57–71: F1/F2, critical.** Delete-before-shift and unshifted rolling means directly invalidate forecast features.
- **L97–108: F7, high.** Whole-pipeline chronological alpha validation is needed.
- **L85–89, L113: F6.** Declare whether 2024 is one-step or annual-origin evaluation.
- **L2 and L125: F10.** Replace “best” wording with a measured, predeclared comparison.
- **L15, L37–43, L62: F9.** Portable input path, strict date validation, and a documented zero-target transformation are needed.
- **Preserve:** arrival-unit evaluation, explicit outer-year split, use of a pipeline, and the Bangkok/Thailand proxy qualification at L1/L138. That qualification belongs in results and UI too.
- **Next edit:** common date-safe features, explicit origin/horizon, time-respecting alpha selection, baseline comparison, then a results/discussion section.

### 2. HONG KONG RIDGE LOG (4).ipynb

- **L55–68: F1/F2, critical.** Same leaked rolling means and compressed calendar.
- **L94–105: F7, high.** Same inner-validation/scaler issue.
- **L124/L127: F10.** Optimistic expectations disagree with the saved output.
- **L14: F9/data provenance.** “Filled” input needs documentation of which values were filled and whether future information was used upstream. Code inspection alone cannot certify this.
- **Preserve:** the explicit outer split and honest negative R² printout.
- **Next edit:** repair the same methodological core as Bangkok, then investigate Hong Kong's recovery regime without precommitting to a desired metric range.

### 3. RF BANGKOK (3).ipynb

- **L23–35: F1/F3, critical.** Full-series percentile fitting and current-target rolling means.
- **L17/L24/L45: F4, high.** Zero denominators produce infinities; NaN-only filtering is insufficient. The saved warning is consistent with the diagnostic.
- **L39: F5.** Current exogenous growth requires future-availability justification.
- **L51–52: F10.** Explain why recovery begins specifically in April 2023 and compare that choice without tuning on the final holdout.
- **L100–120: F4/F10.** Explain the transformed-target/original-level distinction and investigate negative R² rather than assuming growth reconstruction solves it.
- **Preserve:** it calculates lags on a complete calendar before masking, fits both tree models with seeds, and reports original arrival errors as well as growth errors.
- **Next edit:** prefer a log1p-level formulation as a baseline; retain YoY only as a separately justified, finite, train-preprocessed experiment.

### 4. RF SINGAPORE (4).ipynb

- **L23–35: F1/F3, critical.** Same rolling and percentile leakage.
- **L11: F9, high.** Exact required CSV absent. Do not claim reproduction with a substituted CSV.
- **L39/L75–76: F5/F6.** Same-month external inputs and within-test actual lag feedback prevent an unconditional annual-origin interpretation.
- **L97–120: F10.** Saved positive growth R² but negative arrival R² is not mathematically contradictory; explain that they score different transformed objectives.
- **Preserve:** complete-calendar lag construction and separate arrival-level evaluation.
- **Next edit:** establish the exact data version first, then fix features and use common-origin comparisons. The dataset filename's “recovery_index” is not evidence of an implemented recovery-index feature; no such field is selected here.

### 5. HK RF (3).ipynb

- **L23–35: F1/F3, critical.** Same direct leakage and global preprocessing.
- **L17, L39, L105–106: F4/F5.** Near-zero prior-year arrivals can amplify growth; current external inputs and inversion require diagnostics.
- **L61–120: F10.** The saved extreme level errors need an explicit failure analysis and rejection/limitation statement; a model producing numbers is not evidence it is usable.
- **Preserve:** complete-calendar features, random seeds, and retention of severe negative scores rather than hiding them.
- **Next edit:** inspect growth distribution by year, finite values, inverse-transformation sensitivity, and performance relative to a seasonal baseline. Avoid assuming that the Bangkok/Singapore formulation transfers successfully to Hong Kong.

### 6. SG RF AND XGB (5).ipynb

- **L29–31: valid.** Rolling target features are correctly shifted; do not report this notebook as having F1.
- **L38–43 plus L72: F5, high.** Prefix selection leaks current external variables into a purportedly lagged feature set; the disabled option is ineffective.
- **L13: F9, high.** Exact named input is absent.
- **L51–52: F9.** Whole-frame dropna can discard rows for irrelevant missing fields.
- **L75–94: F6/F10.** Clarify forecast information set and benchmark the fixed tree configurations chronologically.
- **Preserve:** continuous calendar, log1p/expm1 pairing, shifted target rolls, and monthly error table.
- **Next edit:** explicit whitelisted features with availability metadata, a tested no-exogenous mode, exact input provenance, and declared one-step versus multi-step evaluation.

### 7. HK RF AND XGB (4).ipynb

- **L29–31: valid.** Target rolling features are correctly shifted.
- **L38–43/L72: F5, high.** Confirmed current-column selection and ineffective exogenous switch, reproduced by extracting this exact function.
- **L51–52: F9.** Filter only required inputs and report dropped dates.
- **L2/L13: medium presentation risk.** The header says Singapore and the dataframe is named `df_sg` despite loading Hong Kong. The printed table title is Hong Kong; this is a copy/paste labelling defect, not proof the wrong data was loaded.
- **Preserve:** target transformation, feature calendar, and monthly output table.
- **Next edit:** repair feature selection, clean labels, investigate filled-data provenance, and use the same protocol as Singapore before comparing models.

### 8. BKK SN (4).ipynb

- **L23: valid.** Lag-12 on the monthly calendar is an appropriate seasonal baseline. No direct target leakage was found in this calculation.
- **L26–31: F8, high for comparison.** `train_mask` is unused; the evaluation covers only September–December. A fitted training regime is not implemented or needed by this deterministic baseline.
- **L2 versus L12/L41: medium.** Header says Hong Kong, but the loaded file and printed results are Bangkok. Correct the copied header.
- **L17/L40/L55–60: F9/F10.** Validate finite actuals and lag availability; define zero-denominator behavior before integer conversion/percentage calculation.
- **Preserve:** simple, interpretable baseline and explicit monthly table.
- **Next edit:** run the same baseline over all common forecast windows, explain the forecast rule and its recovery limitation, and preserve the four-month slice only as supplementary evidence.

### 9. HK SN (5).ipynb

- **L23: valid.** Correct calendar-based seasonal-naïve prediction, with no direct target leakage found.
- **L26–31: F8.** Same unused training mask and four-month evaluation inconsistency.
- **L12: data limitation.** Undocumented upstream filling remains unresolved even when the model itself is simple.
- **L40/L55–60: F9/F10.** Same input/metric edge-case handling needs improvement.
- **Preserve:** the baseline rule and transparent monthly output.
- **Next edit:** evaluate on identical horizons/dates as ML, explain why prior-year recovery may underpredict, and quantify that from results rather than asserting a causal recovery story.

## Defensible rewrite order

1. **Define the forecasting contract:** origin, horizon, data publication lags, geography, and level target. Resolve missing Singapore inputs and upstream filling before claiming exact reproduction.
2. **Establish common data/features/splits:** keep monthly continuity; separate input checking, feature creation, estimator fitting, forecast simulation, and scoring. Keep baseline and ML test windows identical.
3. **Correct F1–F7 with targeted assertions:** current/future target mutation, calendar-source checks, fold-local thresholds/scaling, exogenous whitelist/disabled mode, and no within-horizon actual feedback.
4. **Run compact chronological comparisons:** fixed small search, explicit selection metric, final window excluded from selection. Include both simple baselines; do not choose the “best” model using the reporting year.
5. **Write reasoning around results:** hypotheses, transformations, sample sizes, residual/regime failures, uncertainty limitations, and interpretation of negative scores. Keep failed experiments as clearly labelled research evidence.
6. **Only then update deployment models:** migrate validated changes, regenerate artifacts, verify consistency between notebook and deployed inference, and rerun regression tests. This audit/UI session does not change model scores or add unverified XGBoost outputs.

## Evidence and reproducibility

- [Diagnostic measurements](notebook-audit-evidence.json)
- [Reproducible diagnostic script](../scripts/audit_notebooks.py): run `python scripts/audit_notebooks.py` from the project root. It does not fit models or alter notebooks.
- [Original preservation inventory](source-inventory.json)
- [Existing deployed methodology](METHODOLOGY.md)

The diagnostic script isolates the actual feature function and key operations, rather than executing every original notebook. The observations above do not certify upstream data collection or reproduce historical XGBoost/library behavior. All source findings are tied to the archived files; the originals remain available for a future audited rewrite.
