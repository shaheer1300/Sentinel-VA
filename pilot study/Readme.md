# Norfolk Pilot Study

**Project:** Sentinel-VA  
**Status:** Execution Phases 0–7 complete  
**Release run:** `norfolk-pilot-20260713-release-v7`  
**Classification:** **Conditionally feasible; exploratory ranking**  
**Public application:** [Sentinel-VA Norfolk pilot](https://sentinel-va-norfolk-pilot.abeer.chatgpt.site)

## Purpose and boundary

The Norfolk pilot tests whether public or already-acquired data can support a transparent, reproducible prioritization of traffic-safety locations using historical crashes, vulnerable-road-user evidence, time concentration, and proactive proximity to schools.

The pilot is not a camera-deployment recommendation, legal eligibility determination, causal inference, crash-rate estimate, or production traffic-safety system. Its 250 m cells are reproducible analytic proxies rather than intersections, legal school zones, or deployment units.

## Completed result

| Result | Final value |
|---|---:|
| Source crash rows | 42,004 |
| Eligible rows inside the approved Norfolk boundary | 41,714 |
| Outside-boundary exclusions | 290 |
| NCES-reported public/private K–12 facilities | 74 |
| Candidate 250 m cells | 1,609 |
| Eligible-record assignment rate | 100% |
| Highest index | 89.6875 |
| Lowest index | 21.6169 |
| Exposure adjustment | Disabled; weight 0% |
| Python tests | 15 passed, 0 failed |
| Web tests | 5 passed, 0 failed |

The approved geographic boundary is the U.S. Census Bureau TIGERweb January 1, 2025 county-equivalent boundary for Norfolk city (`GEOID 51710`). School proximity uses official NCES public-school 2023–24 and private-school current location datasets, replacing the superseded third-party POI inputs for the release run.

## Scoring method

The index is a deterministic weighted combination of percentile-normalized components:

| Component | Weight | Evidence |
|---|---:|---|
| Historical burden | 40% | Crash count with explicit fatality, suspected-serious-injury, and people-injured contributions |
| Vulnerable road users | 25% | Pedestrian and bicycle crash evidence |
| Time concentration | 15% | Concentration across time-of-day and day-of-week groups |
| School proximity | 20% | Cell-centroid distance to the nearest reported NCES K–12 school |
| Exposure | 0% | Not applied because the ADT export is transfer-limited |

All 1,609 published rows expose their component contributions and supporting explanation. The output is described as a historical priority index and never as an exposure-adjusted crash rate.

## Validation outcome

| Gate | Threshold | Observed result | Decision |
|---|---:|---:|---|
| Exact reproducibility | Identical rerun | Identical row-level scores | Pass |
| Stratified lineage audit | Wilson 95% lower bound ≥ 95% | 100/100; lower bound 96.3% | Pass |
| Temporal stability | Spearman ≥ 0.70 | 0.573 and 0.562 | Fail |
| Grid sensitivity | Top-10 Jaccard ≥ 0.60 | 0.25 at 200 m; 0.176 at 300 m | Fail |

No abort criterion was triggered. Because the two stability gates failed, the final classification is **conditionally feasible**: the pipeline and explanations are reproducible, but the exact ranking is not stable enough for operational selection.

## Public application safeguards

The release application:

- displays the conditional classification persistently;
- defaults to an index threshold of 80;
- renders at most 40 points on one shared Leaflet canvas;
- limits the visible table to 100 rows while retaining all 1,609 records in the downloadable release data;
- supports search, deterministic sorting, reset, and row-to-detail inspection;
- provides a complete tabular alternative to the map;
- exposes score components, supporting values, limitations, and run metadata;
- fails closed with an unavailable-state message if release data cannot be loaded; and
- publishes reviewed CSV, JSON, and Markdown evidence downloads.

## Data limitations

- The crash record is historical and does not prove future risk or causation.
- The transfer-limited ADT file is excluded from the score; no complete exposure denominator is available.
- NCES points identify reported facilities, not attendance boundaries or legally defined school zones.
- Grid geometry and cell size affect the precise ordering, as demonstrated by the failed sensitivity gate.
- Statewide generalization is prohibited until comparable sources and locality-specific validation are completed.

## Evidence and reproducibility

The final audit trail is stored in `outputs/runs/norfolk-pilot-20260713-release-v7/`. Phase handoffs, hashes, validation tables, release notes, the deployment report, and the final manifest are bound to that immutable run ID.

Use [`Procedure.md`](Procedure.md) for the scientific procedure and [`execution.md`](execution.md) for the operational phase framework.
