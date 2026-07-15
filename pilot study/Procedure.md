# Sentinel-VA Norfolk Pilot: Scientific Execution Procedure

**Document status:** Pre-registered execution framework; no analysis results are reported here  
**Study type:** Retrospective, observational, batch geospatial feasibility study  
**Study boundary:** City of Norfolk, Virginia  
**System under evaluation:** Sentinel-VA public-data pipeline for transparent traffic-safety location prioritization  
**Version:** 1.0 — July 12, 2026

## 0. Purpose, Authority, and Non-Claims

This procedure governs the Norfolk pilot of Sentinel-VA. It converts the project's documented feasibility question into reproducible, auditable operating controls. The pilot evaluates whether the available public or already-acquired data can be ingested, validated, joined, aggregated, scored, explained, and visualized without hidden data-quality, provenance, or methodological defects.

The pilot produces a **historical, explainable prioritization aid**. It does not predict an individual future crash; establish legal school-zone status; determine statutory camera eligibility; authorize a camera deployment; replace traffic engineering, legal review, procurement, or community engagement; process live video; or use vendor, citation, paid-mobility, or other proprietary data.

All thresholds below are pre-execution acceptance criteria. They are operational decision rules for this pilot, not claims about observed performance or statutory requirements. A criterion may be tightened following documented review, but may not be relaxed after inspection of ranked results without a versioned protocol amendment and a full rerun from immutable inputs.

## 1. Methodological Framework & Scope Delimitation

### 1.1 Study design and unit of analysis

The design is a retrospective observational analysis of Norfolk crash records dated from 2016-01-01 through 2025-12-31, supplemented by a validated active K–12 school-location layer. The candidate location unit is deliberately unresolved at protocol issue. Before scoring, the study lead shall select exactly one reproducible unit:

1. named or derived intersections;
2. roadway segments/corridors;
3. fixed spatial grid cells; or
4. deterministic spatial crash clusters.

The selection must be recorded in the run manifest with its algorithm, geographic coordinate reference system (CRS), spatial tolerance or grid resolution, rationale, expected failure modes, and a sensitivity analysis. The same location definition, study window, input snapshots, and scoring specification shall apply to every candidate location in a run.

### 1.2 Hypothesis formalization

#### Primary feasibility hypothesis (H1)

**H1:** Given the documented Norfolk inputs, a deterministic public-data pipeline can generate a complete candidate-location table and an explainable historical prioritization score for every eligible location unit, with all input provenance, transformations, exclusions, factor contributions, and output hashes reproducibly recoverable from the run manifest.

The null hypothesis, **H0**, is that one or more required inputs, joins, location definitions, quality controls, or provenance controls cannot support such a reproducible and explainable output within the pilot boundary.

#### Secondary hypotheses

| ID | Hypothesis | Decision evidence |
|---|---|---|
| H2 | A validated active K–12 facility layer can be joined to the chosen location unit without treating third-party POIs as legal school-zone polygons. | Documented classification, open/closed handling, duplicate-coordinate adjudication, CRS validation, and nearest-facility distance audit. |
| H3 | Historical crash burden, crash harm, pedestrian/bicycle involvement, temporal concentration, and school-facility proximity can be expressed as separately inspectable features rather than a black-box score. | Per-location feature table; normalized components; weights or model explanation; no unexplained aggregate. |
| H4 | The ranking is temporally stable enough to justify feasibility, rather than being driven solely by one anomalous period. | Pre-specified rolling or blocked temporal validation and rank-stability thresholds. |
| H5 | The methodology is portable in design, while the conclusions remain Norfolk-specific until comparable source coverage is independently verified elsewhere. | Parameterized configuration; locality-specific source manifest; no statewide extrapolation from Norfolk performance alone. |

### 1.3 Scope boundary matrix

| Dimension | Norfolk pilot: included | Norfolk pilot: excluded / constrained | Eventual statewide implementation |
|---|---|---|---|
| Geography | City of Norfolk only. | No inference about unobserved Virginia localities. | Virginia localities only where comparable, licensed inputs are available. |
| Time | Crash records spanning 2016–2025, subject to parsing and validation. | No real-time or post-cutoff inference. | Locality-specific historical windows must be declared and harmonized. |
| Crash data | 42,004 documented unique crash records with coordinates, datetime, injury, roadway, and involvement fields. | No unsupported imputation of absent records; no claim of causal effect. | Comparable public crash records with usable coordinates and timestamps. |
| School data | Active K–12 facilities after validation; proximity as a facility-distance feature. | Closed sites excluded from primary feature; preschool/childcare handled explicitly; no legal zone determination. | Official or validated school directory and, where available, verified school-zone geometry. |
| Exposure | ADT may be used only after a complete Norfolk-filtered, paginated extract passes verification. | Current ADT file is transfer-limited; it cannot support a complete denominator. | Comparable complete exposure data preferred; otherwise publish hotspot index only. |
| Scoring | Transparent weighted score, or a model with pre-declared interpretable feature contributions. | No opaque model; no site recommendation for enforcement. | Same explainability contract, recalibrated only with documented evidence. |
| Outputs | Auditable feature table, ranked Norfolk locations, limitations, and map if gates pass. | No camera placement, citation, vendor, or legal output. | Locality-aware ranking and map with coverage limitations disclosed. |
| Data sources | Free public sources or acquired files with recorded provenance and licensing. | No paid, proprietary, vendor, field-survey, or live-camera data. | Same source policy unless a separately approved policy changes it. |

