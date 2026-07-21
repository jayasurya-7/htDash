"""
htDash Training Launcher
Launches Flask dashboard + Tkinter simulator side-by-side
"""

import subprocess
import time
import webbrowser
import sys
import io
import os
from pathlib import Path

# UTF-8 encoding for terminal output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def wait_for_server(port=8080, timeout=30):
    """Wait for Flask server to be ready."""
    import socket
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                return True
        except:
            pass
        time.sleep(0.5)

    return False


def main():
    """Launch Flask and simulator."""
    print("🚀 htDash Training Launcher\n")

    # Get project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Start Flask server
    print("📊 Starting Flask dashboard on port 8080...")
    try:
        flask_process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except Exception as e:
        print(f"❌ Failed to start Flask: {e}")
        return

    # Wait for server to be ready
    print("⏳ Waiting for server...")
    if wait_for_server(8080):
        print("✅ Flask server ready!\n")
        time.sleep(1)

        # Open browser
        print("🌐 Opening browser...")
        webbrowser.open('http://localhost:8080/login')
        time.sleep(2)
    else:
        print("⚠️  Server not responding - proceeding anyway\n")

    # Launch simulator
    print("🎮 Launching Training Simulator...")
    try:
        simulator_process = subprocess.Popen(
            [sys.executable, "-m", "training_simulator"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except Exception as e:
        print(f"❌ Failed to start simulator: {e}")
        flask_process.terminate()
        return

    print("✅ Both applications launched!\n")
    print("💡 Tips:")
    print("   • Dashboard: http://localhost:8080")
    print("   • Create cohort in simulator")
    print("   • File events in dashboard")
    print("   • Watch real-time verification in simulator\n")
    print("Press Ctrl+C to exit both...\n")

    # Wait for both processes
    try:
        while True:
            time.sleep(1)

            # Check if either process died
            flask_poll = flask_process.poll()
            sim_poll = simulator_process.poll()

            if flask_poll is not None and sim_poll is not None:
                print("\n❌ Both processes ended")
                break
            elif flask_poll is not None:
                print("\n⚠️  Flask process ended")
            elif sim_poll is not None:
                print("\n⚠️  Simulator process ended")

    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")

        # Terminate both processes
        try:
            simulator_process.terminate()
            simulator_process.wait(timeout=3)
        except:
            simulator_process.kill()

        try:
            flask_process.terminate()
            flask_process.wait(timeout=3)
        except:
            flask_process.kill()

        print("✅ Shutdown complete")


if __name__ == '__main__':
    main()
