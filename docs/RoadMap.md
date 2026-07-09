# RoadMap.md

**Project:** Sentinel-VA — Proactive Risk Scoring for Virginia's Automated Traffic Enforcement Rollout
**Author:** Shaheer Ahmad
**Date:** July 9, 2026
**Version:** 1.0
**Status:** Draft
**Related Documents:** `Problem_statement.md`, `BRD.md`, `PRD.md`, `README.md`

---

## Methodology

This section is the audit trail for the project: it explains *how* the work was designed and will be carried out, so that anyone — a collaborator, a reviewer, or a future version of the author — can reconstruct the reasoning without needing to have been in the room.

### 1. Guiding Principles

The methodology is built on four non-negotiable principles, carried through from `BRD.md`:

1. **Public data only.** No proprietary, vendor, or private data is used at any stage. Every input dataset is named and linked in the documentation.
2. **Explainable over black-box.** The risk score must be decomposable — a reader can see which factors drove a given location's rank, not just the final number.
3. **Proactive, not reactive, by design.** The entire premise of the project is to identify risk *before* an incident, so the methodology deliberately avoids relying on any single recent event as a trigger.
4. **Honest about limitations.** The project states plainly what it does not do (no violation detection, no claim of vendor affiliation, no substitute for formal traffic engineering review) in every document that presents results.

### 2. Documentation-First Approach

Before any data was touched, the project was scoped through a standard planning sequence, each document building on the last:

`Problem_statement.md` (why this matters) → `BRD.md` (business case and requirements) → `PRD.md` (product scope and functional requirements) → `RoadMap.md` (this document — how the plan gets executed) → implementation.

