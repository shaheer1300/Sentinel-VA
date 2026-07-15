# Sentinel-VA Method Readiness and Gap Assessment

**Status:** Candid assessment for expansion planning  
**Assessment basis:** Repository implementation, frozen Norfolk configuration, and release materials for `norfolk-pilot-20260713-release-v7`  
**Scope:** What the current Norfolk pilot can support, what it cannot support, and what must change before its findings can be used to target real-world action.

## The honest bottom line

Sentinel-VA has built a **reproducible and inspectable way to summarize historical crash evidence in Norfolk**. That is real progress. The data pipeline reconciles its rows, produces the same output from the same inputs, and explains every score.

It has **not** built a validated method for choosing camera locations, proving that a location needs enforcement, predicting future crashes or violations, estimating crash rates, or showing that an intervention will reduce harm. The pilot's two most important reliability tests failed:

| Test | Required before release | Observed result | Why it matters |
|---|---:|---:|---|
| Stability over time | Spearman rank correlation ≥ 0.70 | 0.573 and 0.562 | The locations rise and fall too much when different historical periods are compared. |
| Stability over mapping method | Top-10 overlap ≥ 0.60 | 0.250 at 200 m; 0.176 at 300 m | The apparent "top ten" changes sharply when the city is divided into slightly different grid sizes. |

This means the method should **not** currently be used to target a named intersection, camera, enforcement action, funding decision, or public-safety claim. At most, it can generate **broad, clearly labelled hypotheses for further investigation**. Even that use must retain the conditional status and the underlying evidence.

The central problem is not that the project lacks a more complicated model. It lacks the right evidence chain between a historical crash pattern and a defensible decision about a particular intervention. More machine learning would not fix that on its own.

## What is already solid

These are strengths worth keeping as the project expands:

- The run is reproducible: the released score table reruns with identical row-level values.
- The data pipeline records source and output hashes, transformations, exclusions, configuration, and run IDs.
- The released crash reconciliation is complete: 42,004 source rows equal 41,714 eligible rows plus 290 exclusions.
- Every eligible crash is assigned to one analytic location, and every published score includes its component contributions and a limitation statement.
- The score specification was frozen before rank inspection. This reduces the risk of changing the formula after seeing a preferred answer.
- The project disabled the traffic-exposure component rather than quietly using an incomplete traffic-volume export. That is the correct defensive decision.
- The release tells readers that its grid cells are not intersections, legal school zones, or deployment recommendations.

These controls make Sentinel-VA a useful research foundation. They do **not** establish that the score is accurate or useful for a real-world decision.

## What the current output is—and is not

| Claim | Is it supported now? | Plain-language answer |
|---|---|---|
| "This cell had more severe historical crash evidence than many other Norfolk cells." | Yes, with the stated data limitations. | This is what the index directly summarizes. |
| "This broad area may deserve a traffic-safety review." | Only as an exploratory prompt. | The ranking is unstable, so it is a lead to check, not a confirmed priority. |
| "This is a high-risk intersection." | No. | The unit is a 250 m grid cell, not a verified intersection. |
| "This is a legal school zone or an eligible enforcement site." | No. | A nearby NCES school point is not a legal school-zone boundary or an eligibility decision. |
| "This site has an unusually high crash rate." | No. | There is no trustworthy traffic-exposure denominator. |
| "This site has a high stop-sign or crosswalk-violation rate." | No. | The model does not contain violation observations. |
| "A camera or any other intervention will reduce harm here." | No. | The pilot has no causal or before/after evaluation. |
| "The top ten are the ten places Norfolk should act first." | No. | The top ten changes materially across time blocks and grid sizes. |
| "The Norfolk result works across Virginia." | No. | Only Norfolk has been processed and validated. |

## Confirmed shortcomings and problems

The following findings come from the released materials or the current implementation. “Confirmed” does not mean that the project is broken; it means the limitation is known and must be addressed before making a stronger claim.

### 1. The two core stability gates failed