### 1.4 Inclusion and exclusion criteria

#### Crash-record inclusion

A crash record is eligible when all of the following are true:

1. its document number is non-null and unique after duplicate resolution;
2. its parsed event datetime lies within 2016-01-01 00:00 through 2025-12-31 23:59 local time;
3. latitude and longitude are finite, fall inside the declared Norfolk analysis boundary or an approved boundary buffer, and use the declared geographic CRS;
4. the record can be assigned deterministically to the selected location unit; and
5. required analytic fields are present or the record's exclusion from a particular feature is explicitly logged.

Records are excluded only for a documented reason code: duplicate document number, invalid/unparseable datetime, invalid coordinate, outside-boundary coordinate, unresolved location assignment, or schema violation. Source records remain immutable; exclusion creates a derived audit table and never deletes the original row.

#### School-facility inclusion

The primary school-proximity layer shall include a record only if it is marked `open`, lies in Norfolk, has a valid coordinate, and is classified as elementary, middle, high, or K–12. Preschool and kindergarten-only records shall be retained in a separate audit layer and are excluded from the primary K–12 feature unless the protocol is amended before scoring. Closed facilities are retained for historical context but excluded from primary proximity calculations. Repeated names at different coordinates, including the documented James Blair Middle School and Little Creek Elementary School records, shall be retained as separate candidate campuses until validation establishes a legacy, duplicate, or inactive record.

#### Location-unit inclusion

The study shall not silently substitute a named intersection for a spatial cluster, or vice versa. A candidate location is included only if it is generated by the frozen location algorithm and has sufficient attribution to report its geometry, source records, and feature values. Locations with suppressed counts for privacy or unstable denominators remain in the feature table but are marked as non-rankable rather than removed without trace.

### 1.5 Confounding variables and mitigation register

| Class | Potential confounder or bias | Threat to inference | Required mitigation / disclosure |
|---|---|---|---|
| Environmental | Weather, lighting, roadway surface, seasonal travel, work zones, special events. | May elevate historical crash counts without representing persistent location risk. | Preserve available contextual fields; stratify or sensitivity-test where data support it; state residual confounding. |
| Exposure | Traffic, pedestrian, bicycle, and school-arrival volumes vary by site and year. | Raw counts can mistake volume for risk. | Do not report rates without complete verified ADT; label the output a hotspot index when exposure is incomplete. |
| Temporal | Reporting practices, roadway construction, school openings/closures, pandemic-era travel shifts, and recency effects. | Historic patterns may not represent current conditions. | Report annual counts; use blocked temporal validation; test exclusion of anomalous years; stamp data cutoff. |
| Spatial | Coordinate precision, geocoding drift, long road segments, boundary-edge assignment, and modifiable areal unit effects. | Assignment can move a crash between candidate locations. | Freeze CRS and tolerance; spatially audit samples; perform tolerance/grid sensitivity analysis; report ambiguous assignments. |
| Technical | Schema drift, parsing errors, truncated ADT extraction, library-version drift, rounding, and nondeterministic clustering. | Produces irreproducible results or false precision. | Schema contracts, checksums, version lockfile, deterministic seeds, transfer-limit check, and rerun comparison. |
| Human | Manual school classification, duplicate adjudication, threshold tuning after results, and spreadsheet edits. | Introduces selection or confirmation bias. | Dual review for manual decisions; reason-coded decisions; append-only logs; pre-register configuration before ranking. |
| Measurement | Crash data are not violation data; school POIs are not school-zone polygons. | Score may be interpreted as legal eligibility or violation propensity. | Separate these concepts in all outputs; retain explicit limitation banners. |

### 1.6 Analytic specification and change control

Before T-Zero, create and hash a `run_manifest` that declares: input filenames and SHA-256 hashes; source owner and acquisition date; schema versions; CRS; Norfolk boundary source; location algorithm; school classification map; time window; missing-data handling; score method; transformations; weight values or model hyperparameters; random seed; software versions; and output paths.

The default scoring approach for this feasibility pilot is a transparent weighted index:

