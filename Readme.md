# Sentinel-VA

**Where should Virginia put its next traffic safety camera — before someone gets hurt, not after?**

## What this project is

On July 1, 2026, Virginia passed a law (SB84) allowing cities and counties to use AI-powered cameras to catch dangerous stop-sign and crosswalk violations, especially near schools. This is similar to programs already running in Maryland, where these cameras have cut violations by up to 70% in some towns.

But here's the catch: nobody has an easy way to decide **where to put the cameras first.** Right now, most towns only get attention after something bad has already happened — a serious crash, or worse, a child getting hurt near a school. That's backwards. The data to spot dangerous intersections *before* that happens already exists — it's just scattered across public crash reports and school records instead of being turned into something usable.

**Sentinel-VA turns that public data into a ranked list and map of the intersections in Virginia most likely to need attention — using historical crash patterns, pedestrian risk, and school proximity, instead of waiting for the next headline.**

## What it's going to solve

- **For a town or county:** a starting point for "where should we even be looking?" instead of starting from zero.
- **For state officials:** evidence that this new law can be acted on thoughtfully and proactively, not just reactively.
- **For anyone building or evaluating this kind of technology:** a clear, honest example of what proactive risk-scoring for traffic safety can look like when it's built from public data alone.

## How it works (plain version)

1. Pull public Virginia crash and pedestrian-incident records, plus public school locations.
2. Look for patterns: which intersections have a history of pedestrian danger, which times of day are riskiest, and which locations are close to schools.
3. Combine those patterns into a single, explainable risk score per location — not a black box. Every location on the ranked list comes with the reasons it ranked where it did.
4. Show the results as a simple ranked list and an interactive map.

## What this project is *not*

- It does **not** detect actual violations from camera footage. There's no video or image analysis here — this is entirely about spotting patterns in existing public safety data, not building the camera technology itself.
- It is **not** affiliated with, commissioned by, or endorsed by any traffic camera company or Virginia government body. Any companies or programs referenced (e.g., Maryland's existing camera program) are mentioned only as public context, not as partners.
- It is **not** a finished, production-ready tool. It's a first-pass analysis meant to demonstrate a proactive approach — a real deployment decision would still need proper traffic engineering review, community input, and legal process.

## Data sources

All data used is public:
- Virginia crash and pedestrian-incident records (VDOT / Virginia DMV Traffic Crash Facts)
- Virginia public school location data

No proprietary, private, or vendor-owned data is used anywhere in this project.

## About

Built by Shaheer Ahmad as an independent analysis project exploring proactive, data-driven approaches to traffic safety technology rollout. If you have questions about the methodology or want to see the underlying analysis, reach out directly.
