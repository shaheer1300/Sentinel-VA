# Sentinel-VA

**Where should Norfolk look first for traffic-safety improvements before someone gets hurt?**

Sentinel-VA is an independent public-data research project that ranks Norfolk, Virginia, analysis cells for further traffic-engineering review. The completed pilot is **conditionally feasible**: its data lineage and deterministic rerun gates passed, while its pre-registered temporal-stability and grid-sensitivity gates did not. The output is therefore exploratory and is not a camera-deployment recommendation, legal eligibility determination, causal model, or crash-rate estimate.

## Public pilot

[Open the Sentinel-VA Norfolk pilot](https://sentinel-va-norfolk-pilot.abeer.chatgpt.site)

The web application provides a memory-bounded interactive map, searchable and sortable ranked table, per-location score explanations, validation results, methodology, limitations, and downloadable evidence. Its default view uses a minimum index of 80 and renders no more than 40 points on one shared canvas.

## Final pilot result

| Measure | Result |
|---|---:|
| Release run | `norfolk-pilot-20260713-release-v7` |
| Classification | Conditionally feasible; exploratory ranking |
| Eligible Norfolk crash records | 41,714 |
| Candidate 250 m cells | 1,609 |
| NCES-reported K–12 schools | 74 |
| Deterministic rerun | Passed |
| Stratified lineage audit | 100 / 100 passed; Wilson 95% lower bound 96.3% |
| Temporal stability | Failed; adjacent-period Spearman 0.57 and 0.56, required ≥ 0.70 |
| Grid sensitivity | Failed; top-10 Jaccard 0.25 and 0.176, required ≥ 0.60 |
| Exposure adjustment | Not applied; available ADT export is transfer-limited |

## Method

The transparent index combines four percentile-based components:

- 40% historical crash burden;
- 25% pedestrian and bicycle evidence;
- 15% time concentration; and
- 20% proximity to NCES-reported public or private K–12 schools.

Traffic exposure has a weight of 0% because the available ADT extract cannot support a complete denominator. Every published row includes its component contributions, supporting counts, nearest-school distance, explanation, limitation, and immutable run identifier.

## Repository guide

- [`pilot study/Procedure.md`](pilot%20study/Procedure.md) defines the scientific and defensive execution procedure.
- [`pilot study/execution.md`](pilot%20study/execution.md) defines the phase tasks, tests, and handoff criteria.
- [`pilot study/README.md`](pilot%20study/README.md) records the completed pilot outcome and limitations.
- `src/sentinel_va/` contains the deterministic data, scoring, validation, and release pipeline.
- `tests/` contains the Python quality gates.
- `web/` contains the independently buildable showcase application and its web contract tests.
- `outputs/runs/norfolk-pilot-20260713-release-v7/` contains the final audit trail and phase handoffs.

## Verification

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m pytest
Set-Location web
npm test
```

The final release gate is expected to report 15 passing Python tests and 5 passing web tests.

## Scope boundary

The pilot does not detect violations, process camera footage, recommend enforcement sites, establish legally defined school zones, or replace traffic-engineering, legal, community, equity, procurement, or privacy review. Statewide expansion requires comparable statewide source coverage and a new validation cycle; the Norfolk result must not be generalized without that work.

## About

Built by Shaheer Ahmad as an independent analysis project exploring proactive, explainable approaches to traffic-safety prioritization.