```text
PriorityIndex(location) =
    w_b × normalized(historical crash burden and harm)
  + w_v × normalized(vulnerable-road-user involvement)
  + w_t × normalized(temporal concentration)
  + w_s × normalized(active K–12 facility proximity)
  [+ w_e × normalized(exposure-adjusted burden), only if ADT gate passes]
```

The weights must sum to 1.0 and be frozen before examination of ranked outputs. If an interpretable tree-based model is used instead, the protocol must specify training/validation splits, target definition, calibration method, feature-importance method, monotonicity constraints if any, and the same per-location explanation requirement. No model may be selected solely because it produces a preferred ranking.

## 2. Statistical Validity & Scientific Rigor

### 2.1 Baseline establishment

The control baseline is not a non-treated population; no intervention occurs in this study. It is a frozen, descriptive reference distribution against which pipeline completeness, scoring stability, and input drift are evaluated. Baseline artifacts must include:

| Baseline domain | Required measures | Acceptance rule |
|---|---|---|
| Source inventory | Row count, unique document count, file size, SHA-256, acquisition timestamp, owner/licence status. | Must reconcile to the source snapshot and manifest; unexplained differences are blocking. |
| Crash completeness | Counts by year, severity, fatality, serious injury, pedestrian, bicycle, intersection type, and missingness per required field. | Core-field missingness must be 0% where current inventory claims none; any deviation is investigated and disclosed. |
| Spatial validity | Coordinate ranges, Norfolk-boundary inclusion rate, duplicate coordinate rate, assignment failure rate, sample map. | 100% of included records are within the approved boundary/buffer; unresolved assignment must be 0% for ranked records. |
| Temporal validity | Minimum/maximum timestamp; monthly and hourly distribution; parse-failure count. | 0 unlogged parse failures; all exclusion reasons are countable and reproducible. |
| School layer | Raw/open/closed counts, classification counts, coordinate validity, duplicate-name/coordinate review, nearest-distance distribution. | 100% of primary-feature records meet inclusion criteria and have provenance status recorded. |
| ADT | Feature count, jurisdiction coverage, geographic coverage, `exceededTransferLimit`, and temporal currency. | Exposure gate passes only if transfer limit is false and Norfolk coverage is demonstrated; otherwise omit `w_e`. |
| Pipeline health | Runtime, memory, input/output hashes, dependency versions, warning/error count. | Zero unhandled exceptions; zero silent row loss; outputs hash-identical on an unchanged rerun. |

The baseline must be generated before any score, rank, top-N list, or map legend is reviewed. It becomes the reference used for subsequent drift detection.

### 2.2 Sampling, representativeness, and selection-bias control

The analytic cohort is a census of all eligible crash records in the declared Norfolk time window, not a convenience sample. The principal risks are therefore not sampling error from random selection but coverage and processing bias. Controls are:

1. **Boundary census.** Use a documented Norfolk boundary and report both raw coordinate inclusion and exclusions at the boundary.
2. **No outcome-driven filtering.** Do not select records, years, road classes, or locations after inspecting their score or rank.
3. **Stratified quality audit.** Randomly sample records for manual verification from each year, severity class, pedestrian/bicycle status, and selected location unit. A minimum of 5 records per non-empty stratum, capped at 100 total records, shall be audited. If a stratum contains fewer than 5 records, audit all of it. The sampling seed and row identifiers must be recorded.
4. **Geographic audit.** Review a spatially dispersed sample across city quadrants or an equivalent deterministic tessellation, preventing inspection from concentrating on known hotspots.
5. **School adjudication review.** Manual classifications and duplicate-campus decisions require a second reviewer where available; if only one reviewer is available, decisions require dated evidence and an unresolved-status flag.
6. **Representativeness statement.** Results represent only the recorded crashes and validated facilities in Norfolk during the specified historical period. They do not represent unreported crashes, violations, current exposure, or statewide conditions.

### 2.3 Success metrics, inferential tests, and decision thresholds

This is primarily an engineering-feasibility study; a p-value cannot establish that a location is suitable for enforcement. Statistical tests evaluate stability and data association, while operational criteria determine whether the pilot pipeline is valid enough to proceed.