The pilot compares adjacent time blocks and alternative grid sizes. Both tests failed their pre-registered thresholds. This is the most important result in the repository.

The practical consequence is simple: a location can look like a top priority because of the selected years or the selected 250 m grid, rather than because it is reliably more important than nearby alternatives. Publishing a precise ranked shortlist despite this would overstate the evidence.

**What is needed:** Do not lower the thresholds after seeing the failure. First improve the inputs and location definition, then write a new versioned analysis plan *before* looking at new ranks and rerun all validation gates.

### 2. The model measures crash history, not the decision it originally aims to support

The code uses historical crash counts, reported injury severity, pedestrian/bicycle flags, time concentration, and school proximity. It has no direct observations of stop-sign violations, crosswalk violations, yielding behavior, speeding, near misses, or camera-eligible behavior.

A crash can happen for many reasons unrelated to the type of enforcement under consideration. Conversely, a location can have frequent violations but few recorded crashes. A crash-history index therefore cannot by itself tell a decision-maker where a camera would be appropriate or effective.

**What is needed:** Define one decision at a time and collect a matching outcome. For example:

| Intended decision | Outcome that must be measured |
|---|---|
| Find places for a general traffic-safety field review | Reliable crash, traffic, pedestrian/bicycle, and road-design evidence. |
| Select a crosswalk or stop-sign enforcement candidate | Verified, time-stamped observations of the relevant violation and legal eligibility. |
| Select an engineering treatment | Site geometry, control devices, speeds, conflicts, accessibility conditions, and an engineering diagnosis. |
| Claim that an intervention reduces harm | A prospective before/after study with credible comparison sites or another defensible causal design. |

### 3. There is no exposure denominator, so the score is not a rate

The traffic-volume (ADT) extract is explicitly transfer-limited and the code correctly forces its weight to zero. A high crash count may indicate a dangerous location, but it may also indicate simply that many more vehicles, pedestrians, or bicycles pass through it.

Without exposure, the project cannot distinguish “many crashes because there is much traffic” from “many crashes for the amount of traffic.” This can systematically favor busy roads and major corridors.

**What is needed:** A complete, quality-checked, time-aligned traffic-exposure dataset with road-segment or intersection linkage. It should cover vehicle volume and, where the decision concerns vulnerable road users, pedestrian and bicycle exposure as well. The project must document coverage, missing segments, collection dates, units, and how traffic changes by time of day and school calendar.

### 4. The geographic unit is not the thing a decision-maker would act on

The pilot uses fixed 250 m cells because authoritative intersection topology was unavailable. This choice is reproducible, but a cell can cover more than one intersection, mid-block area, driveway, interchange, or road type. Its displayed point is the **cell centroid**, not necessarily the crash concentration or a safe/feasible installation point.

The failed grid-sensitivity test confirms this is not just a wording issue. The chosen grid materially changes the answer. The untested placement of the grid origin may also affect which events fall together.

**What is needed:** An authoritative, versioned road network and an independently checked crash-to-network matching process. Depending on the decision, the primary unit should be a verified intersection, approach, crossing, road segment, or corridor—not a convenience grid. Test alternative units, multiple grid offsets where grids remain useful, nearby buffer sizes, and sensible top-tier definitions before selecting one.

### 5. The score's weights and cutoffs are transparent but unvalidated

The weights—40% historical burden, 25% vulnerable-road-user evidence, 15% time concentration, and 20% school proximity—are frozen and visible. The raw formula also adds fixed severity multipliers and uses a 500 m school-distance decay. Transparency is good; it does not prove these choices are correct.

There is currently no evidence that 20% is the right influence for school proximity, that 500 m is the right distance, that the severity multipliers match harm, or that the combined index predicts a useful future outcome better than a simple crash count. The 0–100 percentile scale creates a relative ranking even if every location has low absolute risk.

**What is needed:** Pre-specify a justification for each feature and weight. Use one or both of:

