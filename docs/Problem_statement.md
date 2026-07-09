# Problem Statement

**Project:** Sentinel-VA — Proactive Risk Scoring for Virginia's Automated Traffic Enforcement Rollout
**Author:** Shaheer Ahmad
**Date:** July 9, 2026
**Status:** Draft v1.0

---

## 1. Background

On July 1, 2026, Virginia's Senate Bill 84 took effect, authorizing local governments to deploy AI-assisted cameras that detect stop-sign and crosswalk violations in school zones, work zones, and other high-risk pedestrian areas. This follows a pattern already established in Maryland, where automated stop-sign enforcement (piloted first in Prince George's County) reduced violations by up to 70% within four months of installation in participating towns.

Virginia is now the newest state in a small but growing group — alongside Maryland, and with North Carolina, Pennsylvania, and Delaware exploring similar legislation — enabling this category of enforcement technology. Localities that opt in must now decide, with limited internal data science capacity, **where** to deploy a necessarily finite number of cameras first.

## 2. The Problem

Automated enforcement technology only reduces harm at the locations where it is installed. Cameras are expensive to deploy and, under current programs, are typically funded upfront by vendors and recouped through citation revenue — meaning both vendors and municipalities have a shared incentive to prioritize locations correctly the first time.

Today, site selection for this kind of program is driven almost entirely by **reactive signals**: a fatality, a high-profile injury, or sustained community complaints. Maryland's flagship program began only after two children were struck and killed near a school in Prince George's County. This is the pattern industry practitioners describe as the core failure of traditional traffic safety approaches — engineering, education, and enforcement all tend to respond *after* harm has already occurred, not before.

There is no publicly available, systematic method for identifying **which intersections in a newly-enabled state are most likely to need enforcement first**, using data that already exists (historical crash records, pedestrian-involvement rates, proximity to schools, and time-of-day/day-of-week violation patterns) rather than waiting for the next incident to make the case.

## 3. Who Is Affected

- **Pedestrians and schoolchildren** in Virginia communities where dangerous intersections have not yet been identified or flagged for enforcement.
- **Municipalities and police departments** newly authorized under SB84, who must justify camera placement to residents, councils, and state oversight with limited internal analytics resources.
- **Enforcement-technology vendors** (e.g., companies operating in this space such as Obvio) who need a defensible, data-driven way to prioritize which Virginia communities to approach first as they expand beyond their existing Maryland footprint.

## 4. Why Now

Three conditions have converged:

1. **Legal enablement**: SB84 is eight days old at the time of writing — the addressable set of camera-eligible locations in Virginia has just gone from zero to statewide.
2. **Precedent data exists**: Maryland's 2+ years of program data (violation rates, before/after reductions, deployment criteria) provides a template for what "high-risk" looks like in similar jurisdictions.
3. **Public data availability**: Virginia crash and pedestrian-incident data (VDOT, Virginia DMV Traffic Crash Facts) and school-zone location data are both publicly accessible, meaning a credible first-pass risk model can be built without proprietary access.

## 5. Cost of Inaction

Absent a proactive prioritization method, site selection will continue to follow the reactive pattern: communities without a recent, visible tragedy will be deprioritized, even if their underlying risk (measured by near-miss and historical crash data) is comparable or higher. This delays the harm-reduction benefit the technology has already demonstrated in Maryland and puts the burden of proof on communities to produce their own tragedy before receiving attention.

## 6. What "Solved" Looks Like

A ranked, evidence-based shortlist of Virginia intersections and school zones — derived from public crash data, pedestrian-risk factors, and time-pattern analysis — that a municipality, state agency, or enforcement vendor could use as a credible starting point for deployment planning, without waiting for an incident to justify the conversation.

## 7. Out of Scope

This project does not attempt to:
- Detect actual traffic violations from camera footage (no computer-vision detection layer)
- Replace formal traffic engineering studies or legal/procurement review
- Claim affiliation with, or access to proprietary data from, any specific enforcement vendor or Virginia municipality