This ordering is deliberate: it forces the problem and requirements to be fixed before technical decisions are made, and it means every technical choice made later can be traced back to a requirement (BR-# or FR-#) rather than being ad hoc.

### 3. Data Methodology

- **Sourcing:** Virginia crash and pedestrian-incident records (VDOT / Virginia DMV Traffic Crash Facts) and Virginia public school location data (VA Department of Education directory), per `PRD.md` §9.
- **Cleaning and granularity check:** Before any modeling begins, the crash data's resolution is verified (intersection-level vs. road-segment/route-level — the open question flagged in `PRD.md` §13). This determines the finest-grained unit the risk score can be computed at, and is documented rather than assumed.
- **Feature engineering:** For each location unit, four factor groups are computed — historical incident density, pedestrian-involvement rate, time-of-day/day-of-week concentration, and proximity to a school zone.
- **Scoring:** Factors are combined into a single score using either a transparent weighted-sum heuristic or a gradient-boosted model with exposed feature importances (final choice made during Phase 3, based on data volume/quality — see `PRD.md` §13). Whichever is chosen, the requirement is the same: the contribution of each factor to the final score must be visible per location.
- **Validation:** Two checks are applied before results are treated as final —
  - *External sanity check:* top-ranked Virginia locations are compared qualitatively against the profile of locations Maryland's program has already targeted (school zones, historical complaint patterns), to confirm the model surfaces the kind of location the existing program considers high-priority.
  - *Manual spot-check:* a sample of top-10 and bottom-10 ranked locations is manually reviewed against public reporting to confirm the ranking is directionally sensible, not just numerically plausible.

### 4. Tooling

Python (pandas, geopandas) for data processing; a weighted heuristic or LightGBM/XGBoost for scoring, chosen for interpretability; folium or kepler.gl for the interactive map. All open-source, no paid API dependencies, per `PRD.md` NFR-3.

### 5. Change Management

Each planning document is versioned (see the version field in its header). If methodology changes materially after Phase 2 begins (e.g., the granularity check forces a different unit of analysis), the change and its reason are logged in a short changelog at the bottom of this file rather than silently overwriting prior assumptions.

### 6. Reproducibility

Anyone with access to the same public data sources should be able to follow this document plus `PRD.md` §10 (Technical Approach) and arrive at a comparable ranked output. This is treated as a requirement, not a nice-to-have — see `PRD.md` FR-8 and Success Metric "Reproducibility."

---

## RoadMap

### Phase 1: Methodology & Foundation

*(Detailed above. Status: **Complete** as of July 9, 2026.)*

**Core Objective:** Establish a documented, auditable foundation — problem framing, business case, product requirements, and methodology — before any data work begins.

**Key Tasks:**
- Define the core problem and articulate why it matters now (`Problem_statement.md`)
- Establish business objectives, stakeholders, and requirements (`BRD.md`)
- Define product scope, user stories, and functional requirements (`PRD.md`)
- Document the methodology governing all future phases (this section)
- Identify open questions and risks to resolve in later phases

**Deliverables:**
- `Problem_statement.md`
- `BRD.md`
- `PRD.md`
- `README.md` (initial draft)
- `RoadMap.md` (this document)

**Entry Criteria:** The triggering event (Virginia SB84 taking effect) has been identified as worth investigating, and a decision has been made to pursue the project.

**Exit Criteria:** All four planning documents exist, are internally consistent, and the methodology governing data sourcing, scoring, and validation is explicitly written down. ✅ *Met.*

---

### Phase 2: Preparation & Data Foundation

**Core Objective:** Source, validate, and prepare every dataset the scoring model depends on, and stand up the technical environment the rest of the project will run in.

**Key Tasks:**
- Locate and download the Virginia crash/pedestrian-incident dataset from VDOT or Virginia DMV
- Verify the data's granularity (intersection vs. segment) and document the finding, resolving the open question from `PRD.md` §13
- Locate and download Virginia K-12 school location data
- Clean both datasets: standardize location fields, handle missing values, remove duplicates
- Geocode and spatially join school locations to the crash/incident data
- Set up the Python environment and repo structure (`data/`, `src/` or `notebooks/`, `docs/`, `outputs/`)
- Run exploratory data analysis to confirm the data shows expected patterns (e.g., time-of-day clustering, known high-incident regions)
- Cross-check early patterns qualitatively against Maryland's publicly reported program locations as an initial sanity check

**Deliverables:**
- Cleaned, joined dataset ready for feature engineering
- Data quality report (including the resolved granularity question)
- Repo scaffold with documented folder structure
- Short EDA summary (findings, anomalies, any data limitations discovered)

**Entry & Exit Criteria:**
- **Entry:** Phase 1 deliverables complete and methodology agreed.
- **Exit:** Clean, validated datasets exist and are joinable; data granularity is confirmed and documented; repo scaffold is in place; no blocking data-access issues remain.

---

### Phase 3: Execution & Model Development

**Core Objective:** Build the risk-scoring pipeline end-to-end — from cleaned data to a ranked, explainable output and a visual map.

**Key Tasks:**
- Engineer the four factor groups: incident density, pedestrian-involvement rate, time-pattern concentration, school-zone proximity
- Implement the scoring method (weighted heuristic or gradient-boosted model, per the methodology decision rule in this document)
- Expose and verify per-location factor contributions to satisfy the explainability requirement (`BRD.md` BR-2, `PRD.md` NFR-2)
- Generate the ranked list of top-N highest-risk locations
- Build the interactive map visualization
- Run the two validation checks defined in the Methodology section (external sanity check against Maryland precedent; manual spot-check of top/bottom ranked locations)
- Write inline methodology and limitations notes alongside the code, not as a separate afterthought

**Deliverables:**
- Working, reproducible scoring pipeline (code)
- Ranked output (table/CSV) with contributing factors shown per location
- Interactive map (HTML) visualizing statewide risk concentration
- Validation notes documenting the outcome of both sanity checks

**Entry & Exit Criteria:**
- **Entry:** Phase 2 exit criteria met — clean data, resolved granularity, working environment.
- **Exit:** Pipeline runs end-to-end from raw public data to ranked output without manual intervention; every top-10 location has a documented, data-backed explanation for its rank; both validation checks have been run and their results recorded.

---

### Phase 4: Testing, Documentation & Launch

**Core Objective:** Verify the output holds up to scrutiny, bring all documentation to a consistent final state, and publish the project as a complete, reviewable public artifact.

**Key Tasks:**
- Manually review top-ranked locations a second time for plausibility, cross-referencing any available public reporting
- Verify every data source is correctly named, linked, and matches what's actually used in the pipeline
- Reconcile `README.md`, `BRD.md`, `PRD.md`, `Problem_statement.md`, and `RoadMap.md` for consistency (no contradicting claims or stale open questions)
- Run a reader test: have someone unfamiliar with the project read the README and methodology, then summarize the project back — flag anything they misunderstood
- Finalize repo structure, confirm the map and outputs render correctly from a fresh clone
- Publish the repository and confirm public accessibility

**Deliverables:**
- Finalized, internally consistent documentation set (all five `.md` files)
- Publicly accessible GitHub repository with working code, ranked output, and map
- Record of the reader test and any resulting fixes

**Entry & Exit Criteria:**
- **Entry:** Phase 3 exit criteria met — working pipeline, ranked output, and map all validated.
- **Exit:** Repository is public, documentation is fully consistent, the reader test surfaces no unresolved confusion, and the project is ready to be referenced or shared externally.

---

## Indicative Timeline

| Phase | Duration | Status |
|---|---|---|
| Phase 1: Methodology & Foundation | Complete | ✅ Done — July 9, 2026 |
| Phase 2: Preparation & Data Foundation | 2–3 days | Not started |
| Phase 3: Execution & Model Development | 2–3 days | Not started |
| Phase 4: Testing, Documentation & Launch | 1–2 days | Not started |

## Changelog

| Date | Change | Reason |
|---|---|---|
| July 9, 2026 | Initial version created | Project kickoff following Phase 1 completion |