- structured expert elicitation from qualified traffic-safety and road-design professionals; and
- estimates learned from a labelled, future-facing outcome with a held-out evaluation set.

Compare against simple baselines such as recent severe-crash count and exposure-adjusted crash rate. Keep the simpler method unless a more complex one shows a meaningful, reproducible improvement. Report uncertainty, not just a single rank.

### 6. The time feature can overstate weak evidence

The time component is the largest share of crashes in one of four broad hour groups plus the largest share on one weekday. A location with only one crash is perfectly concentrated by that definition. The full score does not apply a reliability adjustment that shrinks such small-sample patterns toward the city average.

The current temporal validation filters comparison cells to those with at least five events in each block, but that minimum does not make the published full-ranking time feature reliable for every cell.

**What is needed:** Apply minimum-count rules or statistical shrinkage for sparse locations, test finer but meaningful time windows only where counts support them, and add school-day/term, weather, and seasonal context where relevant. Measure whether the time feature improves prediction of the selected outcome on unseen data.

### 7. School proximity is contextual, not legal or operational evidence

The model uses a straight-line distance from the cell centroid to the nearest NCES-reported 2023–24 K–12 facility. That point is not a legal school zone, walking route, crossing location, operating schedule, enrollment, arrival/dismissal pattern, or current confirmation that the facility was open throughout 2016–2025.

Using a 2023–24 facility layer for a crash window beginning in 2016 also introduces time mismatch. A school could have opened, closed, relocated, or changed its traffic pattern during the study period.

**What is needed:** Official, current local school-zone and school-route geometry; operating dates; arrival/dismissal schedules; and a documented historical treatment for schools that changed over the study window. Use network/access routes where appropriate, not only straight-line distance. Keep legal eligibility as a separate verified field, never as a score inferred from proximity.

### 8. Important traffic-safety context is missing

The current feature set does not include many factors that explain both crash risk and the choice of a remedy: roadway class, lanes, speed limit and observed speed, traffic control, crosswalk type, signal timing, lighting, curvature, parking, sidewalk and bicycle infrastructure, transit activity, driveway density, construction, land use, and recent safety improvements.

This makes the index vulnerable to omitted-variable errors: a high score may be caused by a known design problem that calls for engineering, not enforcement; a low score may hide a dangerous condition that lacks crash history.

**What is needed:** A documented road-and-place inventory linked to the action unit, plus field verification for candidate sites. Each candidate should produce a diagnosis explaining *why* it is risky and which interventions are plausible, rather than only a composite number.

### 9. Historical crash records are an incomplete and potentially changing observation system

The pipeline checks schema, dates, coordinates, duplicates, boundaries, and row reconciliation. Those are necessary controls. It does not independently prove that every crash was reported, coded consistently, geocoded correctly, or comparable across all ten years. Reporting practices, severity coding, road layouts, traffic volumes, and data systems may have changed.

Pedestrian and bicycle indicators may overlap; the data dictionary explicitly notes that vulnerable-road-user crash totals can overlap. These fields should not be casually read as unique people or independent events.

**What is needed:** A source-data quality study with a data owner or independent reviewer: field definitions, missingness by year and geography, geocoding accuracy, code changes, known under-reporting, duplicates, linkage to police/EMS where permitted, and a refresh policy. Treat missingness and coding uncertainty as model inputs or limitations, not as invisible noise.

### 10. Validation proves repeatability, not real-world accuracy

Running the same deterministic code twice verifies that the implementation is stable. The 100-record audit verifies the math of grid assignment and aggregate recounts for a sample. Neither test establishes that the source record is correct, that the grid is an appropriate location, or that the ranked locations predict future safety problems.

The recorded audit was performed by the implementation agent and explicitly reports no independent second reviewer. It is therefore not an independent external validation.

**What is needed:** Separate the following checks and require all that apply:

