# Sentinel-VA

**Where should Norfolk look first for traffic-safety improvements before someone gets hurt?**

## Current project status

Sentinel-VA is currently in documentation and data-collection. No pilot analysis, risk score, ranking, or map has been started yet.

The project will begin with a limited **Norfolk pilot study**. The pilot is a validation phase before the eventual Virginia-wide scope. It exists to test whether the data pipeline, location definition, school-proximity feature, and explainable scoring approach are workable in one city before the methodology is generalized statewide.

See the [pilot study documentation](pilot%20study/Readme.md) for the current inventory, limitations, and readiness gates.

## What this project is

Sentinel-VA is a public-data analysis project for identifying and ranking locations that may deserve traffic-safety attention. It combines historical crash patterns, pedestrian and bicycle involvement, time patterns, and proximity to schools into an explainable prioritization score.

The eventual project scope is statewide Virginia. Norfolk is the first pilot locality because its available crash data has coordinates, full timestamps, detailed injury information, and useful roadway attributes.

## Project phases

1. **Foundation and documentation** — define the problem, requirements, methodology, and limitations.
2. **Norfolk pilot preparation** — document available data, resolve data-quality issues, choose the location unit, and confirm that the required inputs can be joined.
3. **Norfolk pilot study** — build and validate a limited, explainable ranking and map. This phase has not started.
4. **Statewide expansion** — generalize the validated methodology to Virginia when comparable statewide data is available and the project budget permits it.

## What the pilot is intended to solve

The pilot is intended to answer a narrow feasibility question:

> Can public or already-acquired data support a transparent Norfolk prioritization of crash locations using historical risk factors and proactive school proximity?

The pilot is not intended to authorize, recommend, or implement a camera deployment.

## What the pilot will eventually examine

- Historical crash density and severity.
- Pedestrian and bicycle involvement.
- Fatalities and serious injuries.
- Time-of-day and day-of-week patterns.
- Proximity to active school locations.
- Traffic exposure where a complete traffic-volume extract is available.
- Spatial clusters or intersections, depending on the location unit selected during preparation.

## Current data availability

The current local inventory is documented from the files in `data/Norfolk/`:

| File | Current contents | Status |
|---|---|---|
| `Traffic_Crashes.csv` | 42,004 unique crash records; January 2016–December 2025; coordinates, datetime, severity, injury, pedestrian, bicycle, roadway, and intersection fields | Suitable for preparation; analysis not started |
| `School_information.csv` | 76 school-related POIs; 69 open and 7 closed; 39 elementary, 34 preschool, and 3 kindergarten records | Available, but includes early-childhood facilities and needs filtering |
| `MiddleandHighschool_information.csv` | 26 POIs; 23 open and 3 closed; 14 middle schools, 9 high schools, and 3 K–12 schools | Fills the secondary-school gap; needs deduplication and validation |
| `Traffic Volums ADT.json` | 2,000 GeoJSON line features from a statewide traffic-volume export | Incomplete: the file reports `exceededTransferLimit=true` and is not yet a complete Norfolk exposure layer |

The two school files together contain 102 raw records, 92 marked open and 10 marked closed. All have names, coordinates, Norfolk locality values, and a `last_verified_date` of June 1, 2026. Two names occur at multiple coordinates; these should be retained as separate campuses unless validation shows that one is a legacy record.

## Data constraints and budget limitations

The project is limited to free public sources and data already acquired. It does not currently budget for paid traffic counts, proprietary mobility data, vendor citation data, field surveys, or professional traffic-engineering studies.

The current ADT export is transfer-limited, so it cannot yet support a complete crash-rate denominator for Norfolk. The school files are third-party POI exports and their completeness, licensing, and public/private classification must be documented before final publication.

These limitations mean that an eventual pilot score must be presented as an explainable prioritization aid or historical hotspot index—not as a guaranteed prediction of future crashes or a legal determination of camera eligibility.

## What this project is not

- It does not detect violations from camera footage.
- It does not build a computer-vision system.
- It does not recommend an actual camera installation without traffic engineering, legal review, community input, and local approval.
- It is not affiliated with any camera company, vendor, city department, or state agency.
- It is not yet a finished or production-ready system.

## Eventual statewide scope

After the Norfolk pilot is documented, validated, and reviewed, the methodology may be generalized to Virginia. Statewide expansion depends on obtaining comparable crash coordinates, timestamps, school locations, roadway geometry, and—ideally—traffic exposure data for other localities.

## About

Built by Shaheer Ahmad as an independent analysis project exploring proactive, explainable approaches to traffic safety prioritization.