| Dimension | Metric | Pre-registered success threshold | Failure disposition |
|---|---|---|---|
| Provenance | Manifest coverage of analytic inputs and outputs. | 100% have SHA-256, source, acquisition date, and licence/provenance status. | Block release; reconcile or exclude the affected input. |
| Reproducibility | Exact rerun with identical inputs/configuration. | Identical output hashes, or a documented deterministic serialization exception with identical row-level values. | Stop; resolve nondeterminism. |
| Data retention | Input rows represented in retained/excluded reconciliation table. | 100% reconciled; zero silent loss. | Stop; repair pipeline and rerun. |
| Location assignment | Eligible crash records assigned to a rankable location. | ≥99.5%; all remainder reason-coded. | Investigate; if below threshold, do not rank until location method improves. |
| School feature validity | Primary K–12 feature records satisfying all inclusion checks. | 100%; all excluded POIs retained in audit table. | Exclude school feature or halt scoring. |
| ADT validity | Complete Norfolk exposure layer. | `exceededTransferLimit=false`, documented Norfolk coverage, and 100% of used segments traceable. | Omit exposure factor; do not report rates. |
| Manual audit | Correctness of audited row-to-feature mapping. | ≥98% agreement; two-sided 95% Wilson confidence interval lower bound ≥90%. | Correct defect; expand audit and rerun affected stages. |
| Temporal stability | Spearman rank correlation between adjacent blocked periods for locations with adequate history. | ρ ≥ 0.70 with two-sided p < 0.05; report 95% bootstrap CI. | Label results exploratory; review feature design before claiming stable prioritization. |
| Sensitivity | Top-10 overlap after pre-specified, reasonable spatial tolerance or normalization alternatives. | Jaccard overlap ≥0.60 and no unexplainable rank reversal attributable to a defect. | Publish sensitivity limitation or redesign location rule. |
| Explainability | Ranked locations with component values and plain-language explanation. | 100% of top-10; 100% of published rows have machine-readable components. | No publication until repaired. |

Where hypothesis tests are run, use two-sided tests with α = 0.05 and report effect size plus 95% confidence interval (CI), not p-value alone. Multiple related exploratory comparisons must control false discovery rate using Benjamini–Hochberg at q = 0.05, or be explicitly labeled descriptive. Absence of statistical significance is not evidence of safety; it is evidence that the proposed comparison did not meet the stated evidentiary threshold.

### 2.4 Temporal validation protocol

1. Freeze the scoring method before validation.
2. Partition the 2016–2025 window into non-overlapping chronological blocks, normally 2016–2018, 2019–2021, and 2022–2025; record any adjustment caused by sparse strata.
3. Compute features and scores independently in each block without using future-block information.
4. Compare adjacent-block rankings on locations meeting an a priori minimum event-count criterion. The criterion must be stated before results inspection and must not be set below 5 qualifying crash records per location per compared block unless sparse-count analysis is separately justified.
5. Calculate Spearman ρ, bootstrap its 95% CI by resampling locations, and calculate top-10 Jaccard overlap.
6. Perform a leave-one-year-out sensitivity analysis and a documented pandemic-era sensitivity analysis. Neither may overwrite the primary result.
7. Retain all block-level feature and rank tables; do not retain only the preferred period.

### 2.5 Data integrity, cryptographic verification, and provenance

The pipeline shall use an append-only evidence model. Immutable raw source files are never edited in place. Every derived table must retain `run_id`, input-hash references, transformation version, creation time, row count, and output SHA-256.

```text
raw source snapshot
  -> SHA-256 manifest + schema validation
  -> immutable staging copy
  -> cleaning/exclusion ledger
  -> geospatial assignment + feature tables
  -> score/rank/map artifacts
  -> SHA-256 output manifest + signed/dated audit log
```

Minimum controls:

- Store raw, staged, derived, and exported artifacts in separate paths; write derived data atomically to a temporary path, validate it, hash it, then promote it.
- Emit structured logs in UTC with monotonic event sequence, `run_id`, command/version, input/output row counts, warning/error class, and hash references. Log both success and failure paths.
- At each stage, reconcile input rows = retained rows + excluded rows, with exclusion reason counts. The expected reconciliation difference is zero.
- Validate CSV/GeoJSON schema, primary-key uniqueness, data types, coordinate ranges, datetime parsing, CRS, geometry validity, and categorical domains before downstream use.
- Verify source hashes immediately after acquisition and immediately before execution. A changed source requires a new `run_id`; do not overwrite a prior run.
- Maintain two independent copies of raw inputs and manifests: the working copy and a read-only archive/checksum copy. This is the pilot's N+1 data-preservation control.
- Generate a machine-readable provenance file and a human-readable data dictionary alongside each export. Hash the map HTML, ranked CSV, feature table, configuration, log, and manifest as one release bundle.

Illustrative verification commands (adapt paths to the implemented repository structure):

```powershell
Get-FileHash -Algorithm SHA256 "data/Norfolk/Traffic_Crashes.csv"
Get-FileHash -Algorithm SHA256 "data/Norfolk/School_information.csv"
Get-FileHash -Algorithm SHA256 "data/Norfolk/MiddleandHighschool_information.csv"
Get-FileHash -Algorithm SHA256 "data/Norfolk/Traffic Volums ADT.json"
```

## 3. Defensive Engineering & Failure Mode and Effects Analysis (FMEA)

### 3.1 Operating-state model

The pilot uses explicit states. Automated progression is prohibited; a named operator must sign the gate record.

