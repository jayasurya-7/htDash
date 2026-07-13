"""
Training Simulator GUI Application (Tkinter).

Main entry point for the htDash training simulator.
Provides interface for creating cohorts, running simulations, and verifying results.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from training_simulator.state_store import StateStore
from training_simulator.patient_seed import create_cohort
from training_simulator.protocol_engine import ProtocolEngine
from training_simulator.scenarios import ScenarioGenerator
from training_simulator.verification import VerificationEngine
from utils.data_access import read_patient_meta, derive_status


class SimulatorApp:
    """Main application window."""

    def __init__(self, root):
        self.root = root
        self.root.title("htDash Training Simulator")
        self.root.geometry("1200x700")

        self.state_store = StateStore()
        self.protocol_engine = ProtocolEngine()
        self.scenario_generator = ScenarioGenerator()  # Will create day-specific generators in _run_action
        self.verification_engine = VerificationEngine()

        # Current screen
        self.current_screen = None

        # Show initial screen
        self._show_setup_screen()

    def _clear_screen(self):
        """Clear current screen."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def _show_setup_screen(self):
        """Setup/initialization screen."""
        self._clear_screen()
        self.current_screen = 'setup'

        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(frame, text="htDash Training Simulator", font=("Arial", 18, "bold"))
        title.pack(pady=20)

        # Status
        if self.state_store.is_cohort_active():
            status = ttk.Label(
                frame,
                text=f"[OK] Cohort active ({len(self.state_store.get_patient_ids())} patients)",
                font=("Arial", 12),
                foreground="green"
            )
            status.pack(pady=10)
        else:
            status = ttk.Label(
                frame,
                text="No active cohort",
                font=("Arial", 12),
                foreground="orange"
            )
            status.pack(pady=10)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=30)

        if not self.state_store.is_cohort_active():
            create_btn = ttk.Button(
                button_frame,
                text="Create Simulation Cohort (10 patients)",
                command=self._create_cohort_action
            )
            create_btn.pack(pady=10)
        else:
            run_btn = ttk.Button(
                button_frame,
                text="Continue Simulation",
                command=self._show_main_screen
            )
            run_btn.pack(pady=10)

            reset_btn = ttk.Button(
                button_frame,
                text="Reset Simulation",
                command=self._reset_cohort_action
            )
            reset_btn.pack(pady=10)

    def _create_cohort_action(self):
        """Create a new 10-patient cohort."""
        try:
            self.state_store.log_action("Creating cohort", "Seeding 10 patients…")
            cohort = create_cohort()
            self.state_store.init_cohort(cohort)
            self.state_store.log_action("Cohort created", f"{len(cohort)} patients initialized")
            messagebox.showinfo("Success", f"Created {len(cohort)} patients.\n\nCohort is ready. Press Continue to start simulation.")
            self._show_setup_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create cohort:\n{e}")
            self.state_store.log_action("ERROR", f"Cohort creation failed: {e}")

    def _reset_cohort_action(self):
        """Reset cohort and clear state."""
        if messagebox.askyesno("Confirm Reset", "This will delete all 10 patients and reset the simulation. Continue?"):
            try:
                patient_ids = self.state_store.get_patient_ids()
                # In a full implementation, would also delete patient folders from data/
                # For now, just clear the state store
                self.state_store.reset_cohort()
                self.state_store.log_action("Cohort reset", f"Cleared {len(patient_ids)} patients")
                messagebox.showinfo("Success", "Simulation reset. You can create a new cohort.")
                self._show_setup_screen()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset:\n{e}")

    def _show_main_screen(self):
        """Main simulation screen with Run button and patient grid."""
        self._clear_screen()
        self.current_screen = 'main'

        # Top bar
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        title = ttk.Label(top_frame, text="Simulation Running", font=("Arial", 14, "bold"))
        title.pack(side=tk.LEFT)

        day_label = ttk.Label(
            top_frame,
            text=f"Day: {self.state_store.get_simulated_day()}",
            font=("Arial", 12)
        )
        day_label.pack(side=tk.RIGHT)

        # Button frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        run_btn = ttk.Button(button_frame, text="▶ Run (Next Day)", command=self._run_action)
        run_btn.pack(side=tk.LEFT, padx=5)

        verify_btn = ttk.Button(button_frame, text="🔍 Verify Now", command=self._verify_action)
        verify_btn.pack(side=tk.LEFT, padx=5)

        report_btn = ttk.Button(button_frame, text="📊 Report", command=self._show_report_screen)
        report_btn.pack(side=tk.LEFT, padx=5)

        back_btn = ttk.Button(button_frame, text="Back", command=self._show_setup_screen)
        back_btn.pack(side=tk.RIGHT, padx=5)

        # Main content (paned)
        paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Patient grid
        self._render_patient_grid(paned)

        # Instructions panel
        self._render_instructions_panel(paned)

    def _render_patient_grid(self, parent):
        """Render 10-patient status grid."""
        frame = ttk.LabelFrame(parent, text="Patient Status", padding="5")
        parent.add(frame)

        # Headers
        headers = ["ID", "Group", "Status", "Days Active", "Next Due"]
        for i, h in enumerate(headers):
            header = ttk.Label(frame, text=h, font=("Arial", 10, "bold"))
            header.grid(row=0, column=i, sticky="w", padx=5, pady=5)

        # Patient rows
        patient_ids = self.state_store.get_patient_ids()
        for row, patient_id in enumerate(patient_ids, start=1):
            patient = read_patient_meta('ranipet', patient_id)
            if not patient:
                continue

            status = derive_status(patient)
            group = patient.get('group', '?')

            # Calculate days since activation
            if patient.get('activationDate'):
                from datetime import datetime
                try:
                    act_dt = datetime.fromisoformat(patient['activationDate'])
                    days_active = (datetime.now() - act_dt).days
                except:
                    days_active = '?'
            else:
                days_active = 'N/A'

            # Get next due event
            due_events = self.protocol_engine.get_due_events(patient_id)
            next_due = due_events[0]['event_name'] if due_events else '—'

            # Render row
            ttk.Label(frame, text=patient_id).grid(row=row, column=0, sticky="w", padx=5)
            ttk.Label(frame, text=group).grid(row=row, column=1, sticky="w", padx=5)
            ttk.Label(frame, text=status).grid(row=row, column=2, sticky="w", padx=5)
            ttk.Label(frame, text=str(days_active)).grid(row=row, column=3, sticky="w", padx=5)
            ttk.Label(frame, text=next_due, font=("Arial", 9, "italic")).grid(row=row, column=4, sticky="w", padx=5)

    def _render_instructions_panel(self, parent):
        """Render today's instructions from the state store (no generation here)."""
        frame = ttk.LabelFrame(parent, text="Today's Training Scenarios & Instructions", padding="5")
        parent.add(frame)

        text_widget = scrolledtext.ScrolledText(frame, height=12, wrap=tk.WORD, font=("Courier", 10))
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Read today's expected events from state store (NOT generate new ones)
        current_day = self.state_store.get_simulated_day()
        today_events = self.state_store.get_expected_events_for_day(current_day)

        # Render from state store
        if today_events:
            output_lines = [
                "=" * 70,
                f"DAY {current_day} — TRAINING SCENARIOS & EVENTS",
                "=" * 70,
                "",
            ]
            for i, event in enumerate(today_events, 1):
                patient_id = event.get('patient_id', 'unknown')
                protocol_event_id = event.get('protocol_event_id', 'unknown')
                free_type = event.get('free_type')
                suggested_values = event.get('suggested_values', {})

                output_lines.append(f"[{i}] PATIENT: {patient_id}")
                output_lines.append(f"    EVENT: {protocol_event_id}")

                if suggested_values:
                    output_lines.append(f"    Suggested fields:")
                    for k, v in suggested_values.items():
                        output_lines.append(f"      • {k}: {v}")
                output_lines.append("")

            text_widget.insert('1.0', '\n'.join(output_lines))
        else:
            text_widget.insert('1.0',
                f"No events scheduled for Day {current_day}.\n\n"
                f"Press ▶ Run to advance to the next day.\n\n"
                f"(Scenarios only appear AFTER patients are activated.)")

        text_widget.config(state=tk.DISABLED)

    def _format_protocol_instruction(self, patient_id: str, event_name: str, patient: dict) -> str:
        """Format a protocol event as a training instruction."""
        from datetime import datetime, timedelta

        if event_name == "Patient Activation":
            return (
                f"ACTIVATE PATIENT: File activation event.\n"
                f"    Date: Today, Session: 10:00–11:00 AM (or choose time)\n"
                f"    Training completed: YES"
            )
        elif event_name == "Informed Consent":
            return (
                f"FILE INFORMED CONSENT: Upload PDF consent form.\n"
                f"    Date: Today\n"
                f"    Form required: YES"
            )
        elif "Home Visit" in event_name:
            return (
                f"HOME VISIT: {event_name.upper()}\n"
                f"    Session time: 10:00–11:30 AM (or choose time)\n"
                f"    Training completed: YES (if applicable)"
            )
        elif "Follow-up Call" in event_name:
            return (
                f"FOLLOW-UP CALL: {event_name.upper()}\n"
                f"    Call mode: Audio/Video/Text\n"
                f"    Duration: 10–20 minutes\n"
                f"    Notes required: YES"
            )
        elif "Assessment" in event_name:
            return (
                f"RECORD ASSESSMENT: {event_name.upper()}\n"
                f"    Date: Today or scheduled date\n"
                f"    Notes: Optional"
            )
        else:
            return f"FILE EVENT: {event_name}"

    def _run_action(self):
        """Advance simulation by one day and generate scenarios."""
        try:
            patient_ids = self.state_store.get_patient_ids()
            results = self.protocol_engine.advance_one_day(patient_ids)

            self.state_store.increment_day()
            current_day = self.state_store.get_simulated_day()

            # Determine scenario TYPE for this day (once, globally)
            # But generate unique VALUES for each patient
            # Only generate scenarios AFTER at least one patient is activated
            daily_scenario_type = None
            any_patient_activated = False

            # Check if ANY patient has been activated (has a non-None activationDate)
            for patient_id in patient_ids:
                patient = read_patient_meta('ranipet', patient_id)
                if patient and patient.get('activationDate') is not None:
                    any_patient_activated = True
                    self.state_store.log_action("Scenario system", f"Activated patient {patient_id} detected — scenarios enabled")
                    break

            if any_patient_activated:
                # Generate scenario TYPE for the day (deterministic per day)
                day_generator = ScenarioGenerator(seed=current_day)
                day_scenario = day_generator.roll_scenario_injection(
                    'experimental',
                    injection_probability=0.25
                )
                if day_scenario:
                    daily_scenario_type = day_scenario['type']
                    self.state_store.log_action("Scenario injection", f"Day {current_day}: {daily_scenario_type} scenario type")

            # Generate scenarios for this day
            event_count = 0
            scenario_count = 0
            for patient_id in patient_ids:
                patient = read_patient_meta('ranipet', patient_id)
                if not patient:
                    continue

                group = patient.get('group', 'experimental')

                # Get protocol due events and store them
                due_events = self.protocol_engine.get_due_events(patient_id)
                for event in due_events:
                    if event['days_overdue'] == 0:
                        self.state_store.add_expected_event(
                            day=current_day,
                            patient_id=patient_id,
                            protocol_event_id=event['protocol_event_id'],
                            suggested_values={'event': event['event_name']},
                        )
                        event_count += 1

                # Apply the GLOBAL scenario TYPE to all applicable ACTIVATED patients
                # But generate UNIQUE VALUES for each patient (based on patient ID)
                # (Skip if scenario type not applicable to this patient's group)
                # (Skip if patient is not yet activated)

                # Only add scenario if BOTH conditions are true:
                # 1. A scenario type was determined for this day (patient is activated somewhere)
                # 2. THIS patient is activated (has activationDate set)
                is_patient_activated = patient.get('activationDate') is not None

                if daily_scenario_type and is_patient_activated:
                    scenario_type = daily_scenario_type

                    # Skip robot/device issues for control patients
                    if group == 'control' and scenario_type in ['robot_issue_call', 'other_device_issue_call']:
                        continue

                    # Generate UNIQUE scenario values for THIS patient (seed by day + patient ID hash)
                    patient_seed = current_day + hash(patient_id) % 10000
                    patient_generator = ScenarioGenerator(seed=patient_seed)

                    # Generate values based on scenario type
                    if scenario_type == 'adverse_event':
                        values = patient_generator.generate_adverse_event()
                    elif scenario_type == 'robot_issue_call':
                        values = patient_generator.generate_robot_issue_call()
                    elif scenario_type == 'other_device_issue_call':
                        values = patient_generator.generate_other_device_issue_call()
                    elif scenario_type == 'patient_call':
                        values = patient_generator.generate_patient_call()
                    else:
                        values = {}

                    self.state_store.add_expected_event(
                        day=current_day,
                        patient_id=patient_id,
                        protocol_event_id=scenario_type,
                        free_type=scenario_type,
                        suggested_values=values,  # UNIQUE per patient
                    )
                    scenario_count += 1

            self.state_store.log_action(
                "Day advanced",
                f"Day {current_day}: {event_count} protocol events + {scenario_count} scenarios injected"
            )

            messagebox.showinfo(
                "Success",
                f"Day {current_day} started!\n\n"
                f"Check the instructions panel for today's scenarios.\n"
                f"File each event in htDash with the suggested field values.\n"
                f"Then press Verify to check your work."
            )
            self._show_main_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to advance day:\n{e}")
            self.state_store.log_action("ERROR", f"Day advancement failed: {e}")

    def _verify_action(self):
        """Verify all expected events against actual protocol_events.json."""
        try:
            patient_ids = self.state_store.get_patient_ids()
            all_verdicts = {}

            for patient_id in patient_ids:
                expected_events = self.state_store.get_expected_events_for_patient(patient_id)
                if not expected_events:
                    continue

                verdicts = self.verification_engine.verify_all_expected_events(patient_id, expected_events)
                all_verdicts[patient_id] = verdicts

                # Update state store with verdicts
                for i, expected in enumerate(expected_events):
                    if i < len(verdicts):
                        verdict = verdicts[i]
                        self.state_store.update_expected_event_verdict(
                            day=expected['day'],
                            patient_id=patient_id,
                            protocol_event_id=expected['protocol_event_id'],
                            verdict=verdict['verdict'],
                            actual_completion_date=verdict['actual_completion_date'],
                        )

            self.state_store.log_action("Verification", f"Verified {len(all_verdicts)} patients")
            self._show_report_screen(all_verdicts)
        except Exception as e:
            messagebox.showerror("Error", f"Verification failed:\n{e}")
            self.state_store.log_action("ERROR", f"Verification failed: {e}")

    def _show_report_screen(self, verdicts_data=None):
        """Show final summary report with verification results."""
        self._clear_screen()
        self.current_screen = 'report'

        # Main frame
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title = ttk.Label(frame, text="Training Verification Report", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        if not verdicts_data:
            # Generate verdicts now if not passed in
            try:
                patient_ids = self.state_store.get_patient_ids()
                verdicts_data = {}

                for patient_id in patient_ids:
                    expected_events = self.state_store.get_expected_events_for_patient(patient_id)
                    if expected_events:
                        verdicts = self.verification_engine.verify_all_expected_events(patient_id, expected_events)
                        verdicts_data[patient_id] = verdicts
            except Exception as e:
                ttk.Label(frame, text=f"Error generating report: {e}", foreground="red").pack()
                ttk.Button(frame, text="Back to Simulation", command=self._show_main_screen).pack(pady=10)
                return

        if not verdicts_data:
            ttk.Label(frame, text="No events to verify yet. Run the simulation and file events in htDash.",
                     font=("Arial", 11)).pack(pady=20)
            ttk.Button(frame, text="Back to Simulation", command=self._show_main_screen).pack()
            return

        # Generate summary
        summary = self.verification_engine.generate_summary_report(verdicts_data)

        # Summary stats
        stats_frame = ttk.LabelFrame(frame, text="Overall Results", padding="10")
        stats_frame.pack(fill=tk.X, pady=10)

        overall = summary['overall']
        total = overall['total']
        pass_rate = overall['pass_rate']

        # Color code the pass rate
        if pass_rate >= 90:
            color = "green"
            rating = "Excellent!"
        elif pass_rate >= 70:
            color = "orange"
            rating = "Good"
        elif pass_rate >= 50:
            color = "orange"
            rating = "Fair"
        else:
            color = "red"
            rating = "Needs work"

        ttk.Label(stats_frame, text=f"Pass Rate: {pass_rate:.1f}% ({rating})",
                 font=("Arial", 14, "bold"), foreground=color).pack()

        ttk.Label(stats_frame, text=f"Total Events: {total}").pack()
        ttk.Label(stats_frame, text=f"  ✓ Done on time: {overall['done_on_time']}").pack()
        ttk.Label(stats_frame, text=f"  ⚠ Done late: {overall['done_late']}").pack()
        ttk.Label(stats_frame, text=f"  ✗ Missing: {overall['missing']}").pack()
        ttk.Label(stats_frame, text=f"  ✗ Wrong fields: {overall['wrong_fields']}").pack()

        # Per-patient breakdown
        details_frame = ttk.LabelFrame(frame, text="Per-Patient Breakdown", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Add scrollbar
        canvas = tk.Canvas(details_frame)
        scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Render per-patient stats
        for patient_id in sorted(verdicts_data.keys()):
            patient = read_patient_meta('ranipet', patient_id)
            group = patient.get('group', '?') if patient else '?'
            patient_summary = summary['per_patient'][patient_id]

            patient_frame = ttk.Frame(scrollable_frame)
            patient_frame.pack(fill=tk.X, pady=5)

            patient_rate = (
                (patient_summary['done_on_time'] / patient_summary['total'] * 100)
                if patient_summary['total'] > 0 else 0
            )

            ttk.Label(
                patient_frame,
                text=f"{patient_id} ({group.upper()}): {patient_rate:.0f}% "
                     f"({patient_summary['done_on_time']}/{patient_summary['total']})",
                font=("Arial", 10, "bold")
            ).pack(anchor="w", padx=10)

            ttk.Label(
                patient_frame,
                text=f"  On-time: {patient_summary['done_on_time']} | "
                     f"Late: {patient_summary['done_late']} | "
                     f"Missing: {patient_summary['missing']} | "
                     f"Wrong: {patient_summary['wrong_fields']}",
                font=("Arial", 9)
            ).pack(anchor="w", padx=20)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Back to Simulation", command=self._show_main_screen).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View Details (JSON)", command=self._show_details_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset Simulation", command=self._reset_cohort_action).pack(side=tk.LEFT, padx=5)

    def _show_details_json(self):
        """Show the full state store JSON for inspection."""
        try:
            import json
            state_file = Path(__file__).parent / "state" / "simulation_state.json"
            if state_file.exists():
                data = json.loads(state_file.read_text())
                # Create a new window to display JSON
                details_win = tk.Toplevel(self.root)
                details_win.title("Simulation State (JSON)")
                details_win.geometry("800x600")

                text_widget = scrolledtext.ScrolledText(details_win, wrap=tk.WORD, font=("Courier", 9))
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

                json_str = json.dumps(data, indent=2)
                text_widget.insert('1.0', json_str)
                text_widget.config(state=tk.DISABLED)
            else:
                messagebox.showwarning("No Data", "No simulation state file found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show details:\n{e}")


def main():
    """Entry point."""
    root = tk.Tk()
    app = SimulatorApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
