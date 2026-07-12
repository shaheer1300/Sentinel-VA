# Norfolk Pilot Study

**Project:** Sentinel-VA  
**Status:** Preparation and documentation only  
**Scope:** City of Norfolk, Virginia  
**Analysis status:** Not started

## Purpose

The Norfolk pilot is a feasibility and validation phase before the eventual statewide Sentinel-VA project. Its purpose is to determine whether the currently available data can support a transparent, reproducible prioritization of traffic-safety locations using historical crashes and proactive proximity to schools.

The pilot is intentionally limited. It is not a camera-deployment recommendation, a legal eligibility determination, or a production traffic-safety system.

## Pilot scope

The eventual pilot analysis may include:

- Crash density and severity from Norfolk crash records.
- Fatalities, serious injuries, pedestrian involvement, and bicycle involvement.
- Time-of-day and day-of-week patterns.
- Distance from candidate locations to active school facilities.
- Traffic exposure if the ADT data can be re-extracted without transfer truncation.
- Spatial clusters or intersection-like locations, depending on the location-unit decision.

The pilot will not include live camera footage, violation detection, proprietary citation data, paid mobility data, field observation, legal approval, procurement, or a statewide ranking.

## Current data inventory

### `data/Norfolk/Traffic_Crashes.csv`

- 42,004 unique document numbers.
- Date range: January 1, 2016 through December 31, 2025.
- No missing values in the checked core fields: document number, datetime, route/street name, crash severity, fatalities, pedestrian fields, bicycle involvement, intersection type, latitude, or longitude.
- 821 pedestrian-involved crashes.
- 339 bicycle-involved crashes.
- Contains coordinates, full datetime, severity, injury counts, roadway conditions, intersection type, traffic-control attributes, and behavioral/environmental indicators.

This is the strongest current input for the pilot preparation phase.

### `data/Norfolk/School_information.csv`

- 76 records.
- 69 marked `open`; 7 marked `closed`.
- 39 elementary-school records.
- 34 preschool records.
- 3 kindergarten records.
- No missing names or coordinates.

This file is useful for school proximity, but preschool and childcare-like facilities must be separated from K–12 schools before scoring.

### `data/Norfolk/MiddleandHighschool_information.csv`

The added file is currently CSV, not Excel, despite the original description.

- 26 records.
- 23 marked `open`; 3 marked `closed`.
- 14 middle-school records.
- 9 high-school records.
- 3 K–12-school records.
- No missing names or coordinates.

This file fills the middle- and high-school coverage gap identified in the original school file.

### Combined school inventory

The two school files contain 102 raw records, of which 92 are marked open and 10 are marked closed. All records are labelled with locality `Norfolk` and have `last_verified_date` equal to `2026-06-01`.

Two names appear at multiple coordinates:

- James Blair middle school.
- Little Creek Elementary School.

These may represent relocated facilities, multiple campuses, or duplicate records. They should not be removed automatically; validation should determine whether each coordinate is a distinct active facility.

The school files do not provide a reliable public/private field, enrollment, school hours, attendance boundaries, or legal school-zone polygons. School proximity can therefore be used as a proactive facility-proximity feature, but not as proof that a location is inside a legally defined school zone.

### `data/Norfolk/Traffic Volums ADT.json`

This file contains 2,000 GeoJSON line features and reports `exceededTransferLimit=true`. It is a statewide extract truncated at the service transfer limit, not a complete Norfolk traffic-volume dataset. Only four records in the current file contain an explicit Norfolk jurisdiction/route match.

Before ADT is used as an exposure denominator, a Norfolk-filtered and paginated extraction must be obtained and verified. Until then, the pilot can calculate a historical hotspot index but should not claim a complete exposure-adjusted crash rate.

The filename contains the typo `Volums`; preserve the current name in documentation unless the file is deliberately renamed and all references are updated.

## Required preparation work

The following work must be completed before pilot analysis begins:

1. Combine the school files into one documented school inventory.
2. Remove closed facilities from the primary proximity feature unless they are being retained for historical context.
3. Classify records into elementary, middle, high, K–12, preschool, and kindergarten groups.
4. Validate the two repeated school names and their separate coordinates.
5. Document the provenance and licensing terms of the third-party school POI exports.
6. Re-extract ADT traffic data with a Norfolk spatial or jurisdiction filter and pagination; confirm that transfer truncation is absent.
7. Decide whether the analysis unit is a named intersection, a derived road intersection, a fixed grid, or a spatial crash cluster.
8. Preserve a data-quality report before any risk score is calculated.

## Pilot readiness gate

The pilot study may begin only when:

- The combined school inventory is validated.
- Closed and non-K–12 facilities are handled explicitly.
- The ADT data is either complete for Norfolk or excluded from the score with a documented limitation.
- The location unit is defined and reproducible.
- Core crash and school coordinates are confirmed to use compatible geographic coordinates.
- Source provenance and licensing are recorded.
- The score is framed as prioritization, not certainty or legal eligibility.

## Budget and availability constraints

The project currently relies on free public data and already acquired files. There is no budget assumption for commercial mobility feeds, vendor citation data, paid traffic counts, field surveys, or professional traffic-engineering review. Missing data must therefore be handled through transparent exclusions, documented proxies, or a later expansion phase—not silently filled with unsupported assumptions.

## Expected pilot deliverables

These deliverables belong to the future pilot-analysis phase and have not been created yet:

- Data-quality report.
- Combined and validated school-location layer.
- Defined candidate-location layer or spatial clustering method.
- Explainable feature table.
- Norfolk pilot risk-prioritization score.
- Ranked output with contributing factors.
- Interactive map.
- Limitations and validation notes.

## Transition to the full project

The statewide project should begin only after the Norfolk pilot demonstrates that the pipeline can ingest, join, score, explain, and visualize the available data without hidden data-quality or licensing problems. The statewide phase will require comparable data coverage across additional Virginia localities and a separate review of budget and source availability.
