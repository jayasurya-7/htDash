"""Reusable Tkinter widgets for the training simulator UI."""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from training_simulator.instructions import RenderedInstruction, RenderedField


class FieldChecklistRow(tk.Frame):
    """A single field label + value row in an instruction checklist."""

    def __init__(self, parent, label: str, value: str, **kwargs):
        super().__init__(parent, bg='#334155', **kwargs)
        self.pack_propagate(True)

        # Checkbox column (unfilled, just placeholder)
        checkbox = tk.Label(
            self, text='[ ]', font=('Courier', 10), fg='#94a3b8', bg='#334155', width=3
        )
        checkbox.pack(side=tk.LEFT, padx=(10, 5), pady=4, anchor=tk.NW)

        # Label + Value container (vertical layout for better text wrapping)
        content_frame = tk.Frame(self, bg='#334155')
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=4)

        # Label row
        label_widget = tk.Label(
            content_frame,
            text=label,
            font=('Arial', 9, 'bold'),
            fg='#cbd5e1',
            bg='#334155',
            anchor=tk.W,
            justify=tk.LEFT
        )
        label_widget.pack(fill=tk.X, anchor=tk.NW)

        # Value row (monospace for readability, with word wrapping)
        value_widget = tk.Label(
            content_frame,
            text=value,
            font=('Courier', 9),
            fg='#60a5fa',  # blue-400
            bg='#334155',
            anchor=tk.NW,
            justify=tk.LEFT,
            wraplength=600
        )
        value_widget.pack(fill=tk.BOTH, expand=True, anchor=tk.NW)


class InstructionCard(tk.Frame):
    """A collapsible card displaying one instruction with narrative + field checklist."""

    def __init__(self, parent, instruction: RenderedInstruction, status_callback=None, **kwargs):
        super().__init__(parent, bg='#334155', relief=tk.FLAT, bd=1, **kwargs)
        self.instruction = instruction
        self.status_callback = status_callback
        self._expanded = True
        self.status = 'pending'  # pending, incomplete, correct, incorrect, completed
        self.errors = []

        # Header row (collapsible)
        header_frame = tk.Frame(self, bg='#334155', cursor='hand2')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.bind('<Button-1>', self._toggle_expand)

        # Status indicator
        self.status_indicator = tk.Label(
            header_frame, text='⏳', font=('Arial', 12, 'bold'),
            fg='#64748b', bg='#334155', width=2, cursor='hand2'
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 8))
        self.status_indicator.bind('<Button-1>', self._toggle_expand)

        # Chevron (expand/collapse indicator)
        self.chevron = tk.Label(
            header_frame, text='▼', font=('Arial', 10, 'bold'),
            fg='#a855f7', bg='#334155', width=2, cursor='hand2'
        )
        self.chevron.pack(side=tk.LEFT, padx=(0, 8))
        self.chevron.bind('<Button-1>', self._toggle_expand)

        # Event title
        title = tk.Label(
            header_frame,
            text=instruction.event_title,
            font=('Arial', 11, 'bold'),
            fg='#e2e8f0',
            bg='#334155',
            cursor='hand2'
        )
        title.pack(side=tk.LEFT, fill=tk.X, expand=True)
        title.bind('<Button-1>', self._toggle_expand)

        # Body container (collapsible)
        self.body = tk.Frame(self, bg='#334155')
        self.body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Narrative
        narrative = tk.Label(
            self.body,
            text=instruction.narrative,
            font=('Arial', 9),
            fg='#cbd5e1',
            bg='#334155',
            wraplength=500,
            justify=tk.LEFT
        )
        narrative.pack(fill=tk.X, pady=(0, 10))

        # Separator
        separator = tk.Frame(self.body, bg='#475569', height=1)
        separator.pack(fill=tk.X, pady=8)

        # Fields checklist container
        fields_frame = tk.Frame(self.body, bg='#334155')
        fields_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        for field in instruction.fields:
            FieldChecklistRow(fields_frame, field.label, field.value).pack(
                fill=tk.X, side=tk.TOP
            )

        # Lookup hint (if present)
        if instruction.lookup_hint:
            separator2 = tk.Frame(self.body, bg='#475569', height=1)
            separator2.pack(fill=tk.X, pady=8)
            hint = tk.Label(
                self.body,
                text=f"💡 {instruction.lookup_hint}",
                font=('Arial', 8, 'italic'),
                fg='#a8adb5',
                bg='#334155',
                wraplength=500,
                justify=tk.LEFT
            )
            hint.pack(fill=tk.X, pady=5)

    def _show_errors(self):
        """Display validation errors if any."""
        if not self.errors:
            return

        error_frame = tk.Frame(self.body, bg='#ef444415')
        error_frame.pack(fill=tk.X, pady=(10, 0))

        error_title = tk.Label(
            error_frame,
            text=f"⚠️ Validation Errors ({len(self.errors)})",
            font=('Arial', 9, 'bold'),
            fg='#ef4444',
            bg='#ef444415'
        )
        error_title.pack(anchor=tk.W, padx=10, pady=(5, 3))

        for error in self.errors:
            error_label = tk.Label(
                error_frame,
                text=f"• {error}",
                font=('Arial', 8),
                fg='#fca5a5',
                bg='#ef444415',
                wraplength=400,
                justify=tk.LEFT
            )
            error_label.pack(anchor=tk.W, padx=20, pady=1)

    def _toggle_expand(self, event=None):
        """Toggle card expansion."""
        self._expanded = not self._expanded
        if self._expanded:
            self.body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            self.chevron.config(text='▼')
        else:
            self.body.pack_forget()
            self.chevron.config(text='▶')

    def update_status(self, status: str, errors: list = None):
        """Update event status indicator with real-time feedback."""
        self.status = status
        self.errors = errors or []

        # Map status to icon and color
        status_map = {
            'pending': ('⏳', '#64748b'),           # Gray - waiting
            'incomplete': ('◐', '#f59e0b'),        # Amber - partially filled
            'correct': ('◐', '#6366f1'),           # Indigo - good progress
            'incorrect': ('✗', '#ef4444'),         # Red - errors
            'completed': ('✓', '#10b981'),         # Green - done!
        }

        icon, color = status_map.get(status, ('?', '#64748b'))
        self.status_indicator.config(text=icon, fg=color)

        # Also change card background tint based on status
        bg_map = {
            'completed': '#1a7a4a',    # Green tint
            'incorrect': '#8b2e2e',    # Red tint
            'correct': '#2e3a66',      # Indigo tint
            'incomplete': '#6b5218',   # Amber tint
            'pending': '#334155',      # Normal
        }
        self.config(bg=bg_map.get(status, '#334155'))

        # Show errors if any
        if self.errors and self._expanded:
            self._show_errors()


