# Sentinel-VA Norfolk Pilot: Findings and Results

**Report status:** Final pilot results

**Release run:** `norfolk-pilot-20260713-release-v7`

**Classification:** **Conditionally feasible; exploratory ranking**

**Study area:** Norfolk, Virginia
**Study period:** January 1, 2016–December 31, 2025

> **Decision-use boundary:** This report is a transparent, historical prioritization aid. It is not a camera-deployment recommendation, legal eligibility determination, causal analysis, prediction of future crashes, or crash-rate estimate. Any operational decision would require separate traffic-engineering, legal, community, equity, procurement, and privacy review.

## Executive Summary / TL;DR

Sentinel-VA tested whether public data can produce a transparent and reproducible way to identify **Norfolk areas that warrant further traffic-safety review**. The pilot combined ten years of historical crash records with pedestrian and bicycle involvement, time-pattern concentration, and proximity to reported K–12 schools.

The bottom line is mixed but useful:

- **The data pipeline and its audit trail are reliable.** It processed 41,714 eligible crash records into 1,609 analytic cells, assigned every eligible record, and reproduced identical row-level scores on rerun.
- **The individual scores are explainable.** Every published cell shows the evidence and weighted contribution behind its index.
- **The exact ranking is not stable enough for operational selection.** Both pre-registered stability checks failed: rankings changed materially across time periods and when the analytic grid size changed.
- **Therefore, the pilot is conditionally feasible, not deployment-ready.** Its output can guide exploratory investigation and data-improvement work, but it must not be treated as a definitive shortlist of camera sites or intersections.

The highest-scoring analytic cell was near **3900 Hampton Boulevard**, with an index of **89.69 / 100**. Its score reflects high historical crash burden, pedestrian-related crashes, time concentration, and proximity to Madison Alternative Center. This identifies a location for further study—not a decision to install anything there.

## Context & Methodology

### Purpose

Traffic-safety decisions often begin after a serious incident or sustained public concern. Sentinel-VA asks a narrower, earlier question: *can public historical data highlight places that deserve a closer engineering and community review before a decision is made?*

The Norfolk pilot uses a **250 m fixed grid** rather than named intersections. Public crash coordinates are available, but an authoritative intersection topology was not. Each grid cell is therefore an analytic container for consistently aggregating evidence; it is **not** a legal school zone, roadway-engineering unit, or recommended installation location.

### How the results were gathered

1. **Acquire and preserve source snapshots.** Crash data, NCES school-location data, the Norfolk boundary, and a traffic-volume extract were registered with provenance and checksums.
2. **Validate and clean the data.** The pipeline removed records outside the approved Norfolk boundary and retained an exclusion ledger. It classified reported school facilities and preserved an audit record for excluded or ambiguous school rows.
3. **Aggregate evidence into grid cells.** Each eligible crash was assigned to one 250 m cell. Per-cell features summarized crash burden, vulnerable-road-user evidence, time concentration, and nearest-school distance.
4. **Calculate an explainable index.** The four components were percentile-normalized and combined with fixed, pre-registered weights. The specification was frozen before inspecting ranks.
5. **Validate before release.** The pilot checked deterministic reproducibility, sampled lineage, temporal stability, and sensitivity to changing the grid size.

For the full operating procedure, see [the pilot procedure](../pilot%20study/Procedure.md) and [the execution framework](../pilot%20study/execution.md). The machine-readable score specification is retained in the release archive at `outputs/runs/norfolk-pilot-20260713-release-v7/phase4/score_specification.json`.

### Inputs and treatment

| Input | Use in the pilot | Important limitation |
|---|---|---|
| Norfolk historical crash records | Core historical-safety evidence | Historical crashes are not violations, future-risk predictions, or causal evidence. |
| NCES 2023–24 public and private school locations | Distance-to-reported-school component | Points identify reported facilities, not attendance boundaries, legal school zones, or current operating certification. |
| U.S. Census TIGERweb Norfolk boundary (`GEOID 51710`) | Geographic validation and inclusion | A governmental boundary, not a roadway or school-zone boundary. |
| VDOT ADT traffic-volume export | Evaluated for exposure adjustment | Transfer-limited and incomplete for Norfolk; **excluded from scoring**. |

