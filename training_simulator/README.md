# htDash Training Simulator

A standalone Python GUI application for training therapists and engineers on the htDash clinical dashboard.

## Features

- **10-Patient Cohort**: Automatically creates 5 experimental + 5 control simulated patients
- **Protocol Timeline**: Advances through 187 days of protocol events (A0 → A2 assessment)
- **Scenario Injection**: Randomized adverse events, robot issues, and patient calls to test real-world scenarios
- **Live Verification**: Checks trainee's actual htDash filings against expected events
- **Progress Tracking**: Maintains persistent ledger of expected vs. actual events

## Quick Start

### Prerequisites

- Python 3.7+
- Tkinter (included with most Python distributions)
- htDash installed locally (shares `data/`, `utils/`, `config/` modules)

### Running the Simulator

```bash
cd training_simulator
python simulator_app.py
```

Or from project root:

```bash
python -m training_simulator.simulator_app
```

## Workflow

1. **Create Cohort** → 10 fresh simulated patients seeded in `data/ranipet/patients/`
2. **Run (advance day)** → shifts `activationDate` backward, generates rich scenario instructions with suggested field values
3. **Trainee performs actions in htDash UI** → files informed consent, activation, home visits, calls, assessments, adverse events, device issues, etc. using the suggested values
4. **Verify All** → compares what trainee filed against what the simulator expected, produces detailed verdict report
5. **Report** → summary of pass/fail per patient with overall pass rate (% of events filed correctly)

## Architecture

- **state_store.py** — Persistent ledger of expected events + simulation progress
- **patient_seed.py** — Creates 10 fresh patients (mirrors `scripts/reset_test_patient.py`)
- **protocol_engine.py** — Date advancement + due-event calculation (mirrors `scripts/shift_activation.py`)
- **scenarios.py** — Randomized scenario templates (adverse events, device issues, calls)
- **verification.py** — Diffs expected events against `protocol_events.json`
- **simulator_app.py** — Main Tkinter GUI

## State & Data

- **Simulator state**: `training_simulator/state/simulation_state.json`
  - Cohort patient IDs
  - Day counter
  - Full expected-event history + verdicts

- **Patient data** (shared with htDash):
  - `data/ranipet/patients/<homer_id>/` — patient folders
  - `data/ranipet/patients/<homer_id>/<homer_id>.json` — patient metadata
  - `data/ranipet/patients/<homer_id>/protocol_events.json` — event records

## Key Algorithms

### Date Advancement (`advance_one_day()`)

For each activated, not-training-ended patient:

1. Shift `activationDate` backward by 1 calendar day
2. Re-read `protocol_events.json`
3. For each `incomplete` entry with `reference: "activation"` and a `window`:
   - Recompute `scheduled_date` using the new activation date + window offsets
   - Preserve time-of-day from the original window
4. Write updated patient metadata and protocol events
5. Call `populate_activation_dates()` to fill any still-null activation-referenced stubs

This approach (vs. manipulating the system clock) ensures:
- Real `derive_status()` works with the actual system time
- Only open stubs are recomputed (completed events are immutable audit records)
- Exactly matches the mechanism in `scripts/shift_activation.py`

### Verification

For each expected event in the ledger:

1. Search `protocol_events.json` for matching entry (by `protocol_event_id` or free-event type)
2. Check if `completion_date` falls within expected window
3. Verdict:
   - ✓ `done_on_time` — filed on the expected day
   - ⚠ `done_late` — filed after the window closed
   - ✗ `missing` — no entry found
   - ✗ `wrong_fields` — entry present but missing/invalid fields

## Testing

Manual smoke test:

```bash
# 1. Seed the cohort
python simulator_app.py
# → Click "Create Simulation Cohort"

# 2. Advance a few days
# → Click "▶ Run" several times

# 3. Open htDash in a browser (same data/ranipet folder) and manually file events
# → Log in as RP-HS-IT (therapist)
# → Activate one patient, file home visits, etc.

# 4. Verify in the simulator
# → Click "🔍 Verify Now"
# → Check the report
```

## Limitations & Future Work

- Scenario injection currently templates only, no auto-filing
- Report generation is placeholder
- Event-by-event scenario instruction UI needs refinement
- No support for multi-hospital workflows yet (ranipet only)
- No device inventory mock (devices in real htDash inventory used as-is)

## Troubleshooting

**"patient not found"** → Cohort creation failed; check `data/ranipet/patients/` for folder creation errors.

**"protocol_events.json not found"** → Patient folder exists but protocol events weren't initialized; run `patient_seed.py` manually.

**Events not recomputing** → Check that `config/study_protocol.json` is present and readable; `event_index` must build successfully.

**Tkinter import error** → On Linux, install `python3-tk`; on macOS, reinstall Python via Homebrew with `--with-tcltk`.