1. **Data lineage audit:** independent reviewer checks source-to-output records and geospatial matches.
2. **Field/engineering audit:** qualified reviewers inspect a blinded, stratified set of high, middle, and low candidates before seeing their ranks.
3. **Temporal holdout validation:** train or specify using earlier years, then evaluate against later, untouched outcomes.
4. **Geographic holdout validation:** validate in a different locality before making a statewide claim.
5. **Outcome validation:** compare predicted priorities to the defined outcome—such as independently observed violations or future exposure-adjusted severe crashes.

### 11. There is no causal evidence for any intervention

The pilot is retrospective. It does not compare what happened with and without a camera, traffic-calming project, signal change, education campaign, or enforcement program. It cannot estimate avoided crashes, violations prevented, cost effectiveness, spillover to adjacent streets, or unintended effects.

**What is needed:** A prospective evaluation plan before deployment. It should define the intervention, start date, outcomes, comparison sites, measurement periods, expected effects, discontinuation conditions, and how changes in traffic volume or reporting will be handled. An independent evaluator is strongly preferred.

### 12. The project lacks an equity, civil-rights, privacy, and community-governance method

The release correctly says it does not replace equity, community, legal, procurement, or privacy review. It does not yet provide the method for doing those reviews. For enforcement-related decisions, that omission is material: historical crash and enforcement data can reflect unequal reporting, infrastructure investment, exposure, and policing patterns.

**What is needed:** Before any enforcement-oriented use, establish a governance plan that includes:

- a documented legal and eligibility review by the responsible authority;
- an equity assessment with pre-specified subgroup and geographic analyses, safeguards against disparate burden, and public reporting;
- meaningful community engagement before shortlist approval, including affected schools, pedestrians, cyclists, disability advocates, and residents;
- privacy, data-retention, security, access, and vendor-governance rules for any new observational or camera data; and
- an appeals, complaint, monitoring, and stop/rollback process.

Do not use demographic characteristics as a shortcut for enforcement targeting. Use them, where lawful and appropriate, to test whether the method or its consequences distribute harms unfairly.

### 13. Source provenance and documentation are not yet fully release-ready

The configuration describes the Norfolk crash and ADT snapshots as repository-acquired public data whose source URL and final licence/terms review still need recording before public release. The web release repeats that the crash source link must accompany a public repository release.

Some earlier planning documents also still describe a statewide, intersection-level, camera-prioritization product, while the current release is a Norfolk-only, grid-cell, exploratory analysis. The roadmap still shows phases as in progress/not started even though the release documents phases 0–7 as complete.

This inconsistency can cause an ordinary reader to believe the product is more mature or operationally authorized than it is.

**What is needed:** Complete a source register with authoritative URLs, access dates, licences/terms, permitted reuse, refresh schedule, field dictionaries, hashes, and owner contacts. Reconcile the README, problem statement, PRD, BRD, roadmap, pilot reports, and website so they all state the same current scope and decision-use boundary. Version or archive superseded plans rather than leaving conflicting claims active.

### 14. Statewide expansion has no supporting evidence yet

Norfolk is one locality with its own data coverage, road network, school patterns, and operational context. The repository has no locality-by-locality source audit, location matching, exposure coverage assessment, external validation, or legal/eligibility review for the rest of Virginia.

**What is needed:** Treat each locality as a new study until it passes its own input-quality, provenance, spatial-unit, stability, equity, and outcome-validation gates. A statewide map should never be produced by merely concatenating local datasets with different definitions and completeness.

## What must be obtained or built

The following is the minimum expansion backlog, ordered by dependency rather than convenience.

### A. Decide the claim before collecting more data

Write a short decision charter that names:

- the decision-maker and the decision they will make;
- the intervention(s) being considered;
- the eligible geography and legal rules;
- the outcome to improve and the time horizon;
- what level of error is acceptable and who bears the harm from a false positive or false negative; and
- the strongest claim the project intends to make.

Until this exists, “target these areas” is too vague. Targeting a site for a field visit, a crosswalk redesign, or an enforcement device are fundamentally different decisions that need different evidence.