| State | Permitted activity | Exit condition |
|---|---|---|
| `SAFE-HOLD` | Read-only inspection; no scoring or export. | Preconditions validated and release authorized. |
| `PREPARED` | Snapshot, schema checks, baseline generation, dry-run. | All T-Minus gates pass. |
| `ACTIVE` | Deterministic pipeline execution and monitored artifact creation. | Stage checks pass; no active abort trigger. |
| `DEGRADED` | Read-only diagnostics and preserved partial artifacts only. | Fault isolated; recovery checklist completed; rerun from checkpoint. |
| `ABORTED` | No further transformations or publications. | Independent review approves a clean restart with new `run_id`. |
| `FINALIZED` | Immutable export and analysis handoff. | Bundle hashes verified and limitations approved. |

### 3.2 FMEA risk matrix

Severity (S), occurrence (O), and detectability (D) are rated 1–5; `RPN = S × O × D`. An RPN ≥40, or any S=5 condition, requires a hard gate before continued execution.

| Failure mode | Cause / effect | S | O | D | RPN | Preventive control | Detection and response |
|---|---|---:|---:|---:|---:|---|---|
| Raw-file corruption | Partial copy, unauthorized edit, disk fault; invalid analysis input. | 5 | 2 | 2 | 20 | Read-only archive, dual copies, SHA-256 manifest. | Hash mismatch: enter `ABORTED`; restore source snapshot. |
| Silent row loss | Join/filter/parser defect; biased counts. | 5 | 3 | 3 | 45 | Stage reconciliation and exclusion ledger. | Any unreconciled row: stop, diagnose, rerun stage. |
| Transfer-limited ADT use | Incomplete extract used as denominator; invalid rates. | 5 | 3 | 2 | 30 | Explicit metadata check for transfer limit. | If true/unknown: remove exposure factor; invalidate affected output. |
| CRS or axis mismatch | Latitude/longitude swap or inconsistent projection; wrong distances. | 5 | 2 | 3 | 30 | Fixed CRS contract; bounds and known-point tests. | Spatial outliers or test failure: halt geospatial stage. |
| School misclassification | Closed/non-K–12 POI treated as active school. | 4 | 3 | 3 | 36 | Explicit taxonomy, review ledger, provenance record. | Audit failure: correct inventory, rerun proximity and score. |
| Duplicate campus collapse | Distinct active campuses removed; distorted proximity. | 4 | 2 | 3 | 24 | Preserve multi-coordinate names pending adjudication. | Evidence review; reinstate and rerun. |
| Nondeterministic clustering/model | Different run yields different ranks. | 5 | 3 | 3 | 45 | Frozen seed, deterministic library settings, exact config. | Hash/value comparison failure: halt and remediate. |
| Network partition during acquisition | Partial or stale download. | 4 | 2 | 2 | 16 | Download to temporary path; content-length/hash checks. | Retain prior snapshot; do not promote incomplete file. |
| Dependency drift | Library update changes geometry or model semantics. | 4 | 3 | 3 | 36 | Lock versions and capture environment manifest. | Environment mismatch: execute only a versioned rerun. |
| Manual spreadsheet edit | Unlogged change alters source or result. | 5 | 2 | 4 | 40 | No manual editing of raw/derived production artifacts; access controls. | Hash/reconciliation mismatch: abort and restore. |
| Misinterpretation of output | Score treated as legal or causal decision. | 5 | 3 | 4 | 60 | Limitation banner, metadata, review checklist. | Publication review blocks release until corrected. |
| Hardware/process failure | Interrupted write or lost logs. | 4 | 2 | 3 | 24 | Atomic writes, stage checkpoints, duplicated logs. | Resume only from last verified checkpoint. |

### 3.3 Graceful degradation and N+1 redundancy

The system favors data preservation and correctness over continuity of scoring.

1. **Data layer.** Maintain the working raw snapshot plus one verified independent archival copy; retain manifest hashes for both. This is N+1 for the sole required data copy.
2. **Compute layer.** Persist validated checkpoints after intake, cleaning, geospatial assignment, feature generation, and ranking. A compute interruption may lose only the active uncommitted stage.
3. **Logging layer.** Send structured logs to a local run log and a separate append-only audit artifact. If the secondary log sink fails, enter `DEGRADED`; do not finalize a release without complete logs.
4. **Network layer.** The analytic run must operate offline after source snapshots and dependency environments are frozen. A network partition therefore degrades only acquisition, not reproducibility.
5. **Exposure feature.** If ADT completeness fails, continue only as a historical hotspot index with `w_e = 0`; retain explicit output label: `EXPOSURE_ADJUSTMENT_NOT_APPLIED`.
6. **Map layer.** If interactive map generation fails after a valid feature/rank table is created, preserve and export the validated table and manifest, label the visualization unavailable, and do not infer map-level validation.
7. **School feature.** If provenance, classification, or coordinate validation fails, the primary protocol response is to halt scoring. A crash-only diagnostic may be run only in an isolated, explicitly non-pilot diagnostic run; it cannot be called the Sentinel-VA pilot result.