## Key Findings & Results

### Dataset and output summary

| Measure | Result | What it means |
|---|---:|---|
| Source crash rows | 42,004 | Historical crash records examined for the study period. |
| Eligible crash records | 41,714 | Records retained inside the approved Norfolk boundary. |
| Excluded crash records | 290 | Records outside the approved boundary; the reconciliation difference was zero. |
| Reported K–12 facilities | 74 | NCES public and private school points retained for proximity analysis. |
| Candidate 250 m cells | 1,609 | Analytic locations with published feature and score records. |
| Crash assignment rate | 100% | All eligible crash records were assigned to a cell. |
| Published index range | 21.62–89.69 | Relative index values on a 0–100 scale; not probabilities or rates. |
| Exposure adjustment | Not applied | The traffic-volume source was incomplete; its score weight was 0%. |

### What drove the index

| Component | Weight | Plain-language meaning |
|---|---:|---|
| Historical burden | 40% | More crashes and more severe outcomes increase the relative priority. |
| Vulnerable-road-user evidence | 25% | Pedestrian and bicycle crash evidence receives additional emphasis. |
| Time concentration | 15% | Repeated concentration in particular hour and weekday groups increases the score. |
| School proximity | 20% | Cells closer to a reported K–12 facility receive more weight. |
| Traffic exposure | 0% | Omitted because a complete, trustworthy denominator was unavailable. |

### Top ten analytic cells

These are **analytic grid cells**, summarized by their dominant route name. They are investigative starting points only. The complete, explainable ranking is retained in the release archive at `outputs/runs/norfolk-pilot-20260713-release-v7/phase4/ranked_locations.csv`.

| Rank | Analytic cell / dominant route | Index | Crashes | Vulnerable-road-user crashes | Nearest reported school (distance) |
|---:|---|---:|---:|---:|---|
| 1 | `grid250_1535_16329` / 3900 Hampton Blvd | 89.69 | 170 | 4 | Madison Alternative Center (134 m) |
| 2 | `grid250_1536_16323` / 1100 Hampton Blvd | 86.57 | 146 | 4 | West Ghent School (264 m) |
| 3 | `grid250_1553_16345` / 700 E Little Creek Rd | 85.48 | 134 | 5 | Crossroads PreK-8 School (220 m) |
| 4 | `grid250_1541_16316` / 400 Saint Pauls Blvd | 85.16 | 94 | 4 | First Baptist Ready Academy Christian School (251 m) |
| 5 | `grid250_1547_16323` / 2500 Tidewater Dr | 84.96 | 101 | 5 | Lindenwood Elementary (243 m) |
| 6 | `grid250_1535_16328` / 2700 Hampton Blvd | 84.78 | 87 | 13 | Norfolk Alternative High (115 m) |
| 7 | `grid250_1544_16316` / 700 Tidewater Dr | 84.47 | 163 | 4 | Tidewater Park Elementary (69 m) |
| 8 | `grid250_1553_16313` / Interstate 264 East | 84.26 | 181 | 3 | Chesterfield Elementary (64 m) |
| 9 | `grid250_1539_16324` / 2000 Colonial Ave | 84.25 | 83 | 5 | Bina High School (255 m) |
| 10 | `grid250_1546_16343` / 7400 Granby St | 83.96 | 60 | 5 | Norfolk Collegiate School (105 m) |

### Validation results

