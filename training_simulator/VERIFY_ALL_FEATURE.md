# Verify All Feature — Complete Training Verification

## Overview

The **Verify All** button provides comprehensive training assessment by comparing all expected events against actual htDash filings.

## How It Works

### Flow

```
1. Trainee presses "▶ Run (Next Day)"
   ↓ Simulator advances time, generates scenarios
   ↓ Scenarios show in instructions panel with suggested field values
   ↓
2. Trainee opens htDash in browser
   ↓
3. Trainee files each event with exact suggested values
   ↓
4. After filing events, trainee returns to simulator
   ↓
5. Trainee presses "🔍 Verify All"
   ↓ Simulator reads protocol_events.json for all 10 patients
   ↓ Compares expected events vs. actual filings
   ↓ Generates verdict: done-on-time / done-late / missing / wrong-fields
   ↓
6. Report screen shows pass rate, breakdown per patient
   ↓
7. Click "View Details (JSON)" to inspect full ledger
```

## Verdict Categories

Each expected event gets one verdict:

### ✓ Done On Time
- **Condition**: Event filed and `completion_date` falls within expected day window
- **Example**: Instructed to file activation on Day 1 → filed on Day 1 ✓
- **Score**: Full credit

### ⚠ Done Late
- **Condition**: Event filed but `completion_date` falls outside (after) expected window
- **Example**: Instructed to file home visit on Day 2 → filed on Day 5 ⚠
- **Score**: Partial credit (shows pattern of delays)

### ✗ Missing
- **Condition**: Event expected in ledger but no matching entry in patient's `protocol_events.json`
- **Example**: Scenario called for adverse event → not filed in htDash ✗
- **Score**: No credit

### ✗ Wrong Fields
- **Condition**: Event filed but required fields missing or mismatched
- **Example**: Call was instructed for 12 minutes, audio mode → filed as 5 minutes, video mode ✗
- **Score**: Partial credit (shows execution error)

## Report Screen

### Overall Statistics

```
Pass Rate: 87.5% (Excellent!)
Total Events: 80
  ✓ Done on time: 70
  ⚠ Done late: 5
  ✗ Missing: 4
  ✗ Wrong fields: 1
```

**Pass rate = (done_on_time / total) × 100%**

Color coding:
- **Green** (≥90%) → Excellent
- **Orange** (70–89%) → Good
- **Orange** (50–69%) → Fair  
- **Red** (<50%) → Needs work

### Per-Patient Breakdown

Each patient shows:
- **Pass rate** for that patient
- **Event count**: on-time / late / missing / wrong
- Example:
  ```
  HOCMCV002 (EXP): 85% (17/20)
    On-time: 17 | Late: 0 | Missing: 2 | Wrong: 1
  ```

### Buttons

| Button | Action |
|--------|--------|
| **Back to Simulation** | Return to main screen, continue running |
| **View Details (JSON)** | Open a new window showing full `simulation_state.json` for inspection |
| **Reset Simulation** | Clear cohort and start over |

## State Ledger (simulation_state.json)

All expected events stored with their verdicts:

```json
{
  "expected_events": [
    {
      "day": 1,
      "patient_id": "HOCMCV002",
      "protocol_event_id": "activation",
      "free_type": null,
      "suggested_values": {...},
      "verified": true,
      "verdict": "done_on_time",
      "actual_completion_date": "2026-07-14T10:00"
    },
    {
      "day": 2,
      "patient_id": "HOCMCV002",
      "protocol_event_id": "adverse_event",
      "free_type": "adverse_event",
      "suggested_values": {
        "description": "Joint pain",
        "severity": "Consultant",
        "training_blocked": true
      },
      "verified": true,
      "verdict": "missing",
      "actual_completion_date": null
    },
    ...
  ]
}
```

## Verification Algorithm

For each expected event:

```python
1. Search protocol_events.json for matching entry:
   - By protocol_event_id (for scheduled events)
   - By free_type + file order (for free events like adverse_event)

2. If found:
   a) Extract completion_date from filing
   b) Check if completion_date falls within expected day window
   c) Check if key fields match suggested values (basic check)

   Verdict:
   - Within window → "done_on_time"
   - After window → "done_late"
   - Fields mismatch → "wrong_fields"
   - Entry present but no completion_date → "wrong_fields"

3. If not found:
   - Verdict: "missing"
```

## Use Cases

### 1. Self-Paced Learning
Trainee can:
- Run through several days of scenarios
- File events at their own pace
- Press Verify at the end to see score
- Identify weak areas (many "missing" → rushed)

### 2. Structured Training Program
Instructor can:
- Have cohort complete Week 1 (e.g., Days 1–7)
- Run Verify All to see class average
- Provide feedback ("Most people missed patient calls on Day 5")
- Have trainees repeat weak scenarios

### 3. Competency Assessment
Trainee needs to pass 80%+ on:
- Protocol event filings (activate, home visits, prescriptions, assessments)
- Free events (patient calls, adverse events, discontinuation)
- Field accuracy (correct times, durations, severity levels)

## Limitations

- **Field-level validation**: Currently checks only `completion_date` (day window). Does not deeply inspect all field values (times, durations, descriptions). Future enhancement: pass suggested_values and validate against actual entry fields.
- **No cross-event validation**: Does not check if one event's fields affect another (e.g., "Was follow-up call date within 1 day of adverse event?"). Could be added later.
- **Assumption of 24-hour windows**: Verdict windows assume each day is 24 hours (00:00–23:59). If instructed for a specific time (e.g., 10:00 AM), current algorithm is coarse. Fine-grained time validation possible but requires more setup.

## Example Scenario

**Scenario Generated**:
```
[1] PATIENT: HOCMCV002 (EXPERIMENTAL)
    ADVERSE EVENT: Patient reported muscle soreness
    Suggested fields:
      • description: "Patient reported increased muscle soreness post-training"
      • action_taken: "Discussed with patient and provided modified exercise recommendations"
      • training_blocked: true
      • severity: "Consultant"
```

**Trainee Files in htDash**:
- Adverse Event modal:
  - Description: "Increased muscle soreness after training" (close enough)
  - Action taken: "Discussed and provided modified exercises" ✓
  - Training blocked: ✓ Yes
  - Severity: "Consultant" ✓

**Verdict**: `done_on_time` ✓
- Description close enough (reasonable variance allowed)
- Core fields match
- Filed on same day as instructed

---

## Tips for Trainers

1. **Slow-and-verify**: Have trainees file 1–2 days of scenarios, then Verify All to see scores before advancing.

2. **Discuss verdicts**: After verification:
   - "Why did you miss this call?" (missing verdict)
   - "Why was your timing off?" (done_late verdict)
   - "Did you notice the field mismatch?" (wrong_fields verdict)

3. **Track trends**: Each cohort's average pass rate shows how well training is working. Target ≥85% for competency.

4. **Use JSON details**: Show trainees the full state ledger to understand what was expected vs. what was filed. Builds accountability.

---

## Next Steps

- **Field-level validation**: Enhance verification to check all suggested_values, not just dates
- **Export to CSV**: Add button to export report as Excel file for instructor records
- **Replay scenarios**: Add "Review this scenario" button to replay a specific failed event
- **Benchmarking**: Track pass rates across multiple cohorts to measure training effectiveness
