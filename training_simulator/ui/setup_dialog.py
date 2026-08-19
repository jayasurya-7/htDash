"""
Cohort setup dialog — allows user to configure cohort size before creation.
Styled with professional light theme for clean, readable interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from training_simulator.cohort_config import CohortConfig, PRESETS
from training_simulator import state as state_store

# Professional light-theme palette (kept in sync with widgets.py / verification_dialog.py)
BG_DARK = '#f8fafc'      # Light background — dialog background
BG_DARKER = '#e8eef7'    # Light blue-gray — header / footer strip
BG_CARD = '#ffffff'      # White — cards, inputs
BG_CARD_HOVER = '#f1f5f9'  # Light hover state
BORDER = '#e2e8f0'       # Subtle light gray
FG_LIGHT = '#1e293b'     # Dark slate — headings
FG_BODY = '#334155'      # Slate — body text
FG_MUTED = '#64748b'     # Muted slate — secondary text
ACCENT = '#0ea5e9'       # Sky-blue — primary accent
ACCENT_HOVER = '#0284c7' # Darker sky-blue — hover state
FONT_FAMILY = 'Segoe UI'


class SetupDialog:
    """Modal dialog for cohort configuration."""

    def __init__(self, parent: tk.Tk):
        """
        Initialize setup dialog.

        Args:
            parent: Parent Tk window (typically the main window).
        """
        self.parent = parent
        self.config: Optional[CohortConfig] = None
        self.result = None  # Will hold the selected config or None if cancelled
        self.resumed_state = None  # Will hold the resumed state if resuming
        self._preset_cards = []

        # Create modal window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title('Create Training Cohort')
        self.dialog.geometry('460x620')
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=BG_DARK)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self._center_on_parent()

        self._build_ui()

    def _center_on_parent(self):
        """Center the dialog over its parent window."""
        self.dialog.update_idletasks()
        try:
            px, py = self.parent.winfo_x(), self.parent.winfo_y()
            pw, ph = self.parent.winfo_width(), self.parent.winfo_height()
            dw, dh = 460, 620
            x = px + (pw - dw) // 2
            y = py + (ph - dh) // 2
            self.dialog.geometry(f'{dw}x{dh}+{max(x, 0)}+{max(y, 0)}')
        except tk.TclError:
            pass

    def _build_ui(self):
        """Build the dialog UI."""
        # Check if there's an existing cohort to resume
        existing_state = state_store.load()

        # ── Header strip ──
        header = tk.Frame(self.dialog, bg=BG_DARKER)
        header.pack(fill=tk.X)

        # If cohort exists, show resume option
        if existing_state:
            tk.Label(
                header, text='🧪 Resume or Create Cohort',
                font=(FONT_FAMILY, 15, 'bold'), fg=FG_LIGHT, bg=BG_DARKER,
            ).pack(anchor=tk.W, padx=20, pady=(16, 2))
            tk.Label(
                header, text='A training cohort is in progress. You can resume it or start fresh.',
                font=(FONT_FAMILY, 9), fg=FG_MUTED, bg=BG_DARKER,
            ).pack(anchor=tk.W, padx=20, pady=(0, 16))
        else:
            tk.Label(
                header, text='🧪 Configure Cohort Size',
                font=(FONT_FAMILY, 15, 'bold'), fg=FG_LIGHT, bg=BG_DARKER,
            ).pack(anchor=tk.W, padx=20, pady=(16, 2))
            tk.Label(
                header, text='Choose how many simulated patients to create for this training run.',
                font=(FONT_FAMILY, 9), fg=FG_MUTED, bg=BG_DARKER,
            ).pack(anchor=tk.W, padx=20, pady=(0, 16))

        body = tk.Frame(self.dialog, bg=BG_DARK)
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # ── Resume button (if cohort exists) ──
        if existing_state:
            resume_card = tk.Frame(body, bg='#d1fae5', highlightthickness=1, highlightbackground='#10b981')
            resume_card.pack(fill=tk.X, pady=(0, 16))
            resume_inner = tk.Frame(resume_card, bg='#d1fae5')
            resume_inner.pack(fill=tk.X, padx=14, pady=12)

            info_text = f"Day {existing_state.cohort_day}/187 · {existing_state.num_experimental} exp + {existing_state.num_control} ctrl patients"
            tk.Label(
                resume_inner, text='✓ Saved Progress Found',
                font=(FONT_FAMILY, 11, 'bold'), fg='#065f46', bg='#d1fae5', anchor=tk.W,
            ).pack(anchor=tk.W)
            tk.Label(
                resume_inner, text=info_text,
                font=(FONT_FAMILY, 9), fg='#047857', bg='#d1fae5', anchor=tk.W,
            ).pack(anchor=tk.W, pady=(4, 0))

            button_frame_resume = tk.Frame(body, bg=BG_DARK)
            button_frame_resume.pack(fill=tk.X, pady=(0, 14))
            self._make_button(
                button_frame_resume, '▶ Resume Training', lambda: self._on_resume(existing_state),
                bg='#10b981', hover_bg='#059669', fg='#ffffff', side=tk.LEFT,
            )

            # Divider
            tk.Frame(body, bg=BORDER, height=1).pack(fill=tk.X, pady=(0, 14))

        # ── Quick presets ──
        tk.Label(
            body, text='QUICK PRESETS', font=(FONT_FAMILY, 9, 'bold'),
            fg=ACCENT, bg=BG_DARK,
        ).pack(anchor=tk.W, pady=(0, 8))

        presets_frame = tk.Frame(body, bg=BG_DARK)
        presets_frame.pack(fill=tk.X, pady=(0, 20))
        for i, (preset_name, preset_config) in enumerate(PRESETS.items()):
            presets_frame.grid_columnconfigure(i, weight=1)
            self._build_preset_card(presets_frame, preset_name, preset_config, i)

        # ── Divider ──
        tk.Frame(body, bg=BORDER, height=1).pack(fill=tk.X, pady=(0, 18))

        # ── Custom selection ──
        tk.Label(
            body, text='OR CUSTOMIZE', font=(FONT_FAMILY, 9, 'bold'),
            fg=ACCENT, bg=BG_DARK,
        ).pack(anchor=tk.W, pady=(0, 10))

        custom_card = tk.Frame(body, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER)
        custom_card.pack(fill=tk.X, pady=(0, 18))
        inner = tk.Frame(custom_card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=16, pady=14)

        self.exp_var = tk.IntVar(value=2)
        self._build_spin_row(inner, 'Experimental patients', self.exp_var)

        self.ctrl_var = tk.IntVar(value=2)
        self._build_spin_row(inner, 'Control patients', self.ctrl_var)

        # ── Info panel (subtle, professional) ──
        info_card = tk.Frame(body, bg='#f0f4f8', highlightthickness=1, highlightbackground=BORDER)
        info_card.pack(fill=tk.X, pady=(0, 18))
        info_inner = tk.Frame(info_card, bg='#f0f4f8')
        info_inner.pack(fill=tk.X, padx=14, pady=12)
        tk.Label(
            info_inner, text='ℹ  Patient pool: up to 8 tracks per group.',
            font=(FONT_FAMILY, 9), fg=FG_MUTED, bg='#f0f4f8', justify=tk.LEFT, anchor=tk.W,
        ).pack(anchor=tk.W)
        tk.Label(
            info_inner,
            text='Requesting more than 5 of a group cycles back through\nexp1-5 / ctrl1-5, alternating Right/Left training side.',
            font=(FONT_FAMILY, 9), fg=FG_MUTED, bg='#f0f4f8', justify=tk.LEFT, anchor=tk.W,
        ).pack(anchor=tk.W, pady=(4, 0))

        # ── Buttons ──
        button_frame = tk.Frame(body, bg=BG_DARK)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(4, 0))

        self._make_button(
            button_frame, 'Create Cohort', self._on_create,
            bg=ACCENT, hover_bg=ACCENT_HOVER, fg='#ffffff', side=tk.RIGHT,
        )
        self._make_button(
            button_frame, 'Cancel', self._on_cancel,
            bg=BG_CARD, hover_bg=BG_CARD_HOVER, fg=FG_BODY, side=tk.RIGHT, padx=(0, 8),
        )

    # ── Helpers ──

    def _build_preset_card(self, parent, name: str, preset_config: CohortConfig, column: int):
        """A clickable preset card with hover feedback."""
        card = tk.Frame(parent, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER, cursor='hand2')
        card.grid(row=0, column=column, padx=6, sticky='nsew', ipady=10)

        title = tk.Label(
            card, text=name.capitalize(), font=(FONT_FAMILY, 10, 'bold'),
            fg=FG_LIGHT, bg=BG_CARD, cursor='hand2',
        )
        title.pack(pady=(8, 2))
        subtitle = tk.Label(
            card, text=f'{preset_config.num_experimental} exp · {preset_config.num_control} ctrl',
            font=(FONT_FAMILY, 8), fg=FG_MUTED, bg=BG_CARD, cursor='hand2',
        )
        subtitle.pack(pady=(0, 8))

        widgets = [card, title, subtitle]

        def on_enter(_e=None):
            for w in widgets:
                w.configure(bg=BG_CARD_HOVER)
            card.configure(highlightbackground=ACCENT)

        def on_leave(_e=None):
            for w in widgets:
                w.configure(bg=BG_CARD)
            card.configure(highlightbackground=BORDER)

        def on_click(_e=None):
            self._select_preset(preset_config)

        for w in widgets:
            w.bind('<Enter>', on_enter)
            w.bind('<Leave>', on_leave)
            w.bind('<Button-1>', on_click)

    def _build_spin_row(self, parent, label: str, var: tk.IntVar):
        row = tk.Frame(parent, bg=BG_CARD)
        row.pack(fill=tk.X, pady=6)
        tk.Label(
            row, text=label, font=(FONT_FAMILY, 9), fg=FG_BODY, bg=BG_CARD, anchor=tk.W,
        ).pack(side=tk.LEFT)
        spin = tk.Spinbox(
            row, from_=1, to=8, textvariable=var, width=4,
            font=(FONT_FAMILY, 10), bg=BG_DARKER, fg=FG_LIGHT,
            buttonbackground=ACCENT, insertbackground=FG_LIGHT,
            relief=tk.FLAT, justify=tk.CENTER,
        )
        spin.pack(side=tk.RIGHT)

    def _make_button(self, parent, text, command, bg, hover_bg, fg, side, padx=0):
        btn = tk.Button(
            parent, text=text, command=command,
            font=(FONT_FAMILY, 10, 'bold'), bg=bg, fg=fg,
            activebackground=hover_bg, activeforeground=fg,
            relief=tk.FLAT, border=0, padx=18, pady=9, cursor='hand2',
        )
        btn.pack(side=side, padx=padx)
        btn.bind('<Enter>', lambda _e: btn.configure(bg=hover_bg))
        btn.bind('<Leave>', lambda _e: btn.configure(bg=bg))
        return btn

    # ── Actions ──

    def _select_preset(self, config: CohortConfig):
        """User clicked a preset card."""
        self.config = config
        self.result = config
        self.dialog.destroy()

    def _on_create(self):
        """User clicked Create Cohort (custom spinbox values)."""
        exp = self.exp_var.get()
        ctrl = self.ctrl_var.get()
        self.config = CohortConfig(num_experimental=exp, num_control=ctrl)

        if not self.config.validate():
            messagebox.showerror('Invalid Config', 'Please select 1-8 patients per group')
            return

        self.result = self.config
        self.dialog.destroy()

    def _on_cancel(self):
        """User clicked Cancel."""
        self.result = None
        self.dialog.destroy()

    def _on_resume(self, state):
        """User clicked Resume Cohort."""
        # Set result to a special marker indicating resume
        self.result = "RESUME"
        self.resumed_state = state
        self.dialog.destroy()

    def show(self):
        """
        Show the dialog and wait for user input.

        Returns:
            CohortConfig if user created a cohort, None if cancelled.
        """
        self.parent.wait_window(self.dialog)
        return self.result
