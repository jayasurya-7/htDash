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
from training_simulator.ui.widgets import CohortStatusBar, RoleTab
from training_simulator.ui.setup_dialog import SetupDialog
from training_simulator.ui.verification_dialog import VerificationDialog


class MainWindow(tk.Tk):
    """Main Tkinter window for training simulator."""

    def __init__(self):
        super().__init__()
        self.title('htDash Training Simulator v2')
        self.geometry('1400x850')

        # Apply modern dark theme
        self.configure(bg='#1e293b')  # slate-800

        self.cohort_state = None
        self.selected_role = tk.StringVar()

        # Dynamic roles and role names (populated after cohort is created)
        self.roles: List[str] = []
        self.role_names: Dict[str, str] = {}

        self._build_ui()
        self._initialize_cohort()  # Show setup dialog and create cohort

    def _build_ui(self):
        """Build the UI layout (framework only - patient tabs populated after cohort setup)."""
        # Configure ttk style for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#1e293b')
        style.configure('TLabel', background='#1e293b', foreground='#e2e8f0')
        style.configure('TButton', background='#334155', foreground='#e2e8f0')
        style.configure('TNotebook', background='#1e293b', borderwidth=0)
        style.configure('TNotebook.Tab', padding=[15, 8], font=('Arial', 10))
        style.map('TNotebook.Tab', background=[('selected', '#a855f7')])

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
        self.main_container = tk.Frame(self, bg='#1e293b')
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Left sidebar (will be populated dynamically)
        self.sidebar = tk.Frame(self.main_container, bg='#0f172a', width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=10)
        self.sidebar.pack_propagate(False)

        # Content area (right side) — role tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

        # Placeholder (will be populated after cohort created)
        self.tabs = {}

    def _populate_sidebar(self):
        """Populate sidebar with patient buttons (called after cohort is created)."""
        # Clear sidebar first
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        # Patients label
        patients_label = tk.Label(
            self.sidebar,
            text='👥 Patients',
            font=('Arial', 11, 'bold'),
            fg='#a855f7',
            bg='#0f172a'
        )
        patients_label.pack(pady=(10, 15), padx=10)

        # Patient buttons
        for role in self.roles:
            btn = tk.Button(
                self.sidebar,
                text=self.role_names[role],
                command=lambda r=role: self._select_role(r),
                font=('Arial', 9),
                bg='#334155',
                fg='#e2e8f0',
                activebackground='#a855f7',
                activeforeground='#ffffff',
                border=0,
                padx=10,
                pady=8,
                cursor='hand2'
            )
            btn.pack(fill=tk.X, pady=4, padx=8)

        # Day navigation (sidebar)
        separator = tk.Frame(self.sidebar, bg='#334155', height=1)
        separator.pack(fill=tk.X, pady=15, padx=10)

        # Day navigation label
        nav_label = tk.Label(
            self.sidebar,
            text='📅 Day Navigation',
            font=('Arial', 10, 'bold'),
            fg='#a855f7',
            bg='#0f172a'
        )
        nav_label.pack(pady=(0, 10), padx=10)

        # Navigation frame
        nav_frame = tk.Frame(self.sidebar, bg='#0f172a')
        nav_frame.pack(fill=tk.X, padx=8)

        # Previous day button
        prev_btn = tk.Button(
            nav_frame,
            text='◀',
            width=3,
            command=self._prev_day,
            font=('Arial', 10, 'bold'),
            bg='#334155',
            fg='#e2e8f0',
            activebackground='#a855f7',
            border=0,
            cursor='hand2'
        )
        prev_btn.pack(side=tk.LEFT, padx=2)

        # Day label
        self.day_var = tk.StringVar(value='Day 1')
        day_label = tk.Label(
            nav_frame,
            textvariable=self.day_var,
            font=('Arial', 9, 'bold'),
            fg='#e2e8f0',
            bg='#0f172a'
        )
        day_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Next day button
        next_btn = tk.Button(
            nav_frame,
            text='▶',
            width=3,
            command=self._next_day,
            font=('Arial', 10, 'bold'),
            bg='#334155',
            fg='#e2e8f0',
            activebackground='#a855f7',
            border=0,
            cursor='hand2'
        )
        next_btn.pack(side=tk.RIGHT, padx=2)

        # Day spinbox
        self.day_spin = tk.Spinbox(
            self.sidebar,
            from_=1,
            to=187,
            width=10,
            font=('Courier', 9),
            command=self._on_day_spin,
            bg='#334155',
            fg='#e2e8f0',
            buttonbackground='#a855f7',
            bd=0
        )
        self.day_spin.pack(fill=tk.X, pady=8, padx=8)
        self.day_spin.delete(0, tk.END)
        self.day_spin.insert(0, '1')

    def _populate_notebook(self):
        """Populate notebook with patient tabs (called after cohort is created)."""
        # Clear notebook first
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        self.tabs = {}
        for role in self.roles:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=self.role_names[role])
            self.tabs[role] = frame

        # Select first tab
        if self.roles:
            self.notebook.select(0)
            self.selected_role.set(self.roles[0])

    def _initialize_cohort(self):
        """Show setup dialog and create cohort on startup."""
        setup_dlg = SetupDialog(self)
        config = setup_dlg.show()

        if config is None:
            # User cancelled
            self.destroy()
            return

        # Create cohort with selected config
        try:
            self.cohort_state = cohort.create_cohort(config)
            self._setup_cohort_ui(config)
            self._update_display()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to create cohort:\n{e}')
            self.destroy()

    def _setup_cohort_ui(self, config: CohortConfig):
        """Setup UI elements based on cohort configuration."""
        from training_simulator.cohort_config import generate_patient_defs

        patient_defs = generate_patient_defs(config)

        # Build roles and role_names lists
        self.roles = []
        self.role_names = {}
        for defn in patient_defs:
            role = defn['role']
            group = 'Exp' if defn['group'] == 'experimental' else 'Ctrl'
            side = defn['side']
            homer_id = defn['homer_id']

            self.roles.append(role)
            self.role_names[role] = f'{group} - {side} ({homer_id})'

        # Populate UI
        self._populate_sidebar()
        self._populate_notebook()
        self.day_spin.configure(from_=1, to=187)
        self.day_spin.delete(0, tk.END)
        self.day_spin.insert(0, '1')

        self.status_bar.set_status(
            f'Cohort active: Day {self.cohort_state.cohort_day} of 187 ({len(self.roles)} patients)',
            cohort_active=True
        )

        messagebox.showinfo(
            'Success',
            f'Cohort created successfully.\n\n'
            f'Patients: {len(self.roles)}\n'
            f'  Experimental: {config.num_experimental}\n'
            f'  Control: {config.num_control}\n\n'
            f'Device pool: TRNDEV-* (up to 8 patients supported)'
        )

    def _select_role(self, role: str):
        """Switch to a different role's tab."""
        self.selected_role.set(role)
        if role in self.roles:
            self.notebook.select(self.roles.index(role))
            self._update_display()

    def _on_new_cohort(self):
        """Create a new cohort (show setup dialog)."""
        setup_dlg = SetupDialog(self)
        config = setup_dlg.show()

        if config is None:
            return

        try:
            # Tear down existing cohort first
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
            # Get patient definitions
            from training_simulator.cohort_config import CohortConfig
            # We need to reconstruct the config from the current roles
            # Count exp vs ctrl by looking at patient defs
            patient_defs = []
            for role in self.roles:
                # Find the patient def for this role
                for key, value in self.role_names.items():
                    if key == role:
                        # Extract homer_id from role_names (format: "Exp/Ctrl - Side (TRN###)")
                        import re
                        match = re.search(r'\(TRN\d+\)', self.role_names[role])
                        if match:
                            homer_id = match.group(0).strip('()')
                            # Determine group and side
                            is_exp = 'Exp' in self.role_names[role]
                            group = 'experimental' if is_exp else 'control'
                            side = 'Right' if 'Right' in self.role_names[role] else 'Left'
                            patient_defs.append({
                                'role': role,
                                'homer_id': homer_id,
                                'group': group,
                                'side': side,
                            })
                        break

            # Run verification
            result = verify_cohort(self.cohort_state.cohort_day, patient_defs)

            # Show verification dialog
            dialog = VerificationDialog(self, result)
            dialog.show()

        except Exception as e:
            messagebox.showerror('Verification Error', f'Failed to verify events:\n{e}')

    def _on_advance_day(self):
        """Advance to the next day."""
        if not self.cohort_state:
            messagebox.showwarning('No Cohort', 'Create a cohort first.')
            return

        if self.cohort_state.cohort_day >= 187:
            messagebox.showinfo('End of Training', 'Training simulator complete at Day 187.')
            return

        try:
            day_engine.advance_day(self.cohort_state)
            self.day_spin.delete(0, tk.END)
            self.day_spin.insert(0, str(self.cohort_state.cohort_day))
            self.status_bar.set_status(
                f'Cohort active: Day {self.cohort_state.cohort_day} of 187 (TRN001-004)',
                cohort_active=True
            )
            self._update_display()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to advance day:\n{e}')

    def _prev_day(self):
        """Go to previous day (read-only, no state change)."""
        current = int(self.day_spin.get())
        if current > 1:
            self.day_spin.delete(0, tk.END)
            self.day_spin.insert(0, str(current - 1))

    def _next_day(self):
        """Go to next day (read-only, no state change)."""
        current = int(self.day_spin.get())
        if current < 187:
            self.day_spin.delete(0, tk.END)
            self.day_spin.insert(0, str(current + 1))

    def _on_day_spin(self):
        """Handle day spinbox change."""
        self._update_display()

    def _update_display(self):
        """Update all role tabs with instructions for the current day."""
        if not self.cohort_state:
            # No cohort — show placeholder
            for role, frame in self.tabs.items():
                # Clear frame
                for child in frame.winfo_children():
                    child.destroy()
                ttk.Label(frame, text='No cohort loaded.\nClick "New Cohort" to start.',
                          font=('TkDefaultFont', 11), foreground='#888888').pack(pady=40)
            return

        # Get current day from spinbox
        current_day = int(self.day_spin.get())
        self.day_var.set(f'Day {current_day}')

        # Update each role tab
        for role, frame in self.tabs.items():
            # Clear frame
            for child in frame.winfo_children():
                child.destroy()

            # Get instructions for this role/day
            entries = entries_for_day(role, current_day)
            if not entries:
                ttk.Label(frame, text=f'No events on Day {current_day}.',
                          font=('TkDefaultFont', 11), foreground='#888888').pack(pady=40)
                continue

            # Render instructions
            rendered_instructions = []
            for entry in entries:
                for event in entry.events:
                    instr = instructions.render(event, self._get_patient_id(role), today=date.today())
                    rendered_instructions.append(instr)

            if not rendered_instructions:
                trainer_note = entries[0].trainer_note if entries else 'No events scheduled.'
                ttk.Label(frame, text=trainer_note,
                          font=('TkDefaultFont', 11), foreground='#888888').pack(pady=40)
            else:
                # Create role tab with instructions and patient ID for real-time monitoring
                patient_id = self._get_patient_id(role)
                role_tab = RoleTab(frame, role, rendered_instructions, patient_id=patient_id)
                role_tab.pack(fill=tk.BOTH, expand=True)

    def _get_patient_id(self, role: str) -> str:
        """Get the patient ID for a given role."""
        id_map = {'exp1': 'TRN001', 'exp2': 'TRN002', 'ctrl1': 'TRN003', 'ctrl2': 'TRN004'}
        return id_map.get(role, 'TRN001')


def run():
    """Launch the training simulator UI."""
    app = MainWindow()
    app.mainloop()


if __name__ == '__main__':
    run()
