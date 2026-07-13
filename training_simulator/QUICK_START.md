# Training Simulator — Quick Start Guide

## Prerequisites

- Python 3.7+
- Tkinter (included with most Python distributions)
- htDash installed with valid `data/`, `utils/`, `config/` directories
- About 5 minutes to run your first simulation

## Installation

The simulator is already built into the `training_simulator/` folder. No installation needed.

## Launch the Simulator

```bash
# From project root
python training_simulator/simulator_app.py
```

A Tkinter window will open.

## Your First Simulation (5 minutes)

### Step 1: Create a Cohort (30 seconds)

1. Click **"Create Simulation Cohort (10 patients)"**
2. Wait for success message
3. You now have 10 fresh patients ready in `data/ranipet/patients/`

### Step 2: Run Through Pre-Activation Events (2 minutes)

1. Click **"Continue Simulation"**
2. Review the "Patient Status" grid — all 10 patients should show "unassigned" status
3. Check the "Today's Instructions" panel — it shows events due for all patients today
4. You should see:
   - `informed_consent` (all patients)
   - `exp_device_install` (experimental patients only)
   - `activation` (all patients)
5. Click **"▶ Run (Next Day)"** three times to advance to Day 1 of activation

### Step 3: File Events in Real htDash (2 minutes)

Now you practice using htDash to file the events the simulator told you about.

1. **Open htDash in a browser**:
   ```
   http://localhost:5000
   ```
   (or whatever your htDash server URL is)

2. **Log in as therapist**:
   - Login ID: `RP-HS-IT`
   - Password: `RANIPET@2026it`

