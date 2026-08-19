# Unified App Launcher — Training Simulator + Web Dashboard

**Status:** ✅ Complete  
**Date:** August 3, 2026  
**Feature:** Single launcher running both apps on separate threads

---

## Overview

A new **unified app launcher** that runs both:
1. **Flask Web Dashboard** (background thread)
2. **Training Simulator** (main thread)

No need to run two separate commands. Launch everything with one command!

---

## Quick Start

### Before (Two Commands)

```bash
# Terminal 1
python main.py

# Terminal 2
python training_simulator/simulator_app.py
```

### After (One Command)

```bash
python app_launcher.py
```

Both apps start automatically on separate threads!

---

## What Happens

```
python app_launcher.py
    ↓
┌─────────────────────────────────────┐
│ Unified App Launcher                │
├─────────────────────────────────────┤
│                                     │
│  Thread 1 (Background):             │
│  ▶ Flask Web Server                 │
│    - Starts on port 5000            │
│    - Runs silently                  │
│    - Dashboard auto-refreshes       │
│                                     │
│  Thread 2 (Main):                   │
│  ▶ Training Simulator               │
│    - Tkinter GUI window             │
│    - Normal interaction             │
│                                     │
│  Both run without affecting         │
│  each other!                        │
│                                     │
└─────────────────────────────────────┘
```

---

## Features

✅ **Single Command Launch**  
   No need to run two separate terminals

✅ **Separate Threads**  
   Each app runs independently
   - Flask on background thread
   - Simulator on main thread (required for Tkinter)

✅ **Auto-Refresh Web Dashboard**  
   Dashboard refreshes every 30 seconds automatically
   - No manual refresh needed
   - Data always current

✅ **Clean Console Output**  
   Startup messages show status of both apps

✅ **No Interference**  
   Background checking/operations don't affect simulator

✅ **Easy To Stop**  
   Close simulator window → both apps stop

---

## How It Works

### Thread Architecture

**Background Thread (Flask):**
- Runs Flask web server
- Listens on `http://localhost:5000`
- Doesn't block main thread
- Auto-refresh handles UI updates

**Main Thread (Simulator):**
- Runs Tkinter GUI
- Tkinter MUST run on main thread (Python limitation)
- Responsive and interactive
- Unaffected by background Flask operations

### Threading Benefits

| Aspect | Benefit |
|--------|---------|
| **Independence** | Flask delays don't freeze simulator UI |
| **Responsiveness** | Simulator stays responsive at all times |
| **Scalability** | Can add more background tasks later |
| **Simplicity** | Single unified launcher |

---

## Usage

### Standard Launch

```bash
python app_launcher.py
```

**Output:**
```
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                     htDash — Unified App Launcher                         ║
║                                                                            ║
║                Running Training Simulator + Web Dashboard                 ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

================================================================================
🚀 Starting Flask Web Dashboard...
================================================================================
Web Dashboard: http://localhost:5000
Credentials:
  • Therapist: RP-HS-1002 / password
  • Admin: RP-HS-ADMIN / password
  • Supervisor: LAB-HS-DATA / password
================================================================================

⏳ Waiting for web server to start...
✅ Web server started

================================================================================
📋 READY TO LAUNCH TRAINING SIMULATOR
================================================================================
The Training Simulator window will open shortly...
================================================================================
```

Then **Training Simulator window opens** and both apps run together!

### Access the Apps

**Web Dashboard:**
- URL: `http://localhost:5000`
- In browser: Open `http://localhost:5000`
- Credentials: Above

**Training Simulator:**
- Opened automatically as popup window
- Interact normally

---

## Auto-Refresh Feature

The web dashboard **automatically refreshes every 30 seconds**:

✅ **Data always current** — Shows latest simulator state  
✅ **No manual action** — Transparent to user  
✅ **Smooth transitions** — Page reloads silently  
✅ **Configurable** — Can adjust refresh interval  

### How Auto-Refresh Works

1. Dashboard loads in browser
2. JavaScript checks for auto-refresh flag
3. Every 30 seconds: Silently fetches latest page
4. If changes detected: Reloads page
5. User sees updated data automatically

### Disable Auto-Refresh (if needed)

In browser console:
```javascript
sessionStorage.setItem('enableAutoRefresh', 'false');
```

### Change Refresh Interval

Edit `templates/base.html`:
```javascript
const refreshInterval = 30000; // Change to 60000 for 60 seconds
```

---

## Architecture

### File: `app_launcher.py`

**Purpose:** Main launcher script

**What it does:**
1. Adds project root to Python path
2. Imports Flask app (`from main import app`)
3. Imports Simulator (`from training_simulator.ui.main_window import run`)
4. Creates background thread for Flask
5. Runs Simulator on main thread

**Key Functions:**