### 3.4 Rollback and recovery protocol

1. **Contain.** Stop the pipeline. Disable output publication. Preserve process logs, terminal output, error trace, current configuration, and partial artifacts without overwriting them.
2. **Classify.** Assign a failure ID and determine whether the defect affects raw input, schema/transform, geospatial assignment, scoring, export, or interpretation.
3. **Freeze evidence.** Hash all partial artifacts and record their paths, timestamps, and row counts. Partial artifacts are evidence, not candidate final outputs.
4. **Return to the last verified checkpoint.** Select the most recent stage whose inputs, outputs, reconciliation report, and hashes passed. Do not resume from an unverified in-memory state.
5. **Restore.** Restore only from the verified raw/archive snapshot or verified checkpoint. Never copy a derived result back into raw data.
6. **Correct.** Implement the smallest traceable correction. Update the version, change log, tests, and configuration. A logic or configuration change requires a new `run_id`.
7. **Revalidate.** Rerun all downstream stages, not only the visibly failed artifact. Recalculate hashes, reconciliations, baseline comparisons, and applicable sensitivity tests.
8. **Review.** Require a second review of the failure description, correction, and rerun evidence where feasible. Document whether earlier outputs were invalidated.
9. **Release or abort.** Resume only when all gates pass. Otherwise maintain `ABORTED` and report the reason plainly.

### 3.5 Abort criteria (kill-switch)

The operator shall immediately enter `ABORTED`, preserve evidence, and prohibit scoring/publication if any of the following occurs:

| Trigger | Quantitative or unambiguous condition | Required action |
|---|---|---|
| Integrity breach | Any raw or verified checkpoint hash mismatch not explained by a versioned new source snapshot. | Stop; restore; open incident record. |
| Data-loss breach | Input reconciliation difference is non-zero, or duplicate resolution is not one-to-one and reason-coded. | Stop before features/ranking. |
| Spatial breach | Any included analytic row lies outside approved Norfolk boundary/buffer, or coordinate/CRS validation fails. | Stop geospatial processing; remediate. |
| ADT breach | `exceededTransferLimit=true`, missing, or unverifiable for an ADT file proposed for exposure adjustment. | Disable exposure adjustment; if it has already been used, invalidate run. |
| Provenance breach | Any analytic source lacks an owner/source, acquisition date, hash, or recorded licence/provenance status. | Stop release; exclude or document source properly. |
| Reproducibility breach | Two unchanged reruns produce non-identical row-level output values. | Stop; isolate nondeterminism. |
| Explainability breach | Any published top-10 location lacks contribution values or an explanation. | Stop publication. |
| Method breach | Post-result change to location unit, time window, weights, or inclusion rules without protocol amendment and full rerun. | Invalidate affected outputs; restart run. |
| Interpretation breach | Draft output presents the index as a legal determination, camera recommendation, causal prediction, or vendor-affiliated output. | Block release until corrected and reviewed. |

## 4. Chronological Execution Protocol

### 4.1 Phase T-Minus: pre-pilot validation

#### T−7 to T−3 days: governance, environment, and source freezing

1. Create a unique `run_id` and declare the intended geographic, temporal, and analytic scope.
2. Confirm that this document, the root README, all `docs/*.md` files, and the pilot README are internally consistent for the proposed run.
3. Create the run manifest before inspecting any score or rank.
4. Snapshot each raw source without editing it; calculate SHA-256 and store hashes in the manifest.
5. Record source owner, public/licensing status, acquisition date/time, URL or acquisition method, row/feature count, and known limitations.
6. Create and verify the N+1 archive copy of raw inputs and manifest.
7. Freeze the execution environment: language/runtime version, package lockfile, operating system, geospatial libraries, and deterministic random seed.
8. Configure atomic output directories: `raw`, `staged`, `derived`, `logs`, `exports`, and `archive` (or equivalent); ensure final outputs cannot overwrite prior runs.
9. Define the named operator, reviewer where available, and escalation contact; record that the project is independent and no municipal/vendor authorization is implied.

#### T−2 days: smoke tests and schema contract

