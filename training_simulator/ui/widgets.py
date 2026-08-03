"""Reusable Tkinter widgets for the training simulator UI.

Professional light-theme design with clean colors, excellent readability,
and modern visual hierarchy. Primary accent: Sky-blue (#0ea5e9) for focus & actions.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from training_simulator.instructions import RenderedInstruction, RenderedField

# ── Professional light-theme design tokens (modern, clean, professional) ──
BG_DARK = '#f8fafc'       # Light background — page background
BG_DARKER = '#e8eef7'     # Light blue-gray — top bar / sidebar
BG_CARD = '#ffffff'       # White — card background
BORDER = '#e2e8f0'        # Subtle light gray — dividers, card outline
FG_LIGHT = '#1e293b'      # Dark slate — headings
FG_BODY = '#334155'       # Slate — body text
FG_MUTED = '#64748b'      # Muted slate — secondary text
FG_DIM = '#475569'        # Dim slate — tertiary text
ACCENT = '#0ea5e9'        # Bright sky-blue — primary accent (professional, readable)
ACCENT_HOVER = '#0284c7'  # Darker sky-blue — hover state
VALUE_COLOR = '#0369a1'   # Teal-blue — field values (professional, readable)
FONT_UI = 'Segoe UI'
FONT_MONO = 'Consolas'

# Status → (icon, label, accent color, card tint) — light theme with professional colors
STATUS_STYLE = {
    'pending':    ('⏳', 'Pending',      '#94a3b8', '#f1f5f9'),   # slate-gray
    'incomplete': ('◐', 'In Progress',  '#f59e0b', '#fef3c7'),   # amber
    'correct':    ('◐', 'In Progress',  '#0284c7', '#e0f2fe'),   # sky-blue
    'incorrect':  ('✗', 'Needs Fixes',  '#dc2626', '#fee2e2'),   # red
    'completed':  ('✓', 'Complete',     '#16a34a', '#dcfce7'),   # green
}


class FieldChecklistRow(tk.Frame):
    """A single field label + value row in an instruction checklist."""

    def __init__(self, parent, label: str, value: str, zebra: bool = False, **kwargs):
        row_bg = '#f0f4f8' if zebra else BG_CARD
        super().__init__(parent, bg=row_bg, **kwargs)
        self.pack_propagate(True)

        # Checkbox column (clean checkmark style)
        checkbox = tk.Label(
            self, text='☐', font=(FONT_MONO, 11), fg=ACCENT, bg=row_bg, width=2
        )
        checkbox.pack(side=tk.LEFT, padx=(12, 8), pady=8, anchor=tk.NW)

        # Label + Value container (vertical layout for better text wrapping)
        content_frame = tk.Frame(self, bg=row_bg)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12), pady=8)

        label_widget = tk.Label(
            content_frame, text=label, font=(FONT_UI, 9, 'bold'),
            fg=FG_DIM, bg=row_bg, anchor=tk.W, justify=tk.LEFT,
        )
        label_widget.pack(fill=tk.X, anchor=tk.NW)

        value_widget = tk.Label(
            content_frame, text=value, font=(FONT_MONO, 9),
            fg=VALUE_COLOR, bg=row_bg, anchor=tk.NW, justify=tk.LEFT, wraplength=600,
        )
        value_widget.pack(fill=tk.BOTH, expand=True, anchor=tk.NW, pady=(2, 0))

        # Subtle bottom divider
        tk.Frame(self, bg=BORDER, height=1).pack(side=tk.BOTTOM, fill=tk.X)


class InstructionCard(tk.Frame):
    """A collapsible card displaying one instruction with narrative + field checklist.

    Visually: a colored left accent bar signals status at a glance (matches the
    STATUS_STYLE accent color), with an icon + text badge in the header for
    anyone who can't rely on color alone.
    """

    def __init__(self, parent, instruction: RenderedInstruction, status_callback=None, **kwargs):
        super().__init__(parent, bg=BORDER, **kwargs)  # outer frame = card outline color
        self.instruction = instruction
        self.status_callback = status_callback
        self._expanded = True
        self.status = 'pending'
        self.errors = []

        # Inner frame holds all real content, inset by 1px to fake a border
        self.inner = tk.Frame(self, bg=BG_CARD)
        self.inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Left accent bar (status color)
        self.accent_bar = tk.Frame(self.inner, bg=STATUS_STYLE['pending'][2], width=4)
        self.accent_bar.pack(side=tk.LEFT, fill=tk.Y)

        # Content column
        content = tk.Frame(self.inner, bg=BG_CARD)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header row (collapsible)
        header_frame = tk.Frame(content, bg=BG_CARD, cursor='hand2')
        header_frame.pack(fill=tk.X, padx=12, pady=10)
        header_frame.bind('<Button-1>', self._toggle_expand)

        self.status_icon = tk.Label(
            header_frame, text=STATUS_STYLE['pending'][0], font=(FONT_UI, 13, 'bold'),
            fg=STATUS_STYLE['pending'][2], bg=BG_CARD, width=2, cursor='hand2',
        )
        self.status_icon.pack(side=tk.LEFT, padx=(0, 6))
        self.status_icon.bind('<Button-1>', self._toggle_expand)

        self.chevron = tk.Label(
            header_frame, text='▼', font=(FONT_UI, 9, 'bold'),
            fg=ACCENT, bg=BG_CARD, width=2, cursor='hand2',
        )
        self.chevron.pack(side=tk.LEFT, padx=(0, 8))
        self.chevron.bind('<Button-1>', self._toggle_expand)

        title = tk.Label(
            header_frame, text=instruction.event_title, font=(FONT_UI, 11, 'bold'),
            fg=FG_LIGHT, bg=BG_CARD, cursor='hand2', anchor=tk.W,
        )
        title.pack(side=tk.LEFT, fill=tk.X, expand=True)
        title.bind('<Button-1>', self._toggle_expand)

        self.status_badge = tk.Label(
            header_frame, text=STATUS_STYLE['pending'][1], font=(FONT_UI, 8, 'bold'),
            fg='#ffffff', bg=STATUS_STYLE['pending'][2], padx=8, pady=2, cursor='hand2',
        )
        self.status_badge.pack(side=tk.RIGHT)
        self.status_badge.bind('<Button-1>', self._toggle_expand)

        # Body container (collapsible)
        self.body = tk.Frame(content, bg=BG_CARD)
        self.body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        narrative = tk.Label(
            self.body, text=instruction.narrative, font=(FONT_UI, 9),
            fg=FG_DIM, bg=BG_CARD, wraplength=520, justify=tk.LEFT,
        )
        narrative.pack(fill=tk.X, pady=(0, 10), anchor=tk.W)

        tk.Frame(self.body, bg=BORDER, height=1).pack(fill=tk.X, pady=(0, 8))

        # Fields checklist container (zebra-striped rows)
        fields_frame = tk.Frame(self.body, bg=BG_CARD)
        fields_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        for i, field in enumerate(instruction.fields):
            FieldChecklistRow(fields_frame, field.label, field.value, zebra=(i % 2 == 1)).pack(
                fill=tk.X, side=tk.TOP
            )

        # Lookup hint (if present)
        if instruction.lookup_hint:
            tk.Frame(self.body, bg=BORDER, height=1).pack(fill=tk.X, pady=(8, 8))
            hint = tk.Label(
                self.body, text=f'\U0001f4a1 {instruction.lookup_hint}', font=(FONT_UI, 8, 'italic'),
                fg=FG_MUTED, bg=BG_CARD, wraplength=520, justify=tk.LEFT,
            )
            hint.pack(fill=tk.X, anchor=tk.W)

        self._error_frame: Optional[tk.Frame] = None

    def _show_errors(self):
        """Display validation errors if any."""
        if self._error_frame is not None:
            self._error_frame.destroy()
            self._error_frame = None
        if not self.errors:
            return

        error_bg = '#fee2e2'  # Light red background for light theme
        self._error_frame = tk.Frame(self.body, bg=error_bg, highlightthickness=1, highlightbackground='#dc2626')
        self._error_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(
            self._error_frame, text=f'⚠ Validation Issues ({len(self.errors)})',
            font=(FONT_UI, 9, 'bold'), fg='#dc2626', bg=error_bg,
        ).pack(anchor=tk.W, padx=10, pady=(6, 3))

        for error in self.errors:
            tk.Label(
                self._error_frame, text=f'• {error}', font=(FONT_UI, 8),
                fg='#991b1b', bg=error_bg, wraplength=460, justify=tk.LEFT,
            ).pack(anchor=tk.W, padx=20, pady=1)

        tk.Frame(self._error_frame, bg=error_bg, height=6).pack()  # bottom breathing room

    def _toggle_expand(self, event=None):
        """Toggle card expansion."""
        self._expanded = not self._expanded
        if self._expanded:
            self.body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
            self.chevron.config(text='▼')
        else:
            self.body.pack_forget()
            self.chevron.config(text='▶')

    def update_status(self, status: str, errors: list = None):
        """Update event status indicator with real-time feedback."""
        self.status = status
        self.errors = errors or []

        icon, label, accent, tint = STATUS_STYLE.get(status, STATUS_STYLE['pending'])

        self.status_icon.config(text=icon, fg=accent)
        self.status_badge.config(text=label, bg=accent)
        self.accent_bar.config(bg=accent)

        # Tint every card surface consistently (card bg cascades through children
        # that were built against BG_CARD — repaint the ones that matter).
        self.inner.config(bg=tint)
        for widget in (self.status_icon, self.chevron, self.status_badge):
            pass  # icon/badge already carry their own accent bg, leave as-is

        if self.errors and self._expanded:
            self._show_errors()
        elif self._error_frame is not None:
            self._error_frame.destroy()
            self._error_frame = None


class RoleTab(tk.Frame):
    """A tab showing all instructions for a single role on the current day."""

    def __init__(self, parent, role: str, instructions: list[RenderedInstruction],
                 patient_id: str = None, display_name: str = None, **kwargs):
        super().__init__(parent, bg=BG_DARK, **kwargs)
        self.role = role
        self.patient_id = patient_id
        self.monitor = None
        self.cards = {}  # Map event_key -> InstructionCard

        # Title bar
        title_frame = tk.Frame(self, bg=BG_DARK)
        title_frame.pack(fill=tk.X, padx=16, pady=(16, 12))

        # Falls back to the raw role id (e.g. 'exp3') only if the caller didn't
        # pass a display name — main_window.py always supplies one, built from
        # the live cohort roster, so no scenario is ever silently mislabeled.
        role_label = display_name or role

        title_label = tk.Label(
            title_frame, text=f'\U0001f4cb {role_label}', font=(FONT_UI, 13, 'bold'),
            fg=ACCENT, bg=BG_DARK,
        )
        title_label.pack(side=tk.LEFT)

        count_badge = tk.Label(
            title_frame, text=f'{len(instructions)} event(s) today',
            font=(FONT_UI, 9, 'bold'), fg=FG_LIGHT if instructions else FG_MUTED,
            bg=ACCENT if instructions else BG_CARD, padx=10, pady=3,
        )
        count_badge.pack(side=tk.LEFT, padx=(12, 0))

        if patient_id:
            tk.Label(
                title_frame, text=patient_id, font=(FONT_MONO, 9),
                fg=FG_MUTED, bg=BG_DARK,
            ).pack(side=tk.RIGHT)

        # Cards container with thin scrollbar
        canvas = tk.Canvas(self, bg=BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_DARK)

        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            delta = -1 * (event.delta // 120)
            canvas.yview_scroll(delta, 'units')

        canvas.bind('<MouseWheel>', _on_mousewheel)
        scrollable_frame.bind('<MouseWheel>', _on_mousewheel)

        # Add instruction cards
        if not instructions:
            empty = tk.Frame(scrollable_frame, bg=BG_DARK)
            empty.pack(fill=tk.X, pady=60)
            tk.Label(
                empty, text='\U0001f634', font=(FONT_UI, 28), fg=FG_MUTED, bg=BG_DARK,
            ).pack()
            tk.Label(
                empty, text='No events scheduled for this day.', font=(FONT_UI, 11),
                fg=FG_MUTED, bg=BG_DARK,
            ).pack(pady=(6, 0))
        else:
            for instr in instructions:
                card = InstructionCard(scrollable_frame, instr)
                card.pack(fill=tk.X, pady=6, padx=6)
                self.cards[instr.event_key] = card

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 6))

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
                            # 'stub' (single, pre-seeded) vs 'free' (repeatable/chain) — the monitor
                            # needs this to tell a one-time protocol stub apart from a chain event
                            # like watch_record or a repeating free event like patient_call.
                            self.kind = getattr(instr, 'kind', 'stub')
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
    """Top bar showing cohort status, day progress, and control buttons."""

    def __init__(self, parent, on_new_cohort=None, on_teardown=None, on_advance=None, on_verify=None, **kwargs):
        super().__init__(parent, bg=BG_DARKER, height=68, **kwargs)
        self.pack_propagate(False)

        left = tk.Frame(self, bg=BG_DARKER)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=18, pady=10)

        self.status_label = tk.Label(
            left, text='No cohort loaded', font=(FONT_UI, 11, 'bold'),
            fg=FG_MUTED, bg=BG_DARKER, anchor=tk.W,
        )
        self.status_label.pack(anchor=tk.W)

        # Day progress bar (thin, accent-colored, fills as cohort_day approaches 187)
        self._progress_track = tk.Canvas(left, height=6, bg=BORDER, highlightthickness=0)
        self._progress_track.pack(fill=tk.X, pady=(8, 0), anchor=tk.W)
        self._progress_bar_id = None

        # Control buttons
        button_frame = tk.Frame(self, bg=BG_DARKER)
        button_frame.pack(side=tk.RIGHT, padx=15, pady=10)

        button_style = {
            'font': (FONT_UI, 9, 'bold'),
            'bg': BG_CARD,
            'fg': FG_BODY,
            'activebackground': ACCENT,
            'activeforeground': '#ffffff',
            'disabledforeground': '#475569',
            'border': 0,
            'padx': 14,
            'pady': 9,
            'cursor': 'hand2',
        }

        self.new_cohort_btn = tk.Button(
            button_frame, text='\U0001f504 New Cohort', command=on_new_cohort or (lambda: None), **button_style
        )
        self.new_cohort_btn.pack(side=tk.LEFT, padx=4)

        self.verify_btn = tk.Button(
            button_frame, text='✓ Verify Events', command=on_verify or (lambda: None), **button_style,
            state=tk.DISABLED,
        )
        self.verify_btn.pack(side=tk.LEFT, padx=4)

        self.advance_btn = tk.Button(
            button_frame, text='▶ Advance Day', command=on_advance or (lambda: None), **button_style,
            state=tk.DISABLED,
        )
        self.advance_btn.pack(side=tk.LEFT, padx=4)

        teardown_style = button_style.copy()
        teardown_style.update({'bg': '#dc2626', 'activebackground': '#b91c1c', 'fg': '#ffffff'})
        self.teardown_btn = tk.Button(
            button_frame, text='\U0001f5d1 Teardown', command=on_teardown or (lambda: None), **teardown_style,
            state=tk.DISABLED,
        )
        self.teardown_btn.pack(side=tk.LEFT, padx=4)

        self._add_hover(self.new_cohort_btn, BG_CARD, ACCENT)
        self._add_hover(self.verify_btn, BG_CARD, ACCENT)
        self._add_hover(self.advance_btn, BG_CARD, ACCENT)
        self._add_hover(self.teardown_btn, '#dc2626', '#b91c1c')

    @staticmethod
    def _add_hover(btn: tk.Button, base: str, hover: str):
        def on_enter(_e):
            if btn['state'] != tk.DISABLED:
                btn.configure(bg=hover)

        def on_leave(_e):
            if btn['state'] != tk.DISABLED:
                btn.configure(bg=base)

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

    def set_status(self, text: str, cohort_active: bool = False):
        """Update status label and button states."""
        self.status_label.config(text=text, fg=ACCENT if cohort_active else FG_MUTED)
        state = tk.NORMAL if cohort_active else tk.DISABLED
        self.verify_btn.config(state=state)
        self.advance_btn.config(state=state)
        self.teardown_btn.config(state=state)
        if not cohort_active:
            self.set_progress(0, 187)

    def set_progress(self, current_day: int, total_days: int = 187):
        """Redraw the thin day-progress bar (current_day / total_days)."""
        self._progress_track.delete('all')
        self._progress_track.update_idletasks()
        width = max(self._progress_track.winfo_width(), 1)
        height = 6
        frac = max(0.0, min(1.0, current_day / total_days)) if total_days else 0.0
        fill_width = int(width * frac)
        if fill_width > 0:
            self._progress_track.create_rectangle(
                0, 0, fill_width, height, fill=ACCENT, width=0,
            )