| Gate | Pre-registered standard | Observed result | Outcome |
|---|---|---|---|
| Deterministic rerun | Identical score output | Identical row-level values; ranked-output SHA-256 recorded | **Pass** |
| Stratified lineage audit | ≥98% agreement and Wilson 95% lower bound ≥90% | 100 / 100 records correct; 100% agreement; lower bound 96.3% | **Pass** |
| Temporal stability | Adjacent-period Spearman correlation ≥0.70 | 0.573 (2016–18 vs. 2019–21); 0.562 (2019–21 vs. 2022–25) | **Fail** |
| Grid sensitivity | Top-10 Jaccard overlap ≥0.60 | 0.250 at 200 m; 0.176 at 300 m | **Fail** |

**Interpretation:** The pipeline reliably produces the same answer from the same inputs, and its record-to-cell lineage audit passed. But the answer changes too much when the time period or grid granularity changes. Those failed stability gates drive the final **conditionally feasible; exploratory** classification.

## Deep Dive / Technical Analysis

### Data quality and spatial construction

The study used the U.S. Census Bureau’s 2025 Norfolk city boundary (`GEOID 51710`) with a `covers` inclusion predicate. Of 42,004 input crash records, 41,714 were retained and 290 were excluded; retained plus excluded exactly reconciled to the input count. Date parsing had no failures in the baseline source check. All 41,714 retained records were assigned to one of 1,609 250 m cells, for an assignment rate of 1.000 against a required threshold of 0.995.

School inputs were classified into primary K–12 and audit-only records. Of 79 source school rows, 74 reported K–12 facilities were retained; five audit rows represented records outside the primary K–12 set. Duplicate school names were retained as distinct locations when coordinates differed, with the adjudication recorded in the duplicate-name ledger.

### Score construction

For each cell \(i\), the published priority index is:

\[
\text{Priority Index}_i = 40P(B_i) + 25P(V_i) + 15P(T_i) + 20P(S_i)
\]

where \(P(\cdot)\) is the empirical percentile rank with average ranks for ties. The components are:

| Symbol | Raw formulation |
|---|---|
| \(B\): historical burden | `crash_count + 10 × fatalities + 5 × suspected_serious_injuries + people_injured` |
| \(V\): vulnerable-road-user evidence | `4 × pedestrian_involved_crashes + 3 × bicycle_involved_crashes + 10 × pedestrian_fatalities + 2 × pedestrians_injured` |
| \(T\): time concentration | `0.5 × hour_bin_concentration + 0.5 × weekday_concentration` |
| \(S\): school proximity | `exp(-nearest_school_distance_m / 500)` |

The traffic-exposure term is explicitly disabled (`weight = 0`) because the available ADT export exceeded its transfer limit. This prevents an incomplete traffic-volume file from being mistaken for a valid crash-rate denominator.

The score specification was frozen before rank inspection. Ties resolve deterministically by descending index, then descending crash count, then ascending `location_id`. Component contributions reconciled to the published score with a maximum absolute difference of approximately `1.0e-10`; all 1,609 rows, including the top 10, have a non-empty explanation.

### Stability and sensitivity evidence

Temporal validation compared adjacent blocks using Spearman rank correlation for cells meeting the minimum event requirement. Both comparisons were statistically non-zero but materially below the practical stability threshold:

| Comparison | Cells compared | Spearman \(\rho\) | 95% bootstrap CI | Top-10 Jaccard | Gate |
|---|---:|---:|---:|---:|---|
| 2016–2018 vs. 2019–2021 | 525 | 0.573 | 0.512–0.631 | 0.250 | Fail |
| 2019–2021 vs. 2022–2025 | 571 | 0.562 | 0.497–0.621 | 0.250 | Fail |

Spatial sensitivity reran the frozen score logic on alternative grids, mapped each alternative-grid top-10 centroid back to the primary 250 m grid, and compared unique primary IDs. The observed top-10 overlap was 0.250 for the 200 m grid and 0.176 for the 300 m grid, compared with the required minimum of 0.600. This is direct evidence of the **modifiable areal unit problem**: the precise top-ten ordering depends on how the city is partitioned.

