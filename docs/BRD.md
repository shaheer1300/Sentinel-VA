# Business Requirements Document (BRD)

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
| Reviewers | — |
| Related Documents | Problem_statement.md, PRD.md, README.md |
| Revision History | v1.0 — Initial draft — July 9, 2026 |

## 2. Executive Summary

Virginia's SB84 (effective July 1, 2026) authorizes AI-assisted camera enforcement of stop-sign and crosswalk violations in school zones and other high-risk pedestrian areas. Site selection for this kind of program has historically been reactive, driven by incidents rather than data. This project defines the business case for an independent, public-data-driven risk-scoring tool that identifies and ranks Virginia intersections by pedestrian and violation risk, giving municipalities and enforcement-technology vendors a proactive, defensible starting point for deployment planning.

See `Problem_statement.md` for the full problem framing this BRD is built on.

## 3. Business Objectives

| ID | Objective |
|---|---|
| BO-1 | Produce a credible, publicly-defensible ranking of Virginia intersections/school zones by pedestrian and violation risk. |
| BO-2 | Demonstrate that proactive, pattern-based site selection is feasible using only public data — no proprietary crash or citation data required. |
| BO-3 | Create a reusable methodology that generalizes to other states as similar legislation is adopted (Maryland precedent already exists; North Carolina, Pennsylvania, Delaware are considering similar bills). |
| BO-4 | Produce documentation and analysis rigorous enough to be useful to a real decision-maker (municipal traffic safety office, state DOT, or an enforcement-technology company evaluating market entry) — not a toy demo. |

## 4. Background and Business Context

Maryland's automated stop-sign enforcement program (piloted in Prince George's County, now expanded to ten-plus municipalities) has shown violation reductions of up to 70% within months of camera installation. That program's site selection was largely reactive — the flagship deployment followed a 2023 incident in which two children were struck and killed near a school.

Virginia now sits where Maryland sat several years ago: legally enabled, but without an established, data-driven method for deciding where to act first. This BRD defines the business requirements for a tool that closes that gap using historical Virginia crash data, pedestrian-involvement records, and school-zone proximity — before, not after, the next incident.

## 5. Scope

### 5.1 In Scope
- Aggregation and analysis of public Virginia crash/pedestrian-incident data (VDOT / Virginia DMV Traffic Crash Facts)
- Aggregation of public Virginia K-12 school location data
- A risk-scoring methodology combining historical incident density, pedestrian involvement, time-of-day/day-of-week patterns, and school-zone proximity
- A ranked output (list + map) of highest-priority intersections/corridors
- Supporting documentation (problem statement, BRD, PRD, README) explaining the methodology and its limitations

### 5.2 Out of Scope
- Computer-vision detection of live traffic violations from camera footage
- Any integration with, access to, or data from a specific enforcement vendor's proprietary systems
- Legal, procurement, or engineering review required before actual camera deployment
- Real-time or streaming data processing (this is a batch, point-in-time analysis)

## 6. Stakeholders

| Stakeholder | Interest |
|---|---|
| Author (Shaheer Ahmad) | Delivers a rigorous, credible analysis project demonstrating spatio-temporal risk modeling applied to a live public-safety problem |
| Municipal traffic safety / public works departments (illustrative audience) | Would use output as a starting point for camera-siting discussions |
| State DOT / legislative bodies (illustrative audience) | Interested in evidence that enablement legislation is being acted on responsibly |
| Enforcement-technology vendors operating in this market (e.g., Obvio, illustrative context only — no affiliation implied) | Represent the type of organization for whom this class of analysis is operationally relevant when evaluating new-state market entry |

## 7. Business Requirements

| ID | Requirement | Priority |
|---|---|---|
| BR-1 | The analysis must use only publicly available data sources, with each source documented and linked. | Must Have |
| BR-2 | The risk score must be explainable — a reader must be able to see *why* an intersection ranked highly, not just the final number. | Must Have |
| BR-3 | The methodology must be generalizable to any U.S. state with comparable public crash and school-location data. | Should Have |
| BR-4 | Output must be consumable by a non-technical reader (ranked list + visual map), not just a data scientist. | Must Have |
| BR-5 | The project must clearly disclose its limitations and avoid overstating precision or implying operational/production readiness. | Must Have |
| BR-6 | The project must not misrepresent affiliation with, or endorsement by, any named company or government body. | Must Have |

## 8. Assumptions

- Virginia crash and pedestrian-incident data at intersection/segment granularity is available through VDOT or Virginia DMV public data channels.
- Public school location data for Virginia is available and sufficiently accurate for proximity analysis.
- Maryland's publicly reported program outcomes are a reasonable proxy for what "high-risk, high-impact" looks like in a comparable jurisdiction.

## 9. Constraints

- Solo project, public data only — no access to proprietary citation, insurance, or vendor telemetry data.
- Timeline: single-author build, targeted for completion within 1–2 weeks of this document's date.
- No live camera footage or violation-detection data is available or in scope.

## 10. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Public Virginia crash data lacks intersection-level granularity | Reduces precision of scoring | Fall back to road-segment or corridor-level analysis; document the limitation explicitly |
| Risk score is misread as a guarantee of future incidents | Reputational / credibility risk | Explicit limitations section in README and PRD; frame as prioritization aid, not prediction of certainty |
| Perceived overreach in referencing a named company | Misrepresentation risk | No claim of affiliation, commission, or partnership anywhere in the documentation |

## 11. Success Metrics

| Metric | Target |
|---|---|
| Data sources used | 100% public, documented, and linked |
| Explainability | Every top-10 ranked location has a stated reason (data-backed) for its rank |
| Reader comprehension | A non-technical reader can explain, in their own words, what the tool does and why, after reading the README alone |
| Methodology reuse | Approach is documented clearly enough to be re-run on a different state's data with minimal changes |

## 12. Timeline (Indicative)

| Phase | Duration |
|---|---|
| Data sourcing and cleaning | 2–3 days |
| Scoring methodology and model | 2–3 days |
| Map/visualization and output | 1–2 days |
| Documentation and review | 1–2 days |

## 13. Appendix

Related documents: `Problem_statement.md`, `PRD.md`, `README.md`.