3. **File Informed Consent for one patient**:
   - Click "Patients" → find a patient with ID `HOCMCV###` (starting with `HOCMCV0##` are the simulator's 10 patients)
   - Click the patient's name
   - Click "Informed Consent" event
   - Fill in: consent date (today), PDF form (any PDF file), any notes
   - Click "Save"

4. **File Activation for the same patient**:
   - Scroll down to the "Activation" event
   - Click it
   - Select "Yes, training completed"
   - Fill in: activation date, training start/end times (same day), VCG Group (control only)
   - Click "Save"

### Step 4: Verify Your Work (30 seconds)

1. Back to the simulator app
2. Click **"🔍 Verify Now"** (if implemented; currently a placeholder)
3. Or check the state ledger manually:
   - Open `training_simulator/state/simulation_state.json`
   - Look at the `expected_events` array — you should see entries for "informed_consent" and "activation"
   - Each entry tracks expected vs. actual completion

## Simulator Workflow

### Main Screen Layout

```
┌────────────────────────────────────────────────────────────┐
│  Simulation Running                              Day: 5    │
├────────────────────────────────────────────────────────────┤
│  ▶ Run (Next Day) | 🔍 Verify All | 📊 Report | Back     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Patient Status (10 patients)                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ ID          Group  Status  Days  Next Due          │ │
│  │ HOCMCV### exp    active  3    home_visit_d02     │ │
│  │ HOCMCV### exp    active  3    home_visit_d02     │ │
│  │ ...                                                 │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Today's Training Scenarios & Instructions                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ [1] PATIENT: HOCMCV002 (EXPERIMENTAL)             │ │
│  │     HOME VISIT: Home Visit Day 02                  │ │
│  │     Session time: 10:00–11:30 AM                  │ │
│  │     Training completed: YES                        │ │
│  │                                                    │ │
│  │ [2] PATIENT: HOCMCV003 (EXPERIMENTAL)             │ │
│  │     ADVERSE EVENT: Joint pain (Consultant level)  │ │
│  │     Training paused: YES                          │ │
│  │     Suggested fields:                             │ │
│  │       • severity: Consultant                      │ │
│  │       • training_blocked: true                    │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Button Actions

| Button | Action |
|--------|--------|
| **▶ Run (Next Day)** | Advance by 1 day: shift `activationDate`, generate rich training scenarios with suggested field values, show instructions |
| **🔍 Verify All** | Scan all patients' `protocol_events.json` and compare against expected events. Generate detailed report with verdicts. |
| **📊 Report** | Show verification results: pass rate %, events done on-time/late/missing per patient |
| **Back** | Return to setup screen (can reset cohort from there) |

## Understanding the Instructions

Each instruction card tells you:
- **Patient ID** (e.g., `HOCMCV002`)
- **Event name** (e.g., "Home Visit Day 02")
- **Status** (e.g., "Due today", "2 days overdue")
- **What to do in htDash**: File the event with these suggested field values

Example:
```
[HOCMCV002] Home Visit Day 02 — Due today
  File a Home Visit:
  Session start: 2026-07-15 10:00
  Session end: 2026-07-15 11:30
  Training completed: YES
  Notes: Optional
```

**Your job**: Replicate this in htDash. The simulator checks that you filed it correctly.

## Scenario Injection

After a few days of running, the simulator may inject randomized training scenarios:

- **Adverse Events**: "Patient reported increased muscle soreness" → file as adverse event
- **Robot Issues** (experimental only): "Device Pluto not charging" → file robot issue call
- **Patient Calls**: "Check on exercise progress" → file as patient call
- **Device Issues** (experimental only): "Modem connectivity lost" → file device issue call

Each scenario has suggested field values ("answer key") that you should replicate in htDash.

## Verify All Report

After filing events in htDash, press **🔍 Verify All** to see how well you did:

### Report Screen Shows

**Overall Results**:
- **Pass Rate**: Green (≥90%) / Orange (≥50%) / Red (<50%)
- **Total Events**: How many events were expected
- **Done on time**: ✓ Filed on the correct day
- **Done late**: ⚠ Filed after the due date
- **Missing**: ✗ Expected but never filed in htDash
- **Wrong fields**: ✗ Filed but with incorrect data (e.g., wrong time, duration, severity)

**Per-Patient Breakdown**:
Each patient shows individual score and event breakdown:
```
HOCMCV002 (EXP): 85% (17/20)
  On-time: 17 | Late: 0 | Missing: 2 | Wrong: 1
```

### Verdict Meanings

| Verdict | Meaning | Example |
|---------|---------|---------|
| ✓ Done on time | Event filed on the correct day with correct fields | You filed Home Visit D02 on Day 2 as instructed |
| ⚠ Done late | Event filed after its window closed | You filed Home Visit D02 on Day 5 (window was Days 2–3) |
| ✗ Missing | Event was due but never filed | Patient call was instructed but no entry in htDash |
| ✗ Wrong fields | Event filed but with incorrect suggested values | You filed the call but used wrong duration (5 min instead of 12) |

---

## Troubleshooting

### "patient not found" error
**Cause**: Cohort creation failed or patient folders weren't properly initialized.
**Fix**: Check `data/ranipet/patients/` — should have 10 folders `HOCMCV###` (where `###` are numbers). If not, click "Reset Simulation" and create a new cohort.

### Instructions panel is empty
**Cause**: No events are due "today" (their windows haven't opened yet).
**Fix**: Press **Run** a few times to advance time. Once `activationDate` is shifted into the past relative to today, events will have open windows and appear as due.

### Can't find patients in htDash
**Cause**: htDash is running against a different hospital folder or `data/` tree than the simulator.
**Fix**: Ensure both are using the same `data/ranipet/` directory. Check `config.py` `DATA_ROOT` and `HOSPITAL_FOLDER_MAP`.

### Tkinter import error (Linux/Mac)
**Cause**: Tkinter not installed.
**Fix**:
  - Linux (Debian/Ubuntu): `sudo apt-get install python3-tk`
  - macOS: `brew install python-tk` or reinstall Python via Homebrew with `--with-tcltk`

## Keyboard Shortcuts

None defined yet. Use mouse only.

## Advanced Usage

### Reproducible Scenarios (Testing)

```python
from training_simulator.scenarios import ScenarioGenerator

# Same seed = same scenario sequence
gen = ScenarioGenerator(seed=42)
```

### Manual State Inspection

The simulator writes everything to `training_simulator/state/simulation_state.json`:

```json
{
  "version": 1,
  "cohort": {
    "patient_ids": [
      {"homer_id": "HOCMCV###", "group": "experimental", "training_side": "Right"},
      ...
    ],
    "active": true
  },
  "simulation": {
    "simulated_day_number": 5,
    "session_start": "2026-07-13T14:32:00"
  },
  "expected_events": [
    {
      "day": 1,
      "patient_id": "HOCMCV###",
      "protocol_event_id": "activation",
      "suggested_values": {...},
      "verified": false,
      "verdict": null
    },
    ...
  ],
  "logs": [...]
}
```

You can inspect this JSON to see exactly what the simulator expects.

## Tips for Trainers

- **Slow start**: Press Run once, then have trainees file just 1–2 events in htDash. Verify. Repeat. This paces learning.
- **Intentional mistakes**: Skip an event deliberately, press Verify. See how the simulator flags it as "missing".
- **Scenario replay**: Use `seed=` parameter in scenarios generator to make training reproducible across cohorts.
- **Multi-cohort**: Create multiple simulators (different state files) for different training groups.

## Contact & Support

For issues or feature requests, refer to the `IMPLEMENTATION_SUMMARY.md` in the same directory.

---

**You're ready!** Launch the app and start training. Good luck! 🎓