Leave-one-year-out analysis was more reassuring at the full-ranking level: Spearman correlations ranged from 0.985 to 0.990. However, this does not override the failed adjacent-period and grid-sensitivity gates, especially for a use case focused on a small top-ranked subset.

### Reproducibility and auditability

- The rerun produced identical row-level score values.
- The final ranked output SHA-256 is `3cc53654920215c68af7a91ef9ece2a7e4f00def852476c078d0abf901feb17e`.
- The source-feature SHA-256 is `7d043d6ca7774d6dfafe6b64cf86a6de2df90d7a85bbad174a5879343eec688a`.
- The lineage audit sampled 100 stratified records across spatial quadrants and years; every assignment and aggregate recount passed. The audit did not include an independent second reviewer.
- The release run retains source and output hashes, phase handoffs, quality reports, validation tables, and release metadata at `outputs/runs/norfolk-pilot-20260713-release-v7/`.

### Edge cases and limitations

- **No exposure adjustment:** Results measure a historical priority index, not risk per vehicle-mile, because a complete traffic-volume denominator was unavailable.
- **Grid cells are proxies:** A high-ranked cell can include multiple road features; it should not be relabeled as a specific intersection without geospatial and engineering verification.
- **School points are not school zones:** Proximity to an NCES facility is only one contextual signal and does not establish legal eligibility.
- **Historical association is not causation:** The model does not show that any intervention will reduce crashes or violations.
- **Stability failures matter:** The ranking cannot reliably support a precise, operational top-ten selection in its current form.
- **Geographic scope is limited:** The Norfolk pilot must not be generalized to Virginia without comparable statewide source coverage and a new validation cycle.

## Next Steps / Recommendations

1. **Use the output only to prioritize further investigation.** Treat high-index cells as candidates for site visits, roadway-geometry review, local crash-diagram analysis, and community input—not as deployment decisions.
2. **Acquire a complete, locality-filtered traffic-exposure dataset.** Validate coverage and temporal alignment before enabling an exposure-adjusted component; then rerun the full validation protocol.
3. **Improve the spatial unit.** Test an authoritative intersection/road-segment network or carefully defined corridor units. Pre-register the unit choice and reassess grid/geometry sensitivity before publishing a shortlist.
4. **Strengthen temporal validation.** Investigate recency weighting, minimum-event thresholds, or a longer/cleaner period while keeping the validation plan frozen before reviewing ranks.
5. **Add independent review.** Have a second reviewer repeat the lineage audit and conduct blinded technical and traffic-safety plausibility checks.
6. **Keep the release guardrails in place.** Continue displaying the conditional classification, component explanations, source limitations, and downloadable evidence alongside all rankings.
7. **Do not expand statewide yet.** First demonstrate a stable Norfolk method; only then apply the same data-provenance, exposure, and validation standards to other localities.

## Evidence Index

| Artifact | Purpose |
|---|---|
| [Pilot overview](../pilot%20study/Readme.md) | Concise final status, safeguards, and limitations. |
| `outputs/runs/norfolk-pilot-20260713-release-v7/phase4/ranked_locations.csv` | Complete per-cell score, components, explanations, and metadata. |
| `outputs/runs/norfolk-pilot-20260713-release-v7/phase4/score_specification.json` | Frozen weights, formulas, tie-breaks, and validation thresholds. |
| `outputs/runs/norfolk-pilot-20260713-release-v7/phase5/temporal_validation.csv` | Adjacent-period rank-stability results. |
| `outputs/runs/norfolk-pilot-20260713-release-v7/phase5/sensitivity_analysis.csv` | Grid and temporal sensitivity evidence. |
| `outputs/runs/norfolk-pilot-20260713-release-v7/phase5/validation_report.json` | Final gate decisions and pilot classification. |
| `outputs/runs/norfolk-pilot-20260713-release-v7/phase5/reproducibility_report.json` | Deterministic rerun and output hashes. |
