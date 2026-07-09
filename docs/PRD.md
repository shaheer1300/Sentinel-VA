# Product Requirements Document (PRD)

**Project:** Sentinel-VA — Proactive Risk Scoring for Virginia's Automated Traffic Enforcement Rollout
**Author:** Shaheer Ahmad
**Date:** July 9, 2026
**Version:** 1.0
**Status:** Draft

---

## 1. Document Control

| Field | Value |
|---|---|
| Document Owner | Shaheer Ahmad |
| Related Documents | Problem_statement.md, BRD.md, README.md |
| Revision History | v1.0 — Initial draft — July 9, 2026 |

## 2. Overview

Sentinel-VA is a data analysis tool that scores and ranks Virginia intersections and school zones by pedestrian and traffic-violation risk, using only public data. It exists to support proactive, evidence-based decisions about where automated traffic enforcement (newly authorized under SB84) should be prioritized — replacing the current default of waiting for an incident before acting.

Full problem context: see `Problem_statement.md`. Business case and stakeholder analysis: see `BRD.md`.

## 3. Goals

| ID | Goal |
|---|---|
| G-1 | Produce a ranked list of Virginia intersections/school zones by risk score, backed by explainable, cited public data. |
| G-2 | Visualize the ranking on an interactive map that a non-technical reader can understand in under a minute. |
| G-3 | Document the methodology clearly enough that it could be reproduced or extended to another state. |
| G-4 | Ship a working, reviewable artifact (code + docs) within a 1–2 week solo build. |

## 4. Non-Goals

- Detecting actual violations from video/image data (no computer vision component)
- Building a production-grade, continuously-updated system
- Making legal, procurement, or engineering recommendations on behalf of any municipality
- Any integration with a specific vendor's live systems or proprietary data

## 5. Target Users / Personas

| Persona | Description | What they need from this tool |
|---|---|---|
| **Municipal traffic safety planner** | Works for a Virginia town/county evaluating whether to opt into SB84 camera enforcement | A defensible, data-backed shortlist of locations to start the conversation |
| **State-level policy analyst** | Tracks rollout and impact of SB84 across localities | Evidence that data-driven prioritization is possible, not just incident response |
| **Enforcement-technology evaluator** | Works at a company operating in this space, assessing where to focus outreach as Virginia opens up | A credible, independently-produced view of where risk is concentrated |
| **Technical reviewer (e.g., a hiring manager or engineering lead)** | Evaluating the author's ability to scope, build, and document a real analytical product | Clear evidence of product thinking, not just a model — problem framing, requirements, tradeoffs, and honest limitations |

## 6. User Stories

1. As a traffic safety planner, I want to see which intersections in my region rank highest for pedestrian risk, so I can prioritize where to request funding or approval for a camera.
2. As a policy analyst, I want to understand *why* a location scored highly, so I can explain the reasoning to a city council or the public.
3. As an enforcement-technology evaluator, I want a map view of statewide risk concentration, so I can identify which regions to approach first.
4. As a technical reviewer, I want to see the data sources, assumptions, and limitations stated explicitly, so I can trust the rigor of the work.

## 7. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-1 | Ingest Virginia crash/pedestrian-incident data from a public source (VDOT / Virginia DMV Traffic Crash Facts) | Must Have |
| FR-2 | Ingest Virginia K-12 school location data for proximity scoring | Must Have |
| FR-3 | Compute a risk score per intersection/segment combining: historical incident density, pedestrian involvement rate, time-of-day/day-of-week concentration, and school-zone proximity | Must Have |
| FR-4 | Output a ranked, sortable list of the top-N highest-risk locations, with the contributing factors shown per location | Must Have |
| FR-5 | Render an interactive map (e.g., via folium or kepler.gl) visualizing risk concentration statewide, viewable from a static HTML file or notebook | Must Have |
| FR-6 | Provide a written methodology section explaining how the score is calculated, in plain language | Must Have |
| FR-7 | Provide a limitations section explicitly stating what the score does and does not represent | Must Have |
| FR-8 | Structure the codebase so the pipeline (ingest → score → rank → visualize) can be re-pointed at another state's equivalent data sources with minimal changes | Should Have |

## 8. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | All data sources must be public and cited by name and link in the documentation |
| NFR-2 | The scoring methodology must be interpretable (e.g., weighted factors or a tree-based model with feature importance) rather than a black-box approach, given the target audience includes non-technical readers |
| NFR-3 | The project must run end-to-end from public data using open-source tools, with no paid API dependencies |
| NFR-4 | Documentation must be readable by a non-technical stakeholder without requiring them to read the code |

## 9. Data Sources

| Source | Purpose |
|---|---|
| VDOT / Virginia DMV Traffic Crash Facts (public crash data) | Historical crash and pedestrian-involvement records |
| Virginia Department of Education public school directory | School location and zone proximity data |
| Publicly reported Maryland program outcomes (news/vendor press releases) | Contextual benchmark for what "high-impact" deployment looks like — not used as model input |

## 10. Technical Approach (High Level)

This is a batch analytics pipeline, not a real-time system:

1. **Ingest**: pull and clean public crash and school-location datasets for Virginia.
2. **Feature engineering**: aggregate incidents by intersection/segment; compute pedestrian-involvement rate, time-pattern concentration, and distance to nearest school.
3. **Scoring**: combine features into a single interpretable risk score (weighted heuristic or a gradient-boosted model with exposed feature importances — final choice to be confirmed during build).
4. **Ranking and output**: produce a sorted table of top locations and an interactive map layer.
5. **Documentation**: methodology and limitations written up alongside the output, not as an afterthought.

Detailed technical design (data schemas, exact model parameters, repo structure) belongs in a follow-on technical design doc once data sourcing is confirmed — intentionally out of scope for this PRD, which defines *what* is being built and *why*, not the full implementation spec.

## 11. Success Metrics

| Metric | Target |
|---|---|
| Coverage | Risk scores computed for all Virginia localities with available public crash data |
| Explainability | Top-10 ranked locations each show their contributing factors, not just a final score |
| Reproducibility | A reader could follow the README and methodology section to regenerate the analysis |
| Clarity | A non-technical reader can correctly describe the tool's purpose and limitations after reading the README alone |

## 12. Milestones

| Milestone | Target |
|---|---|
| Data sourcing confirmed and cleaned | Day 3 |
| Scoring methodology implemented | Day 6 |
| Map and ranked output generated | Day 8 |
| Documentation finalized (this doc, BRD, Problem Statement, README) | Day 9 |

## 13. Risks and Open Questions

| Item | Notes |
|---|---|
| Data granularity | Open question: does Virginia's public crash data resolve to intersection level, or only road segment / route level? Determines final scoring resolution. |
| Model choice | Open question: simple weighted heuristic vs. gradient-boosted model — decision deferred to build phase based on data volume and quality. |
| Scope creep risk | Explicit non-goal to avoid building any violation-detection (CV) component, to keep the project shippable in the intended timeframe. |

## 14. Out of Scope / Future Work

- Extending the methodology to other newly-enabled states (Maryland precedent, and potentially North Carolina, Pennsylvania, Delaware if legislation passes)
- Incorporating real-time or near-real-time data feeds
- Building an actual violation-detection model, if paired with a real camera data partnership in the future

## 15. Appendix

Related documents: `Problem_statement.md`, `BRD.md`, `README.md`.