1. Validate the crash schema contains the expected document identifier, datetime, roadway/location descriptors, severity and injury fields, pedestrian/bicycle fields, latitude, longitude, and relevant context fields.
2. Parse all crash datetimes without silently coercing invalid values. Emit a parse report and reason-coded exclusion table.
3. Check document-number uniqueness; compare the count to the documented 42,004 unique records and explain any difference.
4. Validate coordinate type, finite value, plausible latitude/longitude range, Norfolk boundary inclusion, and coordinate axis order.
5. Produce crash baseline distributions by year, month, hour, severity, fatalities, serious injuries, pedestrian involvement, bicycle involvement, and intersection type.
6. Validate both school file schemas, Norfolk locality label, `business_status`, coordinates, categories, and `last_verified_date`.
7. Combine school records only into a derived inventory; preserve raw source identifiers and original category fields.
8. Classify records into elementary, middle, high, K–12, preschool, kindergarten, closed, unresolved, and other. Generate a classification ledger.
9. Review repeated school names at distinct coordinates; retain them until evidence supports a change.
10. Validate that crash and school coordinates share a declared geographic CRS before computing distances; use a meter-based projected CRS for distance calculations and record it.
11. Inspect ADT metadata. If `exceededTransferLimit` is true, set `exposure_enabled=false` in the manifest and test that the pipeline cannot use ADT-derived rates.
12. Perform a dry run on a small, stratified, non-production sample. The dry run must exercise ingestion, hashing, rejection logging, coordinate transformation, location assignment, feature generation, and export without producing a publishable ranking.

#### T−1 day: baseline and go/no-go gate

1. Execute the full baseline establishment protocol in Section 2.1.
2. Select and freeze the location unit using only data-resolution and reproducibility evidence, not desired results.
3. Freeze the score specification, feature definitions, normalization method, weights/hyperparameters, temporal blocks, minimum-count rule, and sensitivity variants.
4. Run the deterministic rerun test using unchanged inputs and configuration.
5. Conduct the stratified manual quality audit and record all findings.
6. Review FMEA controls and confirm that raw/archive copies, checkpoints, logs, kill-switch, and rollback owner are operational.
7. Sign the go/no-go record. A `GO` requires every hard gate to pass. A `NO-GO` moves the study to `SAFE-HOLD` or `ABORTED`; it does not permit a partial ranked output.

### 4.2 Phase T-Zero: controlled launch

1. Confirm the current hashes match the frozen manifest. If they differ, stop and issue a new `run_id` or restore the verified snapshot.
2. Confirm the pipeline version, dependency lockfile, CRS, random seed, and configuration hash match the pre-approved specification.
3. Set the operating state to `ACTIVE` and start structured telemetry.
4. Execute intake and staging. At completion, verify row reconciliation and schema validation before permitting the next stage.
5. Execute cleaning and exclusion ledger generation. Review exclusion counts against baseline; deviations exceeding 0.5 percentage points in a core inclusion category require `DEGRADED` review before continuation.
6. Execute geospatial assignment. Verify geometry validity, Norfolk-boundary checks, assignment rate, and known-point smoke tests.
7. Execute school-proximity computation only after validating the active K–12 layer. Emit nearest-facility identifier, distance, and classification for each candidate location.
8. Execute feature generation and score calculation. If exposure is disabled, assert `w_e = 0` and affix the hotspot-index limitation to all metadata.
9. Produce only provisional artifacts until the T-Plus validation gates complete. Do not circulate a top-N list as a decision recommendation.

#### Minimum real-time telemetry

```text
timestamp_utc | run_id | stage | input_rows | retained_rows | excluded_rows |
assignment_rate | schema_errors | hash_status | config_hash | state | message
```

Stage-completion alerts shall fire for: non-zero reconciliation difference; hash failure; unhandled exception; schema failure; coordinate validation failure; transfer-limit violation; nondeterministic output; and missing required provenance.

### 4.3 Phase T-Plus: active execution and continuous verification

#### After each stage

1. Verify input/output hash recording and row-count reconciliation.
2. Confirm that all exclusion records have a reason code and source identifier.
3. Compare stage metrics with baseline and document any drift.
4. Create a verified checkpoint before beginning the subsequent stage.
5. If a hard gate fails, invoke Section 3.4 rather than patching data manually.

#### Daily operational checklist (for multi-day execution)

1. Confirm raw and archive source hashes remain unchanged.
2. Review structured logs for warnings, retries, exceptions, and missing telemetry intervals.
3. Check available storage, checkpoint readability, and output-path permissions.
4. Confirm no raw files or derived production tables were manually edited.
5. Revalidate the run manifest against the current configuration and environment.
6. Review FMEA incidents and open deviations; no unresolved S=5 or RPN≥40 issue may remain in `ACTIVE` state.
7. Store an immutable daily log bundle and its hash.

#### Periodic analytical checks

1. Run duplicate, missingness, and schema-drift checks before any new source refresh.
2. Execute location-unit sensitivity analysis using only pre-declared alternatives.
3. Execute temporal validation and retain every block-level result.
4. Confirm that score components remain non-negative or otherwise conform to the frozen definition; verify weight sum equals 1.0.
5. Inspect top and bottom locations through a blinded, fixed-size manual spot-check: review the data lineage and geometry first, then unblind rank. This prevents rank-driven rationalization.
6. Verify every top-10 location has a data-backed explanation that distinguishes historical crash evidence, vulnerable-road-user involvement, temporal pattern, and facility proximity.
7. Use public reporting only as a qualitative external sanity check. It must not alter scores, labels, weights, or inclusion rules.

