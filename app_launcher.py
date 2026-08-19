"""
Unified App Launcher for htDash Training Simulator

Runs both the Flask web dashboard and Training Simulator on separate threads
in a single application. No need to run two separate commands.

Usage:
  python app_launcher.py

This will:
  1. Start Flask web server on a background thread (port 5000)
  2. Launch Training Simulator Tkinter UI on main thread
  3. Keep both running without affecting each other
  4. Web dashboard will auto-refresh periodically
"""

import threading
import time
import sys
import webbrowser
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import Flask app
from main import app as flask_app

# Import Training Simulator
from training_simulator.ui.main_window import run as run_simulator


def run_flask_server():
    """Run Flask web server on background thread."""
    try:
        # Run Flask in debug mode without the reloader
        # (reloader would cause issues with threads)
        # Suppress Flask startup messages (we handle that in main())
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        flask_app.run(
            host='localhost',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Flask Error: {e}")


def run_training_simulator():
    """Run Training Simulator on main thread."""
    print("\n" + "="*80)
    print("🧪 Starting Training Simulator...")
    print("="*80)
    print("A new window will open with the Training Simulator UI")
    print("="*80 + "\n")

    try:
        run_simulator()
    except Exception as e:
        print(f"❌ Simulator Error: {e}")


def main():
    """Launch both apps on separate threads."""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "htDash — Unified App Launcher".center(78) + "║")
    print("║" + " "*78 + "║")
    print("║" + "Running Training Simulator + Web Dashboard".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    print()

    # Start Flask on background thread
    flask_thread = threading.Thread(
        target=run_flask_server,
        daemon=True,
        name="FlaskThread"
    )
    flask_thread.start()

    # Give Flask a moment to start
    print("⏳ Waiting for web server to start...")
    time.sleep(3)
    print("✅ Web server started\n")

    # Auto-open browser
    print("🌐 Opening web dashboard in browser...")
    try:
        webbrowser.open('http://localhost:5000')
        print("✅ Browser launched! Dashboard should open shortly...\n")
    except Exception as e:
        print(f"⚠️  Could not auto-open browser: {e}")
        print("   Please open http://localhost:5000 manually in your browser\n")

    # Start Training Simulator on main thread
    # (Tkinter must run on main thread)
    print("\n" + "="*80)
    print("📋 READY TO LAUNCH TRAINING SIMULATOR")
    print("="*80)
    print("The Training Simulator window will open shortly...")
    print("="*80 + "\n")

    try:
        run_training_simulator()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
