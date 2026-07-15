# Norfolk Pilot Implementation Guide

This guide covers the executable implementation of Phases 0–3 in [`execution.md`](execution.md). The pipeline creates run-isolated, hash-verified evidence under `outputs/runs/<run-id>/`. It does not calculate or publish a risk score; scoring begins in Phase 4.

## Environment setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The validated implementation environment uses Python 3.11 with the exact package versions in `requirements.txt`.

## Test commands

Run the complete suite before every phase handoff:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

To retain JUnit evidence for a phase:

```powershell
.\.venv\Scripts\python.exe -m pytest --junitxml "outputs/test-evidence/phase0.xml"
```

Replace `phase0.xml` with the appropriate phase number. A handoff is invalid unless the full suite passes.

## Pipeline commands

Create a new isolated run and execute Phase 0:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m sentinel_va.cli --config configs/norfolk_pilot.json --run-id <unique-run-id> --from-phase 0 --through-phase 0
```

Continue the same immutable configuration through later phases:

```powershell
.\.venv\Scripts\python.exe -m sentinel_va.cli --config configs/norfolk_pilot.json --run-id <same-run-id> --from-phase 1 --through-phase 1
.\.venv\Scripts\python.exe -m sentinel_va.cli --config configs/norfolk_pilot.json --run-id <same-run-id> --from-phase 2 --through-phase 2
.\.venv\Scripts\python.exe -m sentinel_va.cli --config configs/norfolk_pilot.json --run-id <same-run-id> --from-phase 3 --through-phase 3
```

Changing the configuration invalidates continuation of an existing run. Start a new run instead.

## Phase outputs

| Phase | Principal outputs |
|---|---|
| 0 | Manifest, structured log, environment record, handoff record. |
| 1 | Source register, raw/archive hashes, baseline summary, descriptive tables. |
| 2 | Clean crash table, exclusion ledger, combined school inventory, validated active K–12 layer, school audit layer, duplicate-name ledger, quality report. |
| 3 | Location decision, candidate cells, crash-to-cell membership, feature table, data dictionary, sensitivity configuration, quality report. |

## Frozen Phase 3 location unit

The primary unit is a deterministic 250 m fixed grid in `EPSG:26918` (NAD83 / UTM Zone 18N). The source coordinates remain identified as `EPSG:4326`. The grid is an analytic aggregation proxy selected because authoritative intersection topology is not present in the repository. It is not an engineered intersection, legal school zone, or deployment unit.

The 200 m and 300 m grid variants are reserved for Phase 5 sensitivity analysis and may not silently replace the primary output.

## Data and publication limitations

- The configured Norfolk coordinate envelope is a conservative data-quality envelope, not a legal municipal boundary.
- The available ADT file is transfer-limited; the implementation hard-disables exposure-adjusted metrics.
- Third-party school POI source identity/licensing remains subject to final publication verification.
- Phase 3 outputs are unscored research artifacts and must not be circulated as camera recommendations or legal eligibility determinations.
