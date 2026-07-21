"""
Verification dialog — interactive view of event verification results.
Modern dark theme with KPI cards and gradient styling.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List

from training_simulator.verification import (
    CohortVerification, PatientVerification, format_verification_report
)

# Modern color scheme
COLOR_BG_DARK = "#1e293b"  # slate-800
COLOR_BG_DARKER = "#0f172a"  # slate-950
COLOR_FG_LIGHT = "#e2e8f0"  # slate-200
COLOR_FG_MUTED = "#94a3b8"  # slate-400
COLOR_ACCENT_PURPLE = "#a855f7"  # purple-500
COLOR_ACCENT_BLUE = "#3b82f6"  # blue-500
COLOR_ACCENT_GREEN = "#10b981"  # emerald-500
COLOR_ACCENT_ORANGE = "#f97316"  # orange-500


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
            font=("Arial", 16, "bold"),
            fg=COLOR_FG_LIGHT,
            bg=COLOR_BG_DARKER
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = tk.Label(
            header_content,
            text=f"Cohort Day {self.result.cohort_day} / 187",
            font=("Arial", 10),
            fg=COLOR_FG_MUTED,
            bg=COLOR_BG_DARKER
        )
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))

        pass_rate_label = tk.Label(
            header_content,
            text=f"Pass Rate: {self.result.avg_pass_rate:.1f}%",
            font=("Arial", 11, "bold"),
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
        style.configure('TNotebook.Tab', padding=[20, 10], font=("Arial", 10))
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
            fg=COLOR_FG_LIGHT,
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8,
            border=0,
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT)

    def _create_kpi_card(self, parent: tk.Frame, emoji: str, label: str, value: str, accent_color: str, column: int):
        """Create a modern KPI card."""
        card = tk.Frame(parent, bg=accent_color, relief=tk.FLAT)
        card.grid(row=0, column=column, padx=8, pady=5, sticky="nsew", ipadx=15, ipady=15)
        parent.grid_columnconfigure(column, weight=1)

        # Emoji/Icon
        emoji_label = tk.Label(card, text=emoji, font=("Arial", 24), bg=accent_color, fg=COLOR_FG_LIGHT)
        emoji_label.pack()

        # Value
        value_label = tk.Label(card, text=value, font=("Arial", 16, "bold"), bg=accent_color, fg=COLOR_FG_LIGHT)
        value_label.pack(pady=(8, 0))

        # Label
        label_text = tk.Label(card, text=label, font=("Arial", 9), bg=accent_color, fg=COLOR_FG_LIGHT)
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

        report = "\n".join(lines)
        text_widget.insert(tk.END, report)
        text_widget.config(state=tk.DISABLED)

    def show(self):
        """Show the dialog and wait for user to close it."""
        self.parent.wait_window(self.dialog)
