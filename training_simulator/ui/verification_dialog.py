"""
Verification dialog — interactive view of event verification results.
Professional light theme with clean cards and readable typography.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List

from training_simulator.verification import (
    CohortVerification, PatientVerification, format_verification_report
)

# Professional light-theme color scheme
COLOR_BG_DARK = "#f8fafc"  # Light background
COLOR_BG_DARKER = "#e8eef7"  # Light blue-gray header
COLOR_FG_LIGHT = "#1e293b"  # Dark slate headings
COLOR_FG_MUTED = "#64748b"  # Muted slate text
COLOR_ACCENT_PURPLE = "#0ea5e9"  # Sky-blue primary
COLOR_ACCENT_BLUE = "#0284c7"  # Darker sky-blue
COLOR_ACCENT_GREEN = "#16a34a"  # Green success
COLOR_ACCENT_ORANGE = "#ea580c"  # Orange warning


class VerificationDialog:
    """Modal dialog showing verification results."""

    def __init__(self, parent: tk.Tk, result: CohortVerification):
        """
        Initialize verification dialog.

        Args:
            parent: Parent Tk window
            result: CohortVerification results to display
        """
        self.parent = parent
        self.result = result

        # Create modal window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Event Verification Report")
        self.dialog.geometry("1200x750")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Configure dark theme
        self.dialog.configure(bg=COLOR_BG_DARK)

        self._build_ui()

    def _build_ui(self):
        """Build the dialog UI with modern styling."""
        # Header with gradient effect
        header_frame = tk.Frame(self.dialog, bg=COLOR_BG_DARKER, height=80)
        header_frame.pack(fill=tk.X)

        header_content = tk.Frame(header_frame, bg=COLOR_BG_DARKER)
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        title_label = tk.Label(
            header_content,
            text="✓ Event Verification Report",
            font=("Segoe UI", 16, "bold"),
            fg=COLOR_FG_LIGHT,
            bg=COLOR_BG_DARKER
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = tk.Label(
            header_content,
            text=f"Cohort Day {self.result.cohort_day} / 187",
            font=("Segoe UI", 10),
            fg=COLOR_FG_MUTED,
            bg=COLOR_BG_DARKER
        )
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))

        pass_rate_label = tk.Label(
            header_content,
            text=f"Pass Rate: {self.result.avg_pass_rate:.1f}%",
            font=("Segoe UI", 11, "bold"),
            fg=COLOR_ACCENT_PURPLE,
            bg=COLOR_BG_DARKER
        )
        pass_rate_label.pack(side=tk.RIGHT)

        # KPI Cards section
        kpi_frame = tk.Frame(self.dialog, bg=COLOR_BG_DARK)
        kpi_frame.pack(fill=tk.X, padx=15, pady=15)

        # Calculate metrics
        completion_pct = (self.result.total_filed_events / self.result.total_expected_events * 100) if self.result.total_expected_events > 0 else 0
        pass_patients = sum(1 for p in self.result.patients if p.pass_rate >= 100)

        # KPI Cards
        self._create_kpi_card(kpi_frame, "👥", "Total Patients", str(self.result.total_patients), COLOR_ACCENT_BLUE, 0)
        self._create_kpi_card(kpi_frame, "📋", "Expected Events", str(self.result.total_expected_events), COLOR_ACCENT_BLUE, 1)
        self._create_kpi_card(kpi_frame, "✅", "Filed Events", str(self.result.total_filed_events), COLOR_ACCENT_GREEN, 2)
        self._create_kpi_card(kpi_frame, "🎯", "Pass Rate", f"{self.result.avg_pass_rate:.1f}%", COLOR_ACCENT_ORANGE, 3)

        # Tabs: Summary vs Detailed
        # Style the notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=COLOR_BG_DARK, borderwidth=0)
        style.configure('TNotebook.Tab', padding=[20, 10], font=("Segoe UI", 10))
        style.map('TNotebook.Tab', background=[("selected", COLOR_ACCENT_PURPLE)])

        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Tab 1: Summary report (text)
        summary_frame = tk.Frame(notebook, bg=COLOR_BG_DARK)
        notebook.add(summary_frame, text="📊 Summary")
        self._build_summary_tab(summary_frame)

        # Tab 2: Detailed list (treeview)
        detail_frame = tk.Frame(notebook, bg=COLOR_BG_DARK)
        notebook.add(detail_frame, text="📋 Detailed")
        self._build_detail_tab(detail_frame)

        # Tab 3: Missing events
        missing_frame = tk.Frame(notebook, bg=COLOR_BG_DARK)
        notebook.add(missing_frame, text="🔍 Missing Events")
        self._build_missing_tab(missing_frame)

        # Close button
        button_frame = tk.Frame(self.dialog, bg=COLOR_BG_DARK)
        button_frame.pack(fill=tk.X, padx=15, pady=15)

        close_btn = tk.Button(
            button_frame,
            text="Close",
            command=self.dialog.destroy,
            bg=COLOR_ACCENT_PURPLE,
            fg="#ffffff",
            activebackground="#9333ea",
            activeforeground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
            border=0,
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind('<Enter>', lambda _e: close_btn.configure(bg="#9333ea"))
        close_btn.bind('<Leave>', lambda _e: close_btn.configure(bg=COLOR_ACCENT_PURPLE))

    def _create_kpi_card(self, parent: tk.Frame, emoji: str, label: str, value: str, accent_color: str, column: int):
        """Create a modern KPI card."""
        card = tk.Frame(parent, bg=accent_color, relief=tk.FLAT)
        card.grid(row=0, column=column, padx=8, pady=5, sticky="nsew", ipadx=15, ipady=15)
        parent.grid_columnconfigure(column, weight=1)

        # Emoji/Icon
        emoji_label = tk.Label(card, text=emoji, font=("Segoe UI", 24), bg=accent_color, fg=COLOR_FG_LIGHT)
        emoji_label.pack()

        # Value
        value_label = tk.Label(card, text=value, font=("Segoe UI", 16, "bold"), bg=accent_color, fg=COLOR_FG_LIGHT)
        value_label.pack(pady=(8, 0))

        # Label
        label_text = tk.Label(card, text=label, font=("Segoe UI", 9), bg=accent_color, fg=COLOR_FG_LIGHT)
        label_text.pack(pady=(4, 0))

    def _build_summary_tab(self, parent: tk.Frame):
        """Build summary report tab with scrolled text."""
        text_widget = scrolledtext.ScrolledText(
            parent,
            font=("Courier", 9),
            wrap=tk.WORD,
            height=30,
            width=120,
            bg=COLOR_BG_DARKER,
            fg=COLOR_FG_LIGHT,
            insertbackground=COLOR_ACCENT_PURPLE
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, format_verification_report(self.result))
        text_widget.config(state=tk.DISABLED)

    def _build_detail_tab(self, parent: tk.Frame):
        """Build detailed results tab with treeview."""
        # Configure treeview style
        style = ttk.Style()
        style.configure('Treeview', background=COLOR_BG_DARKER, foreground=COLOR_FG_LIGHT, fieldbackground=COLOR_BG_DARKER)
        style.configure('Treeview.Heading', background=COLOR_BG_DARK, foreground=COLOR_FG_LIGHT, relief=tk.FLAT)
        style.map('Treeview', background=[('selected', COLOR_ACCENT_PURPLE)])

        # Treeview with columns
        columns = ('Patient', 'Role', 'Expected', 'Filed', 'Complete', 'Rate')
        tree = ttk.Treeview(parent, columns=columns, height=25, style='Treeview')

        tree.column('#0', width=0, stretch=tk.NO)
        tree.column('Patient', anchor=tk.W, width=100)
        tree.column('Role', anchor=tk.CENTER, width=80)
        tree.column('Expected', anchor=tk.CENTER, width=80)
        tree.column('Filed', anchor=tk.CENTER, width=80)
        tree.column('Complete', anchor=tk.CENTER, width=80)
        tree.column('Rate', anchor=tk.CENTER, width=100)

        tree.heading('#0', text='', anchor=tk.W)
        tree.heading('Patient', text='Patient', anchor=tk.W)
        tree.heading('Role', text='Track', anchor=tk.CENTER)
        tree.heading('Expected', text='Expected', anchor=tk.CENTER)
        tree.heading('Filed', text='Filed', anchor=tk.CENTER)
        tree.heading('Complete', text='Complete', anchor=tk.CENTER)
        tree.heading('Rate', text='Pass Rate', anchor=tk.CENTER)

        # Add patient rows
        for patient in self.result.patients:
            rate_color = 'pass' if patient.pass_rate >= 100 else 'fail'
            rate_text = f"{patient.pass_rate:.1f}%"

            tree.insert(
                '',
                'end',
                text='',
                values=(
                    patient.homer_id,
                    patient.role,
                    patient.total_expected,
                    patient.total_filed,
                    patient.total_completed,
                    rate_text,
                ),
                tags=(rate_color,)
            )

        # Style tags with modern colors
        tree.tag_configure('pass', foreground=COLOR_ACCENT_GREEN)
        tree.tag_configure('fail', foreground=COLOR_ACCENT_ORANGE)

        # Scrollbars
        vsb = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        hsb = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        vsb.grid(row=0, column=1, sticky='ns', padx=(0, 10))
        hsb.grid(row=1, column=0, sticky='ew', padx=10)

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

    def _build_missing_tab(self, parent: tk.Frame):
        """Build missing events tab."""
        # List of patients with missing events
        text_widget = scrolledtext.ScrolledText(
            parent,
            font=("Courier", 9),
            wrap=tk.WORD,
            height=30,
            width=120,
            bg=COLOR_BG_DARKER,
            fg=COLOR_FG_LIGHT,
            insertbackground=COLOR_ACCENT_PURPLE
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        lines = []

        # Group by pass/fail
        by_status = self.result.patients_by_status()

        if by_status['pass']:
            lines.append("✓ ALL EVENTS FILED (Pass)")
            lines.append("=" * 80)
            for p in by_status['pass']:
                lines.append(f"  {p.homer_id} ({p.role}): {p.total_filed}/{p.total_expected}")
            lines.append("")

        if by_status['fail']:
            lines.append("✗ MISSING EVENTS (Fail)")
            lines.append("=" * 80)
            for p in by_status['fail']:
                lines.append(f"\n{p.homer_id} ({p.role}): {p.total_filed}/{p.total_expected} filed")
                missing = p.missing_events()
                for evt in missing:
                    lines.append(f"  • {evt.event_key:30} (Day {evt.cohort_day:3})")
                    if evt.hint:
                        # Wrap hint text for readability
                        hint_lines = []
                        words = evt.hint.split()
                        current_line = ""
                        for word in words:
                            if len(current_line) + len(word) + 1 > 70:
                                hint_lines.append(current_line)
                                current_line = word
                            else:
                                current_line = (current_line + " " + word).strip()
                        if current_line:
                            hint_lines.append(current_line)
                        for hint_line in hint_lines:
                            lines.append(f"    → {hint_line}")

        report = "\n".join(lines)
        text_widget.insert(tk.END, report)
        text_widget.config(state=tk.DISABLED)

    def show(self):
        """Show the dialog and wait for user to close it."""
        self.parent.wait_window(self.dialog)
