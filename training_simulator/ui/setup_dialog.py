"""
Cohort setup dialog — allows user to configure cohort size before creation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from training_simulator.cohort_config import CohortConfig, PRESETS


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

        # Create modal window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create Training Cohort")
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._build_ui()

    def _build_ui(self):
        """Build the dialog UI."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text="Configure Cohort Size", font=("Arial", 14, "bold"))
        title.pack(pady=(0, 20))

        # ── Preset buttons ──
        presets_frame = ttk.LabelFrame(main_frame, text="Quick Presets", padding="10")
        presets_frame.pack(fill=tk.X, pady=(0, 20))

        for preset_name, preset_config in PRESETS.items():
            btn = ttk.Button(
                presets_frame,
                text=f"{preset_name.capitalize()}\n({preset_config.num_experimental} exp + {preset_config.num_control} ctrl)",
                command=lambda cfg=preset_config: self._select_preset(cfg),
            )
            btn.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

        # ── Or custom ──
        ttk.Label(main_frame, text="Or select custom:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 10))

        # Experimental spinbox
        exp_frame = ttk.Frame(main_frame)
        exp_frame.pack(fill=tk.X, pady=5)
        ttk.Label(exp_frame, text="Experimental patients:", width=20).pack(side=tk.LEFT)
        self.exp_var = tk.IntVar(value=2)
        exp_spin = ttk.Spinbox(exp_frame, from_=1, to=8, textvariable=self.exp_var, width=5)
        exp_spin.pack(side=tk.LEFT, padx=5)

        # Control spinbox
        ctrl_frame = ttk.Frame(main_frame)
        ctrl_frame.pack(fill=tk.X, pady=5)
        ttk.Label(ctrl_frame, text="Control patients:", width=20).pack(side=tk.LEFT)
        self.ctrl_var = tk.IntVar(value=2)
        ctrl_spin = ttk.Spinbox(ctrl_frame, from_=1, to=8, textvariable=self.ctrl_var, width=5)
        ctrl_spin.pack(side=tk.LEFT, padx=5)

        # Info text
        info_text = (
            "Patient pool: up to 8 patients total\n"
            "Tracks cycle: 5 exp scenarios × 2 sides (right/left)\n"
            "              5 ctrl scenarios × 2 sides\n"
            "Example: 10 exp patients → cycles through exp1-5 twice"
        )
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT, font=("Arial", 9))
        info_label.pack(anchor=tk.W, pady=(15, 0))

        # ── Buttons ──
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        create_btn = ttk.Button(button_frame, text="Create Cohort", command=self._on_create)
        create_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def _select_preset(self, config: CohortConfig):
        """User clicked a preset button."""
        self.config = config
        self.result = config
        self.dialog.destroy()

    def _on_create(self):
        """User clicked Create Cohort (custom spinbox values)."""
        exp = self.exp_var.get()
        ctrl = self.ctrl_var.get()
        self.config = CohortConfig(num_experimental=exp, num_control=ctrl)

        if not self.config.validate():
            messagebox.showerror("Invalid Config", "Please select 1-8 patients per group")
            return

        self.result = self.config
        self.dialog.destroy()

    def _on_cancel(self):
        """User clicked Cancel."""
        self.result = None
        self.dialog.destroy()

    def show(self) -> Optional[CohortConfig]:
        """
        Show the dialog and wait for user input.

        Returns:
            CohortConfig if user created a cohort, None if cancelled.
        """
        self.parent.wait_window(self.dialog)
        return self.result
