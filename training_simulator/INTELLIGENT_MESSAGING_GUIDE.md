# Training Simulator — Intelligent Messaging System ✨

**Status:** ✅ Complete  
**Date:** August 3, 2026

---

## Overview

Enhanced the Training Simulator with **intelligent messaging** that guides users through the workflow:
- Shows when a patient completes all their events
- Displays when an entire day is complete
- Shows preview of next upcoming events
- Clear call-to-action guidance

---

## User Workflows

### Scenario 1: Patient Completes All Events

**Current Day:** Day 5  
**Patient:** Exp - Right (TRN001) — ✓ All events completed

**What User Sees:**

```
┌─────────────────────────────────────┐
│                                     │
│              ✓                      │
│                                     │
│      All Events Completed!          │
│                                     │
│  Patient Exp - Right (TRN001) has   │
│  finished all events for Day 5.     │
│                                     │
│  👉 Switch to another patient      │
│     using the sidebar               │
│                                     │
└─────────────────────────────────────┘
```

**User Action:**
- Clicks on another patient in sidebar (e.g., "Ctrl - Right (TRN004)")
- That patient's tab shows their events for the day
- If that patient also has no events, same message is shown

---

### Scenario 2: All Patients Complete Today's Events

**Current Day:** Day 5  
**All Patients:** Completed their events

**What User Sees:**

```
┌─────────────────────────────────────┐
│                                     │
│              🎉                     │
│                                     │
│          Day 5 Complete!            │
│                                     │
│    All patients have completed      │
│    their events.                    │
│                                     │
├─────────────────────────────────────┤
│                                     │
│  📋 Next Events Preview             │
│                                     │
│  • Exp - Left (TRN002) — Day 7      │
│    (2 events)                       │
│  • Ctrl - Left (TRN005) — Day 7     │
│    (1 event)                        │
│  • Exp - Right (TRN001) — Day 8     │
│    (3 events)                       │
│                                     │
├─────────────────────────────────────┤
│                                     │
│  👉 Click "Advance Day" to          │
│     progress to the next day        │
│                                     │
└─────────────────────────────────────┘
```

**User Action:**
- Clicks "Advance Day" button in top toolbar
- Simulator advances to Day 6
- Display updates showing Day 6 events (or completion messages)

---

## Features Implemented

### 1. **Patient Completion Detection**
- Checks if a patient has any events scheduled for current day
- Shows "All Events Completed!" message when no events remain
- Includes patient name and encouragement to switch patients

### 2. **Day Completion Detection**
- Checks if ALL patients have completed their events for the day
- Shows celebration message (🎉) when entire day is done
- Only activates when truly all patients have no events

### 3. **Next Events Preview**
- Scans all patients for their next upcoming events
- Shows up to 3 upcoming events
- Displays:
  - Patient name
  - Day number of event
  - Event count ("1 event" or "N events")
- Sorted by day (nearest first), then by patient name
- Looks ahead up to 30 days (or until end of study)

### 4. **Smart Guidance**
- Patient level: "Switch to another patient using the sidebar"
- Day level: "Click 'Advance Day' to progress to the next day"
- Context-aware messaging based on completion state

---

## Code Implementation

### New Methods in `main_window.py`

#### `_show_patient_complete_message(frame, role, current_day)`
Shows when a single patient has no events for current day.

**Visual Elements:**
- Checkmark emoji (✓) in sky-blue accent
- "All Events Completed!" heading
- Patient name and day context
- Guidance to switch patients

#### `_show_day_complete_message(frame, current_day)`
Shows when all patients have completed events for current day.

**Visual Elements:**
- Celebration emoji (🎉) in sky-blue accent
- "Day X Complete!" heading
- Completion confirmation
- **Next Events Preview** section with up to 3 upcoming events
- Guidance to click "Advance Day"

#### `_get_next_events(start_day) → list`
Finds next upcoming events across all patients.

**Returns:**
```python
[
    ("Exp - Left (TRN002)", 7, 2),      # (patient_name, day, event_count)
    ("Ctrl - Left (TRN005)", 7, 1),
    ("Exp - Right (TRN001)", 8, 3),
]
```

**Logic:**
- For each role/patient
- Find first day with events starting from `start_day`
- Count events for that day
- Sort by day, then by patient name
- Return up to reasonable limit (prevents scrolling forever)

### Updated `_update_display()` Method

**Logic Flow:**
1. Check if all patients have events for current day
2. For each patient:
   - If has events: show instruction cards (existing behavior)
   - If no events AND all done: show day completion message
   - If no events AND others have events: show patient completion message

---

## Message Formatting

### Colors Used (Light Theme)

| Element | Color | Hex Code |
|---------|-------|----------|
| Checkmark/Emoji | Sky-blue | `#0ea5e9` |
| Headings | Dark slate | `#1e293b` |
| Body text | Slate | `#334155` |
| Guidance text (bold) | Sky-blue | `#0ea5e9` |
| Secondary text | Muted slate | `#64748b` |