```python
run_flask_server()
  → Starts Flask app on background thread
  → Listens on localhost:5000
  → Runs without blocking

run_training_simulator()
  → Starts Tkinter GUI on main thread
  → Must be main thread (Python requirement)

main()
  → Launches both on separate threads
  → Prints startup messages
  → Handles cleanup on exit
```

### File: `templates/base.html` (Updated)

**Auto-refresh JavaScript added:**
```html
<script>
  // Checks sessionStorage for enableAutoRefresh flag
  // If true: refreshes page every 30 seconds
  // Runs silently in background
</script>
```

---

## Workflow Example

### Scenario: Test Training Simulator + Monitor Dashboard

**Step 1:** Launch everything
```bash
python app_launcher.py
```

**Step 2:** Training Simulator opens
- Create cohort
- Run through days
- Complete events

**Step 3:** Open browser simultaneously
```
http://localhost:5000
Login with test credentials
```

**Step 4:** Dashboard auto-refreshes
- Sees updated data from simulator
- Every 30 seconds: New refresh
- No manual intervention needed

**Step 5:** Stop
- Close Simulator window
- Both apps stop

---

## Technical Details

### Why Threads?

**Flask on background thread:**
- Frees up main thread for Tkinter
- Flask can run indefinitely
- Doesn't block UI

**Simulator on main thread:**
- Python requirement: Tkinter must be on main thread
- Prevents "\_tkinter.TclError: can't invoke 'update' from 'after' callback"
- Ensures responsive GUI

### Thread Safety

Both apps operate independently:
- Flask: Web server, handles HTTP
- Simulator: Tkinter GUI, handles user input
- No shared state = no race conditions
- File I/O is sequential (safe)

### Shutdown

When simulator closes:
1. Main thread exits (Simulator window closed)
2. Background Flask thread marked as daemon
3. Entire process stops cleanly
4. No hanging processes

---

## Troubleshooting

### Problem: Flask doesn't start

**Symptom:** "Address already in use" error

**Solution:**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9  # Mac/Linux
# Or close other Flask instances
```

### Problem: Simulator window doesn't appear

**Symptom:** Console shows startup, but no window

**Solution:**
- Wait 2-3 seconds (Flask is starting)
- Check taskbar for hidden window
- Try clicking on taskbar icon

### Problem: Dashboard doesn't auto-refresh

**Symptom:** Page doesn't update automatically

**Solution:**
- Open browser console (F12)
- Run: `sessionStorage.setItem('enableAutoRefresh', 'true')`
- Reload page (Ctrl+R)

### Problem: Simulator freezes

**Symptom:** Can't interact with simulator

**Solution:**
- Flask might be overloaded
- Close browser if many tabs open
- Restart with: `python app_launcher.py`

---

## Advanced Configuration

### Change Flask Port

Edit `app_launcher.py`:
```python
flask_app.run(
    host='localhost',
    port=5000,  # Change to 8000, 3000, etc.
    ...
)
```

### Change Auto-Refresh Interval

Edit `templates/base.html`:
```javascript
const refreshInterval = 30000; // milliseconds
// 30000 = 30 seconds
// 60000 = 60 seconds
// 10000 = 10 seconds
```

### Add More Background Tasks

In `app_launcher.py`:
```python
def run_background_task():
    # Do something
    pass

task_thread = threading.Thread(target=run_background_task, daemon=True)
task_thread.start()
```

---

## Benefits Summary

### Before (Two Commands)

```
Terminal 1: python main.py
Terminal 2: python training_simulator/simulator_app.py
```
- ❌ Requires 2 terminal windows
- ❌ Manual coordination
- ❌ Dashboard doesn't auto-refresh
- ❌ More complex for users

### After (One Command)

```
python app_launcher.py
```
- ✅ Single command
- ✅ Both apps start automatically
- ✅ Dashboard auto-refreshes
- ✅ Cleaner user experience
- ✅ Background doesn't block UI

---

## Testing

### Quick Test (1 minute)

1. Run: `python app_launcher.py`
2. Wait for startup messages
3. Verify simulator window opens
4. Open browser: `http://localhost:5000`
5. Login with credentials
6. Check dashboard refreshes (watch counter or data)

### Full Test (5 minutes)

1. Launch launcher
2. Create cohort in simulator
3. Monitor dashboard in browser
4. Advance day in simulator
5. Verify dashboard updates automatically (no refresh button clicked)
6. Test both apps responsive
7. Close simulator → apps stop

---

## Files Modified

1. **app_launcher.py** (new)
   - Unified launcher script
   - Thread management

2. **templates/base.html** (updated)
   - Auto-refresh JavaScript added

---

## Summary

✅ **Single unified launcher** — Run both apps with one command  
✅ **Separate threads** — No interference between apps  
✅ **Auto-refresh dashboard** — Data always current  
✅ **Better UX** — Simpler for end users  
✅ **Background operations** — Don't block simulator  

**Run:** `python app_launcher.py`

**That's it!** 🚀