class RoleTab(tk.Frame):
    """A tab showing all instructions for a single role on the current day."""

    def __init__(self, parent, role: str, instructions: list[RenderedInstruction], patient_id: str = None, **kwargs):
        super().__init__(parent, bg='#1e293b', **kwargs)
        self.role = role
        self.patient_id = patient_id
        self.monitor = None
        self.cards = {}  # Map event_key -> InstructionCard

        # Title bar
        title_frame = tk.Frame(self, bg='#1e293b')
        title_frame.pack(fill=tk.X, padx=15, pady=15)

        role_name = {
            'exp1': 'Experimental 1 (Right)',
            'exp2': 'Experimental 2 (Left)',
            'ctrl1': 'Control 1 (Right)',
            'ctrl2': 'Control 2 (Left)',
        }.get(role, role)

        title_label = tk.Label(
            title_frame,
            text=f"📋 {role_name} — {len(instructions)} event(s)",
            font=('Arial', 13, 'bold'),
            fg='#a855f7',
            bg='#1e293b'
        )
        title_label.pack(side=tk.LEFT)

        # Cards container with thin scrollbar
        canvas = tk.Canvas(self, bg='#1e293b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e293b')

        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Mousewheel scrolling support
        def _on_mousewheel(event):
            # event.delta is positive for scroll up, negative for scroll down
            delta = -1 * (event.delta // 120)
            canvas.yview_scroll(delta, "units")

        # Bind to canvas
        canvas.bind('<MouseWheel>', _on_mousewheel)
        # Also bind to scrollable_frame for when focus is on cards
        scrollable_frame.bind('<MouseWheel>', _on_mousewheel)

        # Add instruction cards
        if not instructions:
            no_events_label = tk.Label(
                scrollable_frame,
                text='😴 No events scheduled for this day.',
                font=('Arial', 11),
                fg='#94a3b8',
                bg='#1e293b'
            )
            no_events_label.pack(pady=40)
        else:
            for instr in instructions:
                card = InstructionCard(scrollable_frame, instr)
                card.pack(fill=tk.X, pady=8, padx=5)
                self.cards[instr.event_key] = card

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5))

        # Start monitoring if patient_id provided
        if patient_id:
            self.start_monitoring()

    def start_monitoring(self):
        """Start real-time event monitoring."""
        if not self.patient_id or self.monitor:
            print(f"[Monitor] Skipping - patient_id={self.patient_id}, already_running={self.monitor is not None}")
            return

        try:
            from training_simulator.realtime_monitor import RealtimeMonitor

            print(f"[Monitor] Starting for {self.patient_id} (role={self.role})")
            self.monitor = RealtimeMonitor(self.patient_id, self.role)

            # Register scripted events so monitor can validate against expected values
            for event_key, card in self.cards.items():
                if hasattr(card, 'instruction') and card.instruction:
                    # Store the instruction which has the expected field values
                    # Create a simple object that has event_key and fields
                    class ScriptedEventProxy:
                        def __init__(self, instr):
                            self.event_key = instr.event_key
                            # Convert RenderedField list back to dict for comparison
                            self.fields = {f.label: f.value for f in instr.fields}

                    proxy = ScriptedEventProxy(card.instruction)
                    self.monitor.register_event(proxy)

            self.monitor.on_status_change = self._on_event_status_change
            self.monitor.start_monitoring()
            print(f"[Monitor] Started successfully for {self.patient_id}")
        except Exception as e:
            print(f"[Monitor] Failed to start for {self.patient_id}: {e}")
            import traceback
            traceback.print_exc()

    def _on_event_status_change(self, event_key: str, status: str):
        """Callback when event status changes."""
        print(f"[Callback {self.patient_id}] Event {event_key}: {status}")
        if event_key in self.cards:
            print(f"[Callback] Found card for {event_key}")
            card = self.cards[event_key]
            if self.monitor:
                _, errors = self.monitor.get_status(event_key)
                card.update_status(status, errors)
        else:
            print(f"[Callback] No card found for {event_key}. Available cards: {list(self.cards.keys())}")

    def stop_monitoring(self):
        """Stop monitoring when tab is hidden."""
        if self.monitor:
            self.monitor.stop_monitoring()


