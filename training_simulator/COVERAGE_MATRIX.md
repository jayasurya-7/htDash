# Training Simulator — 10-Patient Coverage Matrix

This document maps each simulator patient to the htDash state-machine branches they're designed to teach. A trainee completing all 10 curricula will have practiced every major workflow path at least once.

---

## Coverage Matrix

| Patient | Group | Location | Scenario | Key Branch | Learning Goal | Days |
|---------|-------|----------|----------|---|---|
| **TRN001** | Exp | Right | **Golden Path** | None (baseline) | Baseline 187-day flow; fastest verification | 1–187 |
| **TRN002** | Ctrl | Right | **Golden Path** | None (baseline) | Control group baseline; validate normal VCG/ADL path | 1–187 |
| **TRN003** | Exp | Left | **Adverse Event** (Injury) → Pause → Resume | AE pause/clearance cycle | Most realistic scenario; teach pause mechanics + follow-up chains | 1–187 |
| **TRN004** | Exp | Right | **Robot Issue** (Pluto) → Call → Visit → Resolve | RI pause/clearance + device replacement | Device failure workflow; pause prevents training resumption | 1–187 |
| **TRN005** | Exp | Left | **Other Device Issue** (Modem) → Call → Visit | ODI (non-pause) + device swap | Contrasts with RI; shows devices can break without pausing training | 1–187 |
| **TRN006** | Ctrl | Left | **D02/D03 Broken Protocol** (Path 3) | Pause follow-up → D03 window expires | Hardest-to-catch broken protocol; teaches why pause follow-ups are time-critical | 1–50 |
| **TRN007** | Ctrl | Right | **Discontinuation** (mid-protocol) | Discontinued status + AE chains stay open | Shows read-only records + exception: AE chains completable after discontinuation | 1–100 |
| **TRN008** | Exp | Right | **Watch Lost** + **Data Upload Skip** | Device loss + skip-with-reason | Edge cases: lost-watch handling + required skip explanation | 1–187 |
| **TRN009** | Either | Right | **Assessment Edge Cases** | A1 out-of-window + A2-before-A1 auto-miss + appointment cancel/reschedule | Assessment branching; out-of-window-reason requirement + auto-miss cascade | 1–187 |
| **TRN010** | Exp | Left | **Secondary AE** (Patient-Initiated) | Patient-initiated call (vs. therapist-initiated) | AE variant: trainee learns patient-initiated flag + distinct interaction pattern | 1–187 |

---

## Detailed Scenario Descriptions

### TRN001 — Exp, Right, Golden Path

**What happens:** A normal, uneventful 187-day progression through all protocol phases.
- Days 1–3: Device setup, activation, initial prescriptions
- Days 1–28: Weekly follow-ups, exercise timing, watch records (all succeed)
- Day 29: Training completion
- Days 30–37: A1 assessment scheduled, filed on day 35 (in window)
- Days 37–183: Long quiet gap
- Day 183: A2 assessment filed (on time)
- End: Device return, watch data uploads, study complete

**Why this patient:** Baseline control for all other scenarios. Fastest to verify. Trainee learns the "happy path" without confusion from exceptions.