### Font Sizes

| Element | Size | Weight |
|---------|------|--------|
| Emoji | 48px | — |
| Heading | 14px | Bold |
| Body text | 10px | Regular |
| Guidance | 9px | Bold |
| Event preview | 9px | Regular |

### Spacing

- Top padding: 40px (patient) / 20px (day)
- Bottom padding: 40px (patient) / 20px (day)
- Horizontal padding: 16px
- Section gaps: 12-16px

---

## User Experience Flow

```
Day 1 Starts
    ↓
Display Day 1 events for all patients
    ↓
User clicks through tabs, completes events for each patient
    ↓
[Patient A completes all events]
    ├→ User sees: "✓ All Events Completed!"
    ├→ User switches to Patient B
    ↓
[Patient B, C, D, E complete all events]
    ├→ User sees: "🎉 Day 1 Complete!"
    ├→ User sees: "Next Events Preview"
    ├→ Shows which patients have events on Day 3, 5, 7, etc.
    ↓
[User clicks "Advance Day"]
    ↓
Day 2 Starts
    ├→ Shows Day 2 events for patients who have them
    ├→ Shows completion messages for patients without Day 2 events
    ↓
[Repeat for Days 3-187]
    ↓
Study Complete
```

---

## Testing Checklist

- [ ] Run simulator with test cohort (2 exp, 2 ctrl)
- [ ] Complete all events for Patient A → see checkmark message
- [ ] Switch to Patient B (still has events) → see their instructions
- [ ] Complete all events for remaining patients
- [ ] Verify "Day X Complete!" message appears
- [ ] Verify next events are displayed correctly:
  - [ ] Shows correct patient names
  - [ ] Shows correct day numbers
  - [ ] Shows correct event counts
  - [ ] Sorted by day (nearest first)
- [ ] Click "Advance Day" → day advances, messages update
- [ ] Check scrolling on next events preview (if > 3 events)
- [ ] Verify colors match light theme
- [ ] Check text readability and spacing

---

## Customization Options

### Adjust lookahead depth for next events:
```python
# In _get_next_events() method
for day in range(start_day, min(start_day + 30, TOTAL_DAYS + 1)):
    # Change 30 to desired lookahead days (e.g., 60 for longer preview)
```

### Adjust number of events shown in preview:
```python
# In _show_day_complete_message() method
for patient_name, day, event_count in next_events[:3]:  # Change 3 to desired count
```

### Change emoji or messaging text:
All text is in the two messaging methods — easy to customize:
- `_show_patient_complete_message()`
- `_show_day_complete_message()`

---

## Benefits

✅ **Better Guidance** — Users always know what to do next  
✅ **Reduced Confusion** — Clear messaging about completion status  
✅ **Workflow Awareness** — Next events preview keeps trainers informed  
✅ **Professional Feel** — Celebratory messages for milestones  
✅ **Efficient Navigation** — Guided transitions between patients/days  

---

## Files Modified

- `training_simulator/ui/main_window.py`
  - Enhanced `_update_display()` logic
  - Added `_show_patient_complete_message()`
  - Added `_show_day_complete_message()`
  - Added `_get_next_events()`

---

## Example Events Preview Output

For a typical 5-patient cohort on Day 5:

```
Next Events Preview
• Exp - Left (TRN002) — Day 7 (2 events)
• Ctrl - Left (TRN005) — Day 7 (1 event)
• Exp - Right (TRN001) — Day 8 (3 events)
```

This tells the trainer:
- Two patients have events coming up on Day 7
- One patient has Day 8 events
- Gives rough event count for planning purposes

---

## Troubleshooting

**Issue:** Next events not showing

**Solution:** Verify that patients have events scheduled beyond current day. Check curriculum files.

**Issue:** Message showing when patient still has events

**Solution:** Check that `entries_for_day()` is working correctly. Verify curriculum is loaded.

**Issue:** Text is hard to read

**Solution:** Verify light theme colors are applied. Check that FG_LIGHT and FG_BODY colors are correct in widgets.py.

---

## Future Enhancements

- [ ] Add time estimates for upcoming events
- [ ] Show event names in preview (not just count)
- [ ] Add "Quick Jump" button to next day with events
- [ ] Statistics: "X events completed today out of Y total"
- [ ] Progress bar showing % of day complete
- [ ] Sound notification when day is complete
- [ ] Export summary of day to file

---

## Developer Notes

The implementation uses **lookahead scanning** to find next events:

```python
# Scan each patient's curriculum
# Starting from start_day
# Until we find an event or reach lookahead limit
# Collect (name, day, count) tuples
# Sort by day, then by name
# Return sorted list
```

This is efficient for typical curricula (187 days, 5-10 patients) and provides good UX feedback.

The messaging is **context-aware**:
- Single patient complete → personal message
- All patients complete → day milestone message
- Messages guide next action clearly