### B. Obtain authoritative location and eligibility data

At a minimum, obtain or verify:

- a current, versioned road network with intersections, approaches, segments, directionality, and road names;
- official school-zone, school-route, crossing, and operating-period data—not just facility points;
- traffic controls, crosswalks, speed limits, signals, lanes, lighting, sidewalks, bicycle facilities, transit stops, and recent projects;
- legal eligibility fields that are verified separately from the risk score; and
- a repeatable geocoding/map-matching process with known accuracy and a review queue for uncertain records.

### C. Obtain complete exposure and behavior evidence

For a safety-priority method, obtain complete, time-aligned exposure estimates by the action unit. Vehicle volume alone is insufficient when the goal includes pedestrian or bicycle safety.

For a violation or enforcement method, obtain independently measured observations of the *specific* prohibited behavior. The collection plan must be representative across geography, time of day, day type, and candidate risk level; only observing locations already thought to be dangerous would bias the result.

Possible sources may include responsible public agencies, validated count programs, field observations, or privacy-governed sensing. The source is less important than documented completeness, accuracy, lawful use, and a clear measurement protocol.

### D. Rebuild the method around reliable action units and uncertainty

The next version should:

1. Match crashes, traffic, road attributes, and school-zone data to the same verified intersection/approach/segment/corridor units.
2. Separate three scores if all three are needed: safety burden, observed violation likelihood, and legal/engineering feasibility. Do not hide them in one number.
3. Use exposure-adjusted rates or an appropriate count model with shrinkage for sparse locations.
4. Use recency in a pre-specified, testable way instead of assuming that a ten-year total is equally relevant today.
5. Quantify uncertainty: confidence/credible intervals, data-completeness flags, and a stability/consensus measure for every candidate.
6. Explain the recommended *next action* and the evidence behind it, not only its rank.

A transparent statistical model may still be the right final method. The requirement is not sophistication; it is demonstrated performance against the stated outcome and understandable reasoning for affected people.

### E. Validate before making any targeting recommendation

Use a prospective, preregistered validation protocol. At minimum:

| Validation question | Evidence required |
|---|---|
| Does the method work later in time? | A fully untouched future-period test with the decision outcome defined in advance. |
| Does it work outside Norfolk? | A geographically separate locality held out from development. |
| Is the answer robust to reasonable mapping choices? | Alternative road units, grid offsets/sizes where relevant, buffer choices, and matching tolerances. |
| Does it beat simple alternatives? | Comparison with recent severe-crash count, exposure-adjusted rate, and an informed engineering baseline. |
| Are candidates real and actionable? | Blinded field/engineering review and legal eligibility verification. |
| Does it create inequitable burdens or blind spots? | Pre-specified equity analysis, community review, and published mitigation actions. |
| Does the intervention help? | Before/after evaluation with credible comparison sites and monitoring for displacement/unintended effects. |

The existing temporal and grid thresholds must either pass in a newly preregistered run or be replaced *before analysis* with better-justified decision metrics. A failed threshold cannot be rewritten away after results are known.

### F. Turn a ranking into a safe decision process

No raw top-ten list should be an action list. Use a staged workflow instead:

1. **Screen:** identify broad areas with multiple consistent signals and explicit uncertainty.
2. **Verify:** check records, map matching, current site conditions, road changes, and legal eligibility.
3. **Diagnose:** identify the likely safety mechanism and compare engineering, education, and enforcement options.
4. **Consult:** conduct community, equity, privacy, and authority review.
5. **Decide:** document why a specific intervention is proportionate and feasible.
6. **Evaluate:** publish outcomes and stop, change, or expand based on the pre-specified evidence.

This prevents an easy but unsafe jump from “a location has historical crashes” to “install a camera here.”

## Readiness gates for stronger claims

The project should use explicit gates rather than vague labels such as “production-ready.”