### 4.4 Phase T-Final: cooldown, export, and post-pilot handoff

1. Stop further ingestion and mark the source snapshot cutoff date/time.
2. Complete all queued stage validations, temporal stability checks, sensitivity analyses, and manual audits.
3. Review all abort criteria one final time. Any unresolved critical issue returns the run to `ABORTED`; do not export a qualified result as final.
4. Produce final machine-readable artifacts: source manifest, exclusion ledger, school-classification ledger, location definition, feature table, score/rank table, validation report, log bundle, configuration, and map artifact if generated.
5. Produce final human-readable artifacts: methodology summary, data dictionary, limitations statement, FMEA incident summary, and reproducibility instructions.
6. Calculate SHA-256 for every final artifact and write a release manifest that references the frozen input hashes and `run_id`.
7. Verify a clean-room rerun, or an equivalent fresh-environment rerun, from the archived inputs and frozen configuration. Compare row-level outputs and hashes.
8. Move the verified release bundle to immutable/read-only archival storage. Preserve working artifacts separately; do not delete failures or superseded runs.
9. Issue the pilot decision using the following categories:
   - **Validated feasibility:** all hard gates pass, reproducibility passes, and limitations are accepted.
   - **Conditionally feasible:** core pipeline passes but a non-critical, explicitly bounded limitation (such as omitted ADT exposure) remains; output is labeled accordingly.
   - **Not yet feasible:** a required input, provenance control, location definition, or reproducibility criterion fails; no prioritization claim is released.
10. Transition to statewide work only after a separate readiness review confirms comparable locality data, source permissions, and a locality-by-locality validation plan. Norfolk success alone is insufficient evidence of statewide validity.

## 5. Required Research Record and Release Checklist

Before any pilot artifact is described as final, confirm all items below are present and hash-verified.

- [ ] Protocol version and signed go/no-go record.
- [ ] Immutable raw-source snapshots and N+1 archive copy.
- [ ] Input and output SHA-256 manifest.
- [ ] Data-source provenance and licence/status register.
- [ ] Schema-validation reports and reconciliation ledgers.
- [ ] School classification, open/closed handling, and duplicate-campus adjudication record.
- [ ] Location-unit specification, CRS, spatial tolerance/grid/cluster parameters, and sensitivity results.
- [ ] ADT completeness report, with exposure factor either verified or explicitly disabled.
- [ ] Frozen score specification, factor contributions, and interpretation limits.
- [ ] Temporal validation, stability statistics, confidence intervals, and any multiplicity correction.
- [ ] Stratified manual-audit sample, seed, findings, and remediation record.
- [ ] FMEA incident log, rollback evidence, and kill-switch status.
- [ ] Reproducibility rerun evidence from frozen inputs.
- [ ] Final limitations banner stating that the output is a historical prioritization aid, not a camera-deployment, legal, or causal determination.

## 6. Interpretation and Publication Guardrails

Every public-facing output shall contain substantially the following statement:

> Sentinel-VA's Norfolk output is a retrospective, public-data historical prioritization index. It is designed to make underlying factors inspectable. It does not predict individual crashes or violations, establish a legal school zone or camera eligibility, recommend deployment, replace engineering or legal review, or imply affiliation with a government entity or enforcement vendor.

The study report shall disclose: the 2016–2025 crash-data window; the use of validated active K–12 facility proximity rather than legal school-zone polygons; whether exposure adjustment was omitted because the available ADT extract was transfer-limited; the selected location unit; all material exclusions; and the difference between feasibility validation in Norfolk and statewide generalization.

## 7. Traceability to Existing Project Documentation

This procedure operationalizes the existing documentation without changing its scope:

- Root `Readme.md`: Norfolk-first feasibility framing, batch public-data architecture, explainable prioritization, and non-deployment limitations.
- `docs/BRD.md`: public-data, interpretability, reuse, and limitation requirements.
- `docs/PRD.md`: ingest → feature engineering → scoring → ranking → visualization pipeline, including open questions on data granularity and model choice.
- `docs/RoadMap.md`: Phase 2 readiness gates, Phase 3 execution activities, reproducibility, and statewide expansion conditions.
- `docs/Problem_statement.md`: proactive site-prioritization context while preserving the explicit boundary against computer vision, legal/procurement decisions, and vendor affiliation.
- `pilot study/Readme.md`: documented Norfolk inventory, school/ADT limitations, and the readiness gate that must precede analysis.

Any conflict between a future implementation detail and this procedure shall be resolved in favor of the more conservative control until a dated, versioned amendment documents the reason, impact, and rerun requirement.