**Common mistakes:** Forgetting dependency locks (can't file before D29), missing watch record chain entries, misunderstanding A1/A2 window calculations.

---

### TRN002 — Ctrl, Right, Golden Path

**What happens:** Same as TRN001, but on the control group track (VCG-only, no ADL).

**Why this patient:** Validates that control group workflow is symmetric to experimental. Shows the role of group-specific exercises + prescriptions.

**Common mistakes:** Same as TRN001, plus accidentally filing experimental-only events (robot issue, other device issues — should never appear on control).

---

### TRN003 — Exp, Left, Adverse Event → Pause → Resume

**What happens:**
- Days 1–3: Normal setup + activation
- **Day 4**: Patient reports wrist pain during follow-up call → therapist files `adverse_event` with `training_blocked: true` → training enters pause
- Days 5–6: Therapist files follow-up calls + clinical visit → wrist improves
- **Day 7**: AE follow-up completed with `can_resume_from: true` → training pause clears → `trainingPausedDate` cleared + `cumulativePauseDays` incremented by 3 days
- Days 8+: Resume normal flow (days are now shifted because of 3-day pause)
- Days 21, 29, 37, 183: Adjusted dates reflect pause offset
- End: Normal completion

**Why this patient:** Most common real-world scenario. Teaches:
- AE stub creation + user fields (description, action_taken, training_blocked)
- Pause state (`trainingPausedDate` set on AE entry)
- Follow-up chains (call + visit, patient-initiated vs. therapist-initiated)
- Pause clearance (when last AE follow-up is filed with `can_resume_from`)
- Date recalculation after pause (Days are offset by cumulative pause)

**Common mistakes:**
- Forgetting `training_blocked: true` on the AE (pause never starts)
- Filing AE follow-ups out of order (chain dependencies)
- Missing `can_resume_from` field on AE follow-up (pause stays active forever)
- Not understanding that AE aliases are stable (AE01, AE02, … assigned at filing time)

---

### TRN004 — Exp, Right, Robot Issue → Call → Visit → Resolve

**What happens:**
- Days 1–10: Normal flow
- **Day 11**: Engineer receives call about Pluto malfunction → `robot_issue_call` filed with device status, `visit_required: true` → triggers `robot_issue_visit` stub
- **Day 12**: Engineer visits, finds Pluto faulty → swaps device + files `robot_issue_visit` → triggers `resolve_robot_issue_visit` stub
- **Day 13**: New device delivered, old one logged as faulty → `resolve_robot_issue_visit` filed with `can_resume_from` (same date, training never paused here)
- Days 14+: Resume with new Pluto (assignment updated in device inventory)
- End: Normal completion + device return (both old and new?)

**Why this patient:** Teaches device issue workflow (engineer-only events, not visible to therapist). Shows:
- RI call (when/how issues are reported)
- RI visit (engineer finds faulty device)
- Resolve visit (new device delivery)
- Device swapping + assignment closure
- Device logging (faulty events recorded with timestamps)
- **Contrast with AE:** RI does NOT pause training (even with `training_blocked` it shouldn't auto-pause; only AEs do)

**Common mistakes:**
- Confusing RI with AE (RI is device-only, doesn't pause training)
- Not filling `visit_required: true` on the call (visit stub doesn't auto-create)
- Forgetting device outcome on visit (Repaired / Swapped / Neither)
- Mismatching device swaps (wrong device marked as old/new)

---

### TRN005 — Exp, Left, Other Device Issue (Modem) → Call → Visit

**What happens:**
- Days 1–15: Normal flow including modem assignment
- **Day 16**: Engineer receives call about modem not charging → `other_device_issue_call` filed with device (modem), `visit_required: true`
- **Day 17**: Engineer visits, swaps modem for new one → `other_device_issue_visit` filed
- Days 18+: Resume with new modem (no training pause, no follow-up resolution step)
- End: Normal completion

**Why this patient:** Teaches that not all device issues pause training or require multi-step resolution. Shows:
- ODI is simpler than RI (call → visit, done; no resolve step)
- ODI never pauses training (even with triggered events)
- ODI device outcomes (Repaired / Swapped)
- **Contrast with RI:** RI has resolve step + `can_resume_from` field; ODI doesn't

**Common mistakes:**
- Accidentally pausing training on an ODI (should never happen; experimental-only ODI chain)
- Filing resolve_robot_issue_visit for an ODI (that event doesn't exist for ODI)
- Forgetting device outcome on the visit

---

### TRN006 — Ctrl, Left, D02/D03 Broken Protocol (Path 3)

**What happens:**
- Day 1: Activation
- **Day 2**: Home visit scheduled but therapist has to skip (emergency) → training goes on hold via AE pause
- Day 3: Therapist files AE follow-up (pause is still active)
- **Day 4**: `max(can_resume_from)` from all AEs is day 4 (after D03 window ends)
- **Trainer manually checks**: "D03 home visit is now impossible (day 4 > day 3 window); mark patient broken protocol"
- Day 4: Trainer manually sets `brokenProtocolDate` + creates synthetic `discontinuation_reminder` event
- Days 5+: Read-only record; only AE chain and assessments visible

**Why this patient:** Teaches the hardest-to-spot broken protocol path:
- D02/D03 missed events are critical (therapeutic window closes)
- If AE pause overlaps D02/D03 and clears after window end, broken protocol is automatic
- Broken protocol detection logic (when pause max > window end)
- Read-only mode + limited event visibility after broken protocol
- **Unlike paths 1–2:** This path is *not* caught by simple "date outside window" checks; it requires comparing pause clearance dates to protocol windows

**Common mistakes:**
- Not filing the AE follow-up on time (pause never clears)
- Misunderstanding when broken protocol is detected (not immediately; happens during clearance check on the AE follow-up save)
- Forgetting the discontinuation event must be filed after broken protocol is set

---

### TRN007 — Ctrl, Right, Discontinuation (mid-protocol)

**What happens:**
- Days 1–30: Normal flow
- **Day 31**: Therapist decides patient should drop out (personal reasons) → files `discontinuation` event with reason, notes, date (day 31)
- **Immediately:** Patient status → `discontinued`, record becomes read-only
- Days 32+: No overdue events shown (all are hidden), BUT:
  - If an AE had been filed before day 31, its follow-up chains remain completable (exception!)
  - Assessments (A1/A2) remain visible and can still be filed (patient may complete them after dropping out)
- Study design notes: Some discontinued patients may still complete assessments for data collection purposes

**Why this patient:** Teaches discontinuation + read-only + exception rules:
- Discontinuation sets `discontinuationDate` and makes record read-only
- "Read-only" still allows AE follow-up chains to complete (exception to normal rule)
- Assessments remain accessible (A1/A2 visibility never suppressed for discontinued)
- Filters in overdue lists: `_DISCONTINUED_VISIBLE` defines what's shown (AE chains + assessments)
- `discontinuation` event is human-editable (has date, reason, notes, attachment)

**Common mistakes:**
- Trying to file training events after discontinuation (403 Forbidden; UI prevents this)
- Forgetting that AE chains are still completable (trainee assumes everything is locked)
- Assuming discontinued = no assessments (wrong; A1/A2 can still be filed)

---

### TRN008 — Exp, Right, Watch Lost + Data Upload Skip

**What happens:**
- Days 1–20: Normal flow, watches being swapped out and replaced every 5–7 days
- **Day 21**: Watch record filed, marking right AG Watch as "Lost" (e.g., patient reports watch fell off during session)
- Days 22+: Right watch assignment closed with `lost: true` + `lost_date` set
  - Lost watch removed from available pool (can never be reassigned)
  - `watch_data_upload` stub NOT created for lost watch (no data to retrieve)
- Day 40: Another watch is replaced (normal swap, not lost) → `watch_data_upload` stub created
- Day 41: Engineer tries to retrieve data from Day 40 watch but device is inaccessible → **skips with reason:** "Device in clinic storage, not retrieved yet"
  - Fields: `skipped: true`, `notes: "reason text"` (no `.gt3x` file uploaded)
- Days 42+: Resume normal flow

**Why this patient:** Teaches device edge cases:
- Watch lost workflow (marking lost in watch_record, setting lost_date + lost flag)
- Lost watches don't trigger data uploads (no device to retrieve)
- Data upload skip-with-reason (engineer can't retrieve data but needs to document why)
- `skipped: true` on watch_data_upload + required notes when skipping
- Difference between "lost" (no device) and "normal replacement" (device exists, data should be uploaded)

**Common mistakes:**
- Accidentally creating a data upload stub for a lost watch (shouldn't happen if logic is right, but UI might not prevent it)
- Forgetting notes on a skipped data upload (reason is required)
- Trying to reassign a lost watch (should be filtered out of available pools)

---

### TRN009 — Either, Right, Assessment Edge Cases

**What happens:**
- Days 1–37: Normal flow
- **Day 37** (A1 window start = day 30, end = day 37): Therapist tries to file A1 today
  - But date field has `out_of_window_reason` showing as required (because filing on day 37 is at the edge)
  - Actually, day 37 is still in window, so no reason is required; trainee files normally
- **Day 45** (outside A1 window): Therapist files A1 assessment on day 45 (delayed)
  - Reason is required: "Clinic closure delayed session; patient catch-up"
  - Filed with reason; assessment marked "Delayed" (orange badge in UI)
- Day 46: A2 assessment stub becomes available (lazy-seeded)
- **Day 47** (before A1 marked complete): Trainer accidentally opens A2 modal without completing A1
  - UI shows: "A1 has not been completed. Filing A2 will mark A1 as missed. Continue?"
  - Trainer clicks "Cancel" (doesn't want to auto-miss A1)
  - Returns to A1, completes it properly
- **Day 52** (within A2 window): A2 assessment filed normally

**Why this patient:** Teaches assessment branching + out-of-window + auto-miss mechanics:
- A1/A2 windows are `[start_day, end_day]` from `study_protocol.json`
- Out-of-window filing requires reason (required field)
- Delayed assessments get a badge in UI for visibility
- A2-before-A1 triggers auto-miss: A1 is marked missed (with filed_at timestamp adjusted so A1 shows before A2 in timeline)
- Appointment scheduling + cancellation/reschedule workflows
- How date fields change when window logic applies

**Common mistakes:**
- Entering assessment date outside window without reason (validation blocks save)
- Attempting to file A2 before A1, then canceling (requires understanding the confirmation flow)
- Misunderstanding "delayed" (just a badge; no broken protocol or status change)
- Forgetting appointment must be scheduled before assessment can be filed (depends_on: schedule_a1_call)

---

### TRN010 — Exp, Left, Secondary AE (Patient-Initiated)

**What happens:**
- Days 1–50: Normal flow with one AE filed early (therapist-initiated after home visit)
- **Day 51**: Patient calls the clinic to report a new concern (pressure sore from device) → therapist files `adverse_event_followup` call with `patient_initiated: true`
  - Different from normal follow-up: this is triggered by patient, not therapist scheduling
  - `patient_initiated: true` stored on the entry
  - Appears in Timeline/UI with "Patient-initiated" chip
- Days 52–55: AE follow-up visit + resolution
- Days 56+: Continue normal flow

**Why this patient:** Teaches AE call variant + patient-initiated distinction:
- Some calls are therapist-initiated (scheduled follow-ups)
- Some calls are patient-initiated (patient calls about issue)
- Both go through same `adverse_event_followup` event, but `patient_initiated` flag differs
- UI shows distinct chips/badges for the distinction
- Trainee learns to distinguish who initiated the contact (required field in modal)

**Common mistakes:**
- Forgetting to set `patient_initiated: true` when the patient calls (trainee assumes all AE calls are therapist-scheduled)
- Misunderstanding the timing (patient-initiated can happen anytime, not just on scheduled days)

---

## Using This Matrix

### For Trainee Curriculum Design
When writing or reviewing a curriculum file (e.g., `exp3_track.py`), refer to this matrix to validate coverage:
- Does the patient hit the assigned branch? (Check `ScriptedEvent`s for the key events)
- Are all required fields present in the curriculum?
- Do the dates make sense for the scenario?

### For Regression Testing
After any changes to `study_protocol.json` or event schemas, re-run all 10 curricula and verify no regressions:
```bash
# (Future: automated test script)
# For now, manual verification:
# 1. Launch simulator
# 2. Set up cohort with all 10 patients
# 3. Click Verify at Day 1
# 4. Confirm all Day 1 events are expected
# 5. Advance through key days (1, 2, 3, 7, 21, 29, 37, 183)
# 6. Check Verify at end: all events should match curriculum
```

### For Trainer Briefings
When preparing to train a new therapist:
- If they need to learn AE workflows, run TRN003
- If they need to learn device issues, run TRN004 + TRN005
- If they need to learn assessments, run TRN009
- If they need the full experience, run all 10 (more time, comprehensive)

---

## Coverage Analysis

**All major branches covered:**
- ✅ AE pause/clearance (TRN003)
- ✅ RI call/visit/resolve + device replacement (TRN004)
- ✅ ODI call/visit + non-pausing device swap (TRN005)
- ✅ D02/D03 broken protocol via path 3 (TRN006)
- ✅ Discontinuation + read-only mode (TRN007)
- ✅ Watch lost + data upload skip (TRN008)
- ✅ A1 out-of-window + A2-before-A1 auto-miss (TRN009)
- ✅ Patient-initiated AE call variant (TRN010)
- ✅ Golden path (no issues) for both groups (TRN001, TRN002)

**Not yet covered (OK for Phase 1):**
- D02/D03 broken protocol path 1 (training_not_done flag)
- D02/D03 broken protocol path 2 (training completed but no session time recorded)
- Cumulative pause > 10 days → broken protocol (rare, can be added later)
- Loss of blinding event
- Multi-site device sharing (future: multi-hospital support)

---

**Version:** August 2026  
**Last Updated:** With simulator overhaul (updated from earlier ad-hoc design)