| Claim the project wants to make | Minimum gate before making it |
|---|---|
| “This is an exploratory historical crash-priority index.” | Current reproducibility, provenance, and limitation controls; persistent conditional labelling; no operational recommendation. |
| “This broad area warrants a field review.” | Stable results across time and mapping choices, current site verification, complete data-quality flags, and qualified traffic-safety review. |
| “This specific intersection/approach should be prioritized for an intervention study.” | Verified action unit, exposure data, relevant road context, future-period validation, field diagnosis, equity/community review, and legal feasibility. |
| “This site is suitable for this type of enforcement.” | All prior gates plus direct measurement of the relevant violation, verified statutory/local eligibility, privacy/governance approval, and a proportionality assessment against non-enforcement alternatives. |
| “This intervention reduces harm.” | A prospective evaluation with credible comparison, published effect and uncertainty, equity impacts, and monitoring for unintended effects. |
| “This works statewide.” | Separate source, validation, governance, and outcome evidence for each included locality; pooled performance only after demonstrating comparable definitions and quality. |

The current pilot passes only the first row, and even there its publication must remain clearly conditional because the stability gates failed.

## Proposed next release: a practical, honest sequence

1. **Freeze the current pilot as exploratory.** Do not relabel its top cells as target locations or recommendations.
2. **Reconcile public documentation.** Remove or clearly archive claims that imply statewide coverage, verified intersections, camera-site selection, or completed phases that are not supported by the final release.
3. **Create the decision charter and governance plan.** Get agreement from the responsible traffic-safety, legal, and community stakeholders before expanding data collection.
4. **Run a Norfolk data-acquisition and map-matching phase.** Prioritize complete exposure data, authoritative road/intersection geometry, official school-zone information, and current road context.
5. **Design a small independent observation study.** Measure the specific behavior the project intends to address across a representative sample of locations and times.
6. **Build Version 2 as a separate, preregistered study.** Preserve Version 1; do not silently overwrite it or tune it until it passes.
7. **Require external and field validation before publishing a location shortlist.** If the new method is not stable or does not predict the chosen outcome, publish that result and do not operationalize it.
8. **Only then run a prospective intervention pilot.** Treat results as evidence about the intervention, not merely evidence that the ranking looks plausible.

## Final recommendation

Keep Sentinel-VA, but change its near-term promise. Its credible promise today is:

> “A transparent research pipeline for auditing and exploring historical traffic-safety patterns in Norfolk.”

It is **not yet credible** to promise:

> “A data-driven system that tells authorities where to deploy enforcement or which locations to target first.”

The route to that stronger claim is not a cosmetic disclaimer or a higher score threshold. It requires better matching between the decision and the outcome, complete exposure and location data, stable geography and time results, independent field validation, equity and legal governance, and a prospective test of whether the proposed intervention actually helps.

## Evidence used for this assessment

- [Root README](../README.md): final classification, passed controls, failed stability gates, and scope boundary.
- [Norfolk Pilot Findings](Norfolk_Pilot_Findings.md): released counts, formulas, validation results, and stated limitations.
- [Norfolk pilot overview](../pilot%20study/README.md): final pilot status and safeguards.
- [`configs/norfolk_pilot.json`](../configs/norfolk_pilot.json): location-unit, source, school, boundary, and exposure settings.
- [`configs/norfolk_phase4_7.json`](../configs/norfolk_phase4_7.json): frozen weights, formulas, and validation thresholds.
- [`src/sentinel_va/scoring.py`](../src/sentinel_va/scoring.py): implemented score and time/proximity treatment.
- [`src/sentinel_va/validation.py`](../src/sentinel_va/validation.py): rerun, audit, temporal, and grid-sensitivity implementation.
- [Problem statement](Problem_statement.md), [PRD](PRD.md), [BRD](BRD.md), and [roadmap](RoadMap.md): original product framing and documentation status.

This assessment deliberately distinguishes evidence present in the repository from work that still needs to be performed. It does not assert that any external source, statute, locality, vendor, or intervention has been independently verified here.
