"""
Cohort view tab — unified "Today's Tasks" showing all patients' events for current day.

Trainer sees all 10 patients' tasks at once, grouped by experimental/control,
so they can manage the cross-patient workflow (similar to real htDash Dashboard).
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict

from training_simulator.instructions import RenderedInstruction, RenderedField

# Professional light-theme design tokens (matches widgets.py)
BG_DARK = '#f8fafc'       # Light background — page background
BG_DARKER = '#e8eef7'     # Light blue-gray — top bar / sidebar
BG_CARD = '#ffffff'       # White — card background
BORDER = '#e2e8f0'        # Subtle light gray — dividers, card outline
FG_LIGHT = '#1e293b'      # Dark slate — headings
FG_BODY = '#334155'       # Slate — body text
FG_MUTED = '#64748b'      # Muted slate — secondary text
ACCENT = '#0ea5e9'        # Bright sky-blue — primary accent
ACCENT_HOVER = '#0284c7'  # Darker sky-blue — hover state
FONT_UI = 'Segoe UI'
FONT_MONO = 'Consolas'


class CohortViewTab(tk.Frame):
    """Unified "Today's Tasks" view showing all patients + their events for current day."""

    def __init__(self, parent, patients_data: Dict[str, dict], on_patient_selected=None, **kwargs):
        """
        Initialize cohort view tab.

        Args:
            parent: Parent Tkinter widget
            patients_data: Dict mapping role → {homer_id, group, instructions}
            on_patient_selected: Callback(role) when user clicks a patient
        """
        super().__init__(parent, bg=BG_DARK, **kwargs)
        self.patients_data = patients_data
        self.on_patient_selected = on_patient_selected

        self._build_ui()

    def _build_ui(self):
        """Build the cohort view UI with grouped patient sections."""
        # Header
        header = tk.Frame(self, bg=BG_DARKER, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg=BG_DARKER)
        header_content.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        title = tk.Label(
            header_content, text='📋 Today\'s Tasks — All Patients',
            font=(FONT_UI, 14, 'bold'), fg=FG_LIGHT, bg=BG_DARKER,
        )
        title.pack(side=tk.LEFT)

        subtitle = tk.Label(
            header_content, text='Click a patient or event to see details',
            font=(FONT_UI, 9), fg=FG_MUTED, bg=BG_DARKER,
        )
        subtitle.pack(side=tk.LEFT, padx=(16, 0))

        # Main scrollable container
        canvas_frame = tk.Frame(self, bg=BG_DARK)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame, bg=BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_DARK)

        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        canvas.bind_all('<MouseWheel>', on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Build patient groups (experimental, then control)
        self._build_patient_groups(scrollable_frame)

    def _build_patient_groups(self, parent):
        """Build grouped patient sections (experimental, then control)."""
        # Separate by group
        exp_patients = [
            (role, data) for role, data in self.patients_data.items()
            if data.get('group') == 'experimental'
        ]
        ctrl_patients = [
            (role, data) for role, data in self.patients_data.items()
            if data.get('group') == 'control'
        ]

        if exp_patients:
            self._build_group_section(parent, 'EXPERIMENTAL', exp_patients, '#38bdf8')

        if ctrl_patients:
            self._build_group_section(parent, 'CONTROL', ctrl_patients, '#fb923c')

    def _build_group_section(self, parent, group_label: str, patients: List[tuple], dot_color: str):
        """Build a group section (experimental or control) with patient cards."""
        # Group header
        group_header = tk.Frame(parent, bg=BG_DARK)
        group_header.pack(fill=tk.X, padx=16, pady=(16, 8))

        dot = tk.Label(
            group_header, text='●', font=(FONT_UI, 12), fg=dot_color, bg=BG_DARK,
        )
        dot.pack(side=tk.LEFT, padx=(0, 8))

        label = tk.Label(
            group_header, text=group_label, font=(FONT_UI, 11, 'bold'),
            fg=FG_LIGHT, bg=BG_DARK,
        )
        label.pack(side=tk.LEFT)

        # Patient cards
        for role, data in patients:
            self._build_patient_card(parent, role, data, dot_color)

    def _build_patient_card(self, parent, role: str, data: dict, accent_color: str):
        """Build a patient card with their today's instructions."""
        homer_id = data.get('homer_id', role)
        instructions = data.get('instructions', [])

        # Card container
        card = tk.Frame(parent, bg=BORDER)
        card.pack(fill=tk.X, padx=16, pady=8)

        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Left accent bar
        accent_bar = tk.Frame(inner, bg=accent_color, width=4)
        accent_bar.pack(side=tk.LEFT, fill=tk.Y)

        # Card content
        content = tk.Frame(inner, bg=BG_CARD)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header row — clickable to select patient
        header_frame = tk.Frame(content, bg=BG_CARD, cursor='hand2')
        header_frame.pack(fill=tk.X, padx=12, pady=10)

        # Bind click to select patient
        def on_click_patient(event=None):
            if self.on_patient_selected:
                self.on_patient_selected(role)

        header_frame.bind('<Button-1>', on_click_patient)

        patient_name = tk.Label(
            header_frame, text=f'{homer_id}', font=(FONT_UI, 11, 'bold'),
            fg=FG_LIGHT, bg=BG_CARD, cursor='hand2',
        )
        patient_name.pack(side=tk.LEFT)
        patient_name.bind('<Button-1>', on_click_patient)

        event_count = tk.Label(
            header_frame, text=f'{len(instructions)} event{"s" if len(instructions) != 1 else ""}',
            font=(FONT_UI, 9), fg=FG_MUTED, bg=BG_CARD,
        )
        event_count.pack(side=tk.LEFT, padx=(12, 0))

        # Events list (if any)
        if instructions:
            events_frame = tk.Frame(content, bg=BG_CARD)
            events_frame.pack(fill=tk.X, padx=12, pady=(0, 10))

            for instr in instructions:
                self._build_event_mini_card(events_frame, instr, role)
        else:
            no_events = tk.Label(
                content, text='No events scheduled for today',
                font=(FONT_UI, 9, 'italic'), fg=FG_MUTED, bg=BG_CARD,
            )
            no_events.pack(padx=12, pady=(0, 10))

    def _build_event_mini_card(self, parent, instruction: RenderedInstruction, role: str):
        """Build a mini event card inside a patient card."""
        event_card = tk.Frame(parent, bg='#f1f5f9', relief=tk.FLAT)
        event_card.pack(fill=tk.X, pady=4)

        # Event title
        title = tk.Label(
            event_card, text=f'→ {instruction.event_title}',
            font=(FONT_UI, 9, 'bold'), fg=FG_BODY, bg='#f1f5f9', anchor=tk.W,
        )
        title.pack(fill=tk.X, padx=8, pady=(6, 2))

        # Event narrative (summary only, first 60 chars)
        narrative_short = instruction.narrative[:60]
        if len(instruction.narrative) > 60:
            narrative_short += '…'

        narrative = tk.Label(
            event_card, text=narrative_short, font=(FONT_UI, 8),
            fg=FG_MUTED, bg='#f1f5f9', anchor=tk.W, wraplength=400, justify=tk.LEFT,
        )
        narrative.pack(fill=tk.X, padx=8, pady=(0, 6))

        # Learn note (if present) — amber badge
        if instruction.learn_note:
            note_label = tk.Label(
                event_card, text=f'ℹ️ {instruction.learn_note}',
                font=(FONT_UI, 8), fg='#b45309', bg='#fef3c7',
                anchor=tk.W, wraplength=400, justify=tk.LEFT, padx=6, pady=4,
            )
            note_label.pack(fill=tk.X, padx=8, pady=(0, 6))

        # "Click to view full details" hint
        click_hint = tk.Label(
            event_card, text='Click patient name to see full details',
            font=(FONT_UI, 8, 'italic'), fg=ACCENT, bg='#f1f5f9',
        )
        click_hint.pack(fill=tk.X, padx=8, pady=(0, 4))