class CohortStatusBar(tk.Frame):
    """Top bar showing cohort status and control buttons."""

    def __init__(self, parent, on_new_cohort=None, on_teardown=None, on_advance=None, on_verify=None, **kwargs):
        super().__init__(parent, bg='#0f172a', height=60, **kwargs)
        self.pack_propagate(False)

        # Status text
        self.status_label = tk.Label(
            self,
            text='No cohort loaded',
            font=('Arial', 11, 'bold'),
            fg='#a855f7',
            bg='#0f172a'
        )
        self.status_label.pack(side=tk.LEFT, padx=15, pady=15, fill=tk.X, expand=True)

        # Control buttons
        button_frame = tk.Frame(self, bg='#0f172a')
        button_frame.pack(side=tk.RIGHT, padx=15, pady=10)

        # Button styling
        button_style = {
            'font': ('Arial', 9, 'bold'),
            'bg': '#334155',
            'fg': '#e2e8f0',
            'activebackground': '#a855f7',
            'activeforeground': '#ffffff',
            'border': 0,
            'padx': 15,
            'pady': 8,
            'cursor': 'hand2'
        }

        self.new_cohort_btn = tk.Button(
            button_frame, text='New Cohort', command=on_new_cohort or (lambda: None), **button_style
        )
        self.new_cohort_btn.pack(side=tk.LEFT, padx=5)

        self.verify_btn = tk.Button(
            button_frame, text='Verify Events', command=on_verify or (lambda: None), **button_style,
            state=tk.DISABLED, disabledforeground='#64748b'
        )
        self.verify_btn.pack(side=tk.LEFT, padx=5)

        self.advance_btn = tk.Button(
            button_frame, text='Advance Day', command=on_advance or (lambda: None), **button_style,
            state=tk.DISABLED, disabledforeground='#64748b'
        )
        self.advance_btn.pack(side=tk.LEFT, padx=5)

        # Teardown button with red styling
        teardown_style = button_style.copy()
        teardown_style.update({'bg': '#dc2626', 'activebackground': '#b91c1c'})
        self.teardown_btn = tk.Button(
            button_frame, text='Teardown', command=on_teardown or (lambda: None), **teardown_style,
            state=tk.DISABLED, disabledforeground='#64748b'
        )
        self.teardown_btn.pack(side=tk.LEFT, padx=5)

    def set_status(self, text: str, cohort_active: bool = False):
        """Update status label and button states."""
        self.status_label.config(text=text, fg='#a855f7' if cohort_active else '#64748b')
        self.verify_btn.config(state=tk.NORMAL if cohort_active else tk.DISABLED)
        self.advance_btn.config(state=tk.NORMAL if cohort_active else tk.DISABLED)
        self.teardown_btn.config(state=tk.NORMAL if cohort_active else tk.DISABLED)
