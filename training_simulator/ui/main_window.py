"""Main window for the training simulator Tkinter UI."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from typing import List, Dict

from training_simulator.bootstrap import Config
from training_simulator import cohort, state as state_store, day_engine
from training_simulator.cohort_config import CohortConfig, generate_patient_defs
from training_simulator.curriculum import entries_for_day, max_day
from training_simulator import instructions
from training_simulator.verification import verify_cohort
from training_simulator.ui.widgets import (
    CohortStatusBar, RoleTab,
    BG_DARK, BG_DARKER, BG_CARD, BORDER, FG_LIGHT, FG_BODY, FG_MUTED, ACCENT, ACCENT_HOVER,
    FONT_UI, FONT_MONO,
)
from training_simulator.ui.setup_dialog import SetupDialog
from training_simulator.ui.verification_dialog import VerificationDialog
from training_simulator.ui.cohort_view import CohortViewTab

TOTAL_DAYS = 187


class MainWindow(tk.Tk):
    """Main Tkinter window for training simulator."""

    def __init__(self):
        super().__init__()
        self.title('htDash Training Simulator')
        self.geometry('1440x880')
        self.minsize(1100, 700)
        self.configure(bg=BG_DARK)  # Light background for modern, professional look

        self.cohort_state = None
        self.selected_role = tk.StringVar()

        # Dynamic roles and role names (populated after cohort is created)
        self.roles: List[str] = []
        self.role_names: Dict[str, str] = {}       # role -> "Exp - Right (TRN001)"
        self.role_groups: Dict[str, str] = {}       # role -> 'experimental' | 'control'
        self.role_to_homer_id: Dict[str, str] = {}
        self.patient_defs: List[dict] = []
        self._patient_buttons: Dict[str, tk.Widget] = {}

        self._build_ui()
        self._initialize_cohort()  # Show setup dialog and create cohort

    def _build_ui(self):
        """Build the UI layout (framework only - patient tabs populated after cohort setup)."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=BG_DARK)
        style.configure('TLabel', background=BG_DARK, foreground=FG_BODY, font=(FONT_UI, 10))
        style.configure('TButton', background=BG_CARD, foreground=FG_BODY, font=(FONT_UI, 9))
        style.configure('TNotebook', background=BG_DARK, borderwidth=0)
        style.configure('TNotebook.Tab', padding=[16, 9], font=(FONT_UI, 10), background=BG_CARD, foreground=FG_MUTED)
        style.map(
            'TNotebook.Tab',
            background=[('selected', ACCENT)],
            foreground=[('selected', '#ffffff')],
        )

        # Status bar (top)
        self.status_bar = CohortStatusBar(
            self,
            on_new_cohort=self._on_new_cohort,
            on_teardown=self._on_teardown,
            on_advance=self._on_advance_day,
            on_verify=self._on_verify
        )
        self.status_bar.pack(fill=tk.X, side=tk.TOP)

        # Main container (left sidebar + content area)
        self.main_container = tk.Frame(self, bg=BG_DARK)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Left sidebar (will be populated dynamically)
        self.sidebar = tk.Frame(self.main_container, bg=BG_DARKER, width=230)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(8, 4), pady=8)
        self.sidebar.pack_propagate(False)

        # Content area (right side) — role tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=(4, 8), pady=8)
        self.notebook.bind('<<NotebookTabChanged>>', self._on_notebook_tab_changed)

        # Placeholder (will be populated after cohort created)
        self.tabs = {}

    # ── Sidebar ──

    def _populate_sidebar(self):
        """Populate sidebar with grouped patient buttons + day navigation."""
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self._patient_buttons = {}

        tk.Label(
            self.sidebar, text='\U0001f465 PATIENTS', font=(FONT_UI, 10, 'bold'),
            fg=ACCENT, bg=BG_DARKER, anchor=tk.W,
        ).pack(fill=tk.X, pady=(14, 10), padx=14)

        exp_roles = [r for r in self.roles if self.role_groups.get(r) == 'experimental']
        ctrl_roles = [r for r in self.roles if self.role_groups.get(r) == 'control']

        if exp_roles:
            self._build_patient_group(self.sidebar, 'EXPERIMENTAL', exp_roles, '#38bdf8')
        if ctrl_roles:
            self._build_patient_group(self.sidebar, 'CONTROL', ctrl_roles, '#fb923c')

        # ── Day navigation ──
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill=tk.X, pady=(10, 14), padx=14)

        tk.Label(
            self.sidebar, text='\U0001f4c5 DAY NAVIGATION', font=(FONT_UI, 10, 'bold'),
            fg=ACCENT, bg=BG_DARKER, anchor=tk.W,
        ).pack(fill=tk.X, pady=(0, 10), padx=14)

        nav_frame = tk.Frame(self.sidebar, bg=BG_DARKER)
        nav_frame.pack(fill=tk.X, padx=14)

        prev_btn = self._nav_button(nav_frame, '◀', self._prev_day)
        prev_btn.pack(side=tk.LEFT)

        self.day_var = tk.StringVar(value='Day 1')
        tk.Label(
            nav_frame, textvariable=self.day_var, font=(FONT_UI, 10, 'bold'),
            fg=FG_LIGHT, bg=BG_DARKER,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        next_btn = self._nav_button(nav_frame, '▶', self._next_day)
        next_btn.pack(side=tk.RIGHT)

        self.day_spin = tk.Spinbox(
            self.sidebar, from_=1, to=TOTAL_DAYS, width=10, font=(FONT_MONO, 9),
            command=self._on_day_spin, bg=BG_CARD, fg=FG_LIGHT,
            buttonbackground=ACCENT, insertbackground=FG_LIGHT, relief=tk.FLAT, justify=tk.CENTER,
        )
        self.day_spin.pack(fill=tk.X, pady=10, padx=14)
        self.day_spin.delete(0, tk.END)
        self.day_spin.insert(0, '1')
        self.day_spin.bind('<Return>', lambda _e: self._on_day_spin())
        self.day_spin.bind('<FocusOut>', lambda _e: self._on_day_spin())

    def _build_patient_group(self, parent, label: str, roles: List[str], dot_color: str):
        tk.Label(
            parent, text=label, font=(FONT_UI, 8, 'bold'),
            fg=FG_MUTED, bg=BG_DARKER, anchor=tk.W,
        ).pack(fill=tk.X, padx=14, pady=(4, 4))

        for role in roles:
            btn = tk.Button(
                parent,
                text=f'  {self.role_names[role]}',
                command=lambda r=role: self._select_role(r),
                font=(FONT_UI, 9), bg=BG_CARD, fg=FG_BODY,
                activebackground=ACCENT, activeforeground='#ffffff',
                anchor=tk.W, border=0, padx=10, pady=8, cursor='hand2',
            )
            btn.pack(fill=tk.X, pady=2, padx=10)
            btn.bind('<Enter>', lambda _e, b=btn, r=role: self._on_patient_btn_enter(b, r))
            btn.bind('<Leave>', lambda _e, b=btn, r=role: self._on_patient_btn_leave(b, r))
            self._patient_buttons[role] = btn

    def _on_patient_btn_enter(self, btn: tk.Widget, role: str):
        if self.selected_role.get() != role:
            btn.configure(bg='#3f4f6b')

    def _on_patient_btn_leave(self, btn: tk.Widget, role: str):
        if self.selected_role.get() != role:
            btn.configure(bg=BG_CARD)

    def _highlight_selected_patient(self):
        """Give the active patient's sidebar button a persistent accent highlight."""
        active = self.selected_role.get()
        for role, btn in self._patient_buttons.items():
            if role == active:
                btn.configure(bg=ACCENT, fg='#ffffff')
            else:
                btn.configure(bg=BG_CARD, fg=FG_BODY)

    def _nav_button(self, parent, text: str, command) -> tk.Button:
        btn = tk.Button(
            parent, text=text, width=3, command=command, font=(FONT_UI, 10, 'bold'),
            bg=BG_CARD, fg=FG_BODY, activebackground=ACCENT, activeforeground='#ffffff',
            border=0, cursor='hand2',
        )
        btn.bind('<Enter>', lambda _e: btn.configure(bg=ACCENT_HOVER))
        btn.bind('<Leave>', lambda _e: btn.configure(bg=BG_CARD))
        return btn

    # ── Notebook ──

    def _populate_notebook(self):
        """Populate notebook with cohort view + patient tabs (called after cohort is created)."""
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        self.tabs = {}

        # Add cohort view as first tab (index 0)
        cohort_frame = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(cohort_frame, text='📋 Today\'s Tasks')
        self.tabs['_cohort'] = cohort_frame
        self._cohort_frame = cohort_frame  # Save reference for updates

        # Add individual patient tabs
        for role in self.roles:
            frame = tk.Frame(self.notebook, bg=BG_DARK)
            self.notebook.add(frame, text=self.role_names[role])
            self.tabs[role] = frame

        if self.roles:
            self.notebook.select(0)  # Start on cohort view
            self.selected_role.set(self.roles[0])
            self._highlight_selected_patient()

    def _on_notebook_tab_changed(self, _event=None):
        """Keep the sidebar highlight in sync when the user clicks a notebook tab directly."""
        try:
            idx = self.notebook.index(self.notebook.select())
        except tk.TclError:
            return
        if 0 <= idx < len(self.roles):
            self.selected_role.set(self.roles[idx])
            self._highlight_selected_patient()

    # ── Cohort lifecycle ──

    def _initialize_cohort(self):
        """Show setup dialog and create or resume cohort on startup."""
        setup_dlg = SetupDialog(self)
        result = setup_dlg.show()

        if result is None:
            self.destroy()
            return

        try:
            # Handle resume vs. create new
            if result == "RESUME":
                # Resume existing cohort
                self.cohort_state = setup_dlg.resumed_state
                # Reconstruct config from saved state
                config = CohortConfig(
                    num_experimental=self.cohort_state.num_experimental,
                    num_control=self.cohort_state.num_control,
                )
                self._setup_cohort_ui(config)
                messagebox.showinfo(
                    'Cohort Resumed',
                    f'Welcome back!\n\n'
                    f'Resuming Day {self.cohort_state.cohort_day} of 187\n'
                    f'Patients: {len(self.cohort_state.patient_list or [])}'
                )
            else:
                # Create new cohort
                config = result
                self.cohort_state = cohort.create_cohort(config)
                self._setup_cohort_ui(config)

            self._update_display()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to initialize cohort:\n{e}')
            self.destroy()

    def _setup_cohort_ui(self, config: CohortConfig):
        """Setup UI elements based on cohort configuration."""
        patient_defs = generate_patient_defs(config)
        self.patient_defs = patient_defs

        self.roles = []
        self.role_names = {}
        self.role_groups = {}
        self.role_to_homer_id = {}
        for defn in patient_defs:
            role = defn['role']
            group = 'Exp' if defn['group'] == 'experimental' else 'Ctrl'
            side = defn['side']
            homer_id = defn['homer_id']

            self.roles.append(role)
            self.role_names[role] = f'{group} - {side} ({homer_id})'
            self.role_groups[role] = defn['group']
            self.role_to_homer_id[role] = homer_id

        self._populate_sidebar()
        self._populate_notebook()
        self.day_spin.configure(from_=1, to=TOTAL_DAYS)
        self.day_spin.delete(0, tk.END)
        self.day_spin.insert(0, str(self.cohort_state.cohort_day))

        # Save cohort metadata to state for resume functionality
        self.cohort_state.num_experimental = config.num_experimental
        self.cohort_state.num_control = config.num_control
        self.cohort_state.patient_list = patient_defs
        state_store.save(self.cohort_state)

        self.status_bar.set_status(
            f'Cohort active — Day {self.cohort_state.cohort_day} of {TOTAL_DAYS} · {len(self.roles)} patients',
            cohort_active=True
        )
        self.status_bar.set_progress(self.cohort_state.cohort_day, TOTAL_DAYS)

        messagebox.showinfo(
            'Cohort Created',
            f'Cohort created successfully.\n\n'
            f'Patients: {len(self.roles)}\n'
            f'  Experimental: {config.num_experimental}\n'
            f'  Control: {config.num_control}\n\n'
            f'Device pool: TRNDEV-* (up to 8 patients per group)\n\n'
            f'Progress is automatically saved. Close anytime and resume later!'
        )

    def _select_role(self, role: str):
        """Switch to a different role's tab."""
        self.selected_role.set(role)
        if role in self.roles:
            # Skip cohort view (index 0), so add 1 to role index
            self.notebook.select(self.roles.index(role) + 1)
        self._highlight_selected_patient()
        self._update_display()

    def _on_cohort_patient_selected(self, role: str):
        """Callback when user clicks a patient in the cohort view."""
        self._select_role(role)

    def _on_new_cohort(self):
        """Create a new cohort (show setup dialog)."""
        setup_dlg = SetupDialog(self)
        config = setup_dlg.show()

        if config is None:
            return

        try:
            if self.cohort_state:
                cohort.teardown_cohort(verbose=False)

            self.cohort_state = cohort.create_cohort(config)
            self._setup_cohort_ui(config)
            self._update_display()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to create cohort:\n{e}')

    def _on_teardown(self):
        """Tear down the current cohort."""
        if not self.cohort_state:
            messagebox.showwarning('No Cohort', 'No active cohort to tear down.')
            return

        if messagebox.askyesno(
            'Confirm Teardown',
            'This will delete all TRN* patients and TRNDEV-* devices.\n\nContinue?'
        ):
            try:
                cohort.teardown_cohort()
                self.cohort_state = None
                self.day_spin.delete(0, tk.END)
                self.day_spin.insert(0, '1')
                self.status_bar.set_status('No cohort loaded', cohort_active=False)
                self._update_display()
                messagebox.showinfo('Success', 'Cohort torn down successfully.')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to tear down cohort:\n{e}')

    def _on_verify(self):
        """Verify that all events are properly entered in htDash."""
        if not self.cohort_state:
            messagebox.showwarning('No Cohort', 'Create a cohort first.')
            return

        try:
            result = verify_cohort(self.cohort_state.cohort_day, self.patient_defs)
            dialog = VerificationDialog(self, result)
            dialog.show()
        except Exception as e:
            messagebox.showerror('Verification Error', f'Failed to verify events:\n{e}')

    def _on_advance_day(self):
        """Advance to the next day with force reload of dashboard."""
        if not self.cohort_state:
            messagebox.showwarning('No Cohort', 'Create a cohort first.')
            return

        if self.cohort_state.cohort_day >= TOTAL_DAYS:
            messagebox.showinfo('End of Training', f'Training simulator complete at Day {TOTAL_DAYS}.')
            return

        try:
            day_engine.advance_day(self.cohort_state)
            self.day_spin.delete(0, tk.END)
            self.day_spin.insert(0, str(self.cohort_state.cohort_day))
            self.status_bar.set_status(
                f'Cohort active — Day {self.cohort_state.cohort_day} of {TOTAL_DAYS} · {len(self.roles)} patients',
                cohort_active=True
            )
            self.status_bar.set_progress(self.cohort_state.cohort_day, TOTAL_DAYS)

            # Force reload: Clear all tabs and rebuild from scratch
            self._force_reload_dashboard()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to advance day:\n{e}')

    def _force_reload_dashboard(self):
        """Force reload the entire dashboard - clear all content and refresh."""
        try:
            # Clear content from all existing tabs (don't rebuild tabs)
            for role, frame in self.tabs.items():
                for child in frame.winfo_children():
                    child.destroy()

            # Force the update
            self.update_idletasks()

            # Update display with fresh data for current day
            self._update_display()

            # Force final UI update to flush all changes
            self.update_idletasks()

        except Exception as e:
            messagebox.showerror('Reload Error', f'Failed to reload dashboard:\n{e}')

    def _prev_day(self):
        """Go to previous day (read-only, no state change)."""
        current = int(self.day_spin.get())
        if current > 1:
            self.day_spin.delete(0, tk.END)
            self.day_spin.insert(0, str(current - 1))
            self._on_day_spin()

    def _next_day(self):
        """Go to next day (read-only, no state change)."""
        current = int(self.day_spin.get())
        if current < TOTAL_DAYS:
            self.day_spin.delete(0, tk.END)
            self.day_spin.insert(0, str(current + 1))
            self._on_day_spin()

    def _on_day_spin(self):
        """Handle day spinbox change."""
        self._update_display()

    def _update_display(self):
        """Update all role tabs + cohort view with instructions for current day + lookahead (±2 days)."""
        if not self.cohort_state:
            for role, frame in self.tabs.items():
                for child in frame.winfo_children():
                    child.destroy()
                self._empty_state(frame, 'No cohort loaded.\nClick "New Cohort" to start.')
            return

        current_day = int(self.day_spin.get())
        self.day_var.set(f'Day {current_day}')

        # Check if all patients have completed events for this day
        all_patients_done = all(
            not entries_for_day(role, current_day) for role in self.roles
        )

        # ──── Update Cohort View (Today's Tasks) ────
        cohort_frame = self.tabs.get('_cohort')
        if cohort_frame:
            for child in cohort_frame.winfo_children():
                child.destroy()

            # Gather all patients' instructions for today only (not lookahead)
            patients_data = {}
            for role in self.roles:
                # Today's events only (current_day, no lookahead)
                entries = entries_for_day(role, current_day)
                rendered_instructions = []
                for entry in entries:
                    for event in entry.events:
                        instr = instructions.render(event, self._get_patient_id(role), today=date.today())
                        rendered_instructions.append(instr)

                patients_data[role] = {
                    'homer_id': self._get_patient_id(role),
                    'group': self.role_groups.get(role),
                    'instructions': rendered_instructions,
                }

            cohort_view = CohortViewTab(
                cohort_frame, patients_data,
                on_patient_selected=self._on_cohort_patient_selected
            )
            cohort_view.pack(fill=tk.BOTH, expand=True)

        # ──── Update Individual Patient Tabs ────
        for role, frame in self.tabs.items():
            if role == '_cohort':  # Skip cohort frame
                continue

            for child in frame.winfo_children():
                child.destroy()

            # Gather instructions for today ± 2 days (lookahead range)
            # This prevents showing all 187 days at once, which is overwhelming
            rendered_instructions = self._get_instructions_for_range(role, current_day, lookahead_days=2)

            if not rendered_instructions:
                # Patient has no events in this range
                if all_patients_done:
                    # All patients done — show advance day guidance
                    self._show_day_complete_message(frame, current_day)
                else:
                    # Other patients still have events — suggest switching
                    self._show_patient_complete_message(frame, role, current_day)
                continue

            patient_id = self._get_patient_id(role)
            role_tab = RoleTab(
                frame, role, rendered_instructions,
                patient_id=patient_id, display_name=self.role_names.get(role, role),
            )
            role_tab.pack(fill=tk.BOTH, expand=True)

    def _get_instructions_for_range(self, role: str, center_day: int, lookahead_days: int = 2):
        """Gather instructions for a day range (center_day - lookahead to center_day + lookahead)."""
        rendered_instructions = []
        day_min = max(1, center_day - lookahead_days)
        day_max = min(TOTAL_DAYS, center_day + lookahead_days)

        for day in range(day_min, day_max + 1):
            entries = entries_for_day(role, day)
            for entry in entries:
                for event in entry.events:
                    instr = instructions.render(event, self._get_patient_id(role), today=date.today())
                    # Add day context to narrative if rendering from non-current day
                    if day != center_day:
                        instr.narrative = f'[Day {day}] {instr.narrative}'
                    rendered_instructions.append(instr)

        return rendered_instructions

    def _show_patient_complete_message(self, frame: tk.Frame, role: str, current_day: int):
        """Show message when a single patient has completed their events."""
        container = tk.Frame(frame, bg=BG_DARK)
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=40)

        # Completion checkmark
        tk.Label(
            container, text='✓', font=(FONT_UI, 48), fg=ACCENT, bg=BG_DARK,
        ).pack()

        # Main message
        tk.Label(
            container, text='All Events Completed!', font=(FONT_UI, 14, 'bold'),
            fg=FG_LIGHT, bg=BG_DARK,
        ).pack(pady=(12, 6))

        # Guidance
        tk.Label(
            container, text=f'Patient {self.role_names.get(role, role)} has finished all events for Day {current_day}.',
            font=(FONT_UI, 10), fg=FG_BODY, bg=BG_DARK, justify=tk.CENTER,
        ).pack(pady=(0, 12))

        tk.Label(
            container, text='👉 Switch to another patient using the sidebar',
            font=(FONT_UI, 9, 'bold'), fg=ACCENT, bg=BG_DARK, justify=tk.CENTER,
        ).pack()

    def _show_day_complete_message(self, frame: tk.Frame, current_day: int):
        """Show message when all patients have completed their events for the day."""
        container = tk.Frame(frame, bg=BG_DARK)
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=20)

        # Completion celebration
        tk.Label(
            container, text='🎉', font=(FONT_UI, 48), fg=ACCENT, bg=BG_DARK,
        ).pack()

        # Main message
        tk.Label(
            container, text=f'Day {current_day} Complete!', font=(FONT_UI, 14, 'bold'),
            fg=FG_LIGHT, bg=BG_DARK,
        ).pack(pady=(12, 8))

        tk.Label(
            container, text='All patients have completed their events.',
            font=(FONT_UI, 10), fg=FG_BODY, bg=BG_DARK, justify=tk.CENTER,
        ).pack(pady=(0, 16))

        # Divider
        tk.Frame(container, bg=BORDER, height=1).pack(fill=tk.X, pady=(0, 16))

        # Next events preview
        if current_day < TOTAL_DAYS:
            tk.Label(
                container, text='📋 Next Events Preview', font=(FONT_UI, 10, 'bold'),
                fg=ACCENT, bg=BG_DARK,
            ).pack(anchor=tk.W, pady=(0, 10))

            next_events = self._get_next_events(current_day + 1)
            if next_events:
                for patient_name, day, event_count in next_events[:3]:  # Show top 3
                    tk.Label(
                        container, text=f'• {patient_name} — Day {day} ({event_count} event{"s" if event_count != 1 else ""})',
                        font=(FONT_UI, 9), fg=FG_BODY, bg=BG_DARK, justify=tk.LEFT, anchor=tk.W,
                    ).pack(anchor=tk.W, pady=2)
            else:
                tk.Label(
                    container, text='No upcoming events', font=(FONT_UI, 9), fg=FG_MUTED, bg=BG_DARK,
                ).pack(anchor=tk.W)

            tk.Label(
                container, text='', font=(FONT_UI, 1), bg=BG_DARK,
            ).pack(pady=12)

        # Action button guidance
        tk.Label(
            container, text='👉 Click "Advance Day" to progress to the next day',
            font=(FONT_UI, 9, 'bold'), fg=ACCENT, bg=BG_DARK, justify=tk.CENTER,
        ).pack()

    def _get_next_events(self, start_day: int) -> list:
        """Find next upcoming events for all patients starting from start_day.
        Returns list of (patient_name, day, event_count) tuples."""
        next_events = []

        for role in self.roles:
            for day in range(start_day, min(start_day + 30, TOTAL_DAYS + 1)):  # Look ahead 30 days max
                entries = entries_for_day(role, day)
                if entries:
                    event_count = sum(len(entry.events) for entry in entries)
                    display_name = self.role_names.get(role, role)
                    next_events.append((display_name, day, event_count))
                    break  # Only first event day per patient

        # Sort by day, then by patient name
        next_events.sort(key=lambda x: (x[1], x[0]))
        return next_events

    @staticmethod
    def _empty_state(frame: tk.Frame, message: str):
        tk.Label(
            frame, text=message, font=(FONT_UI, 11), fg=FG_MUTED, bg=BG_DARK, justify=tk.CENTER,
        ).pack(pady=60)

    def _get_patient_id(self, role: str) -> str:
        """Get the patient ID for a given role (dynamic — assigned at cohort creation)."""
        return self.role_to_homer_id.get(role, 'TRN001')


def run():
    """Launch the training simulator UI."""
    app = MainWindow()
    app.mainloop()


if __name__ == '__main__':
    run()
