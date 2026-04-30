"""Capture configuration controls."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from collections.abc import Callable

from logic_analyzer.plotter import RATE_LABELS


class ConfigPanel(ttk.LabelFrame):
    """Panel for sample rate, depth, trigger, and channel names."""

    def __init__(
        self,
        master: tk.Widget,
        on_apply: Callable[[], None],
        on_start: Callable[[], None],
        on_stop: Callable[[], None],
    ) -> None:
        super().__init__(master, text="Capture")
        self._on_apply = on_apply
        self._on_start = on_start
        self._on_stop = on_stop

        self.rate_var = tk.IntVar(value=5)
        self.depth_var = tk.IntVar(value=1024)
        self.trigger_var = tk.StringVar(value="Immediate")
        self.trigger_channel_var = tk.IntVar(value=0)
        self.pattern_var = tk.StringVar(value="00")
        self.channel_vars = [tk.StringVar(value=f"ch{i}") for i in range(8)]

        ttk.Label(self, text="Rate").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        self.rate_combo = ttk.Combobox(
            self,
            values=[f"{code}: {label}" for code, (label, _) in RATE_LABELS.items()],
            state="readonly",
            width=14,
        )
        self.rate_combo.current(5)
        self.rate_combo.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

        ttk.Label(self, text="Depth").grid(row=0, column=2, padx=6, pady=4, sticky="w")
        ttk.Spinbox(self, from_=1, to=32768, textvariable=self.depth_var, width=8).grid(
            row=0, column=3, padx=6, pady=4, sticky="ew"
        )

        ttk.Label(self, text="Trigger").grid(row=1, column=0, padx=6, pady=4, sticky="w")
        ttk.Combobox(
            self,
            textvariable=self.trigger_var,
            values=["Immediate", "Rising", "Falling", "Pattern"],
            state="readonly",
            width=12,
        ).grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        ttk.Label(self, text="Channel").grid(row=1, column=2, padx=6, pady=4, sticky="w")
        ttk.Spinbox(self, from_=0, to=7, textvariable=self.trigger_channel_var, width=4).grid(
            row=1, column=3, padx=6, pady=4, sticky="w"
        )
        ttk.Label(self, text="Pattern").grid(row=1, column=4, padx=6, pady=4, sticky="w")
        ttk.Entry(self, textvariable=self.pattern_var, width=5).grid(row=1, column=5, padx=6, pady=4)

        for index, var in enumerate(self.channel_vars):
            ttk.Label(self, text=f"Ch {index}").grid(row=2 + index // 4, column=(index % 4) * 2, padx=6, pady=4)
            ttk.Entry(self, textvariable=var, width=10).grid(
                row=2 + index // 4, column=(index % 4) * 2 + 1, padx=6, pady=4
            )

        ttk.Button(self, text="Apply", command=self._on_apply).grid(row=4, column=0, padx=6, pady=8)
        ttk.Button(self, text="Start", command=self._on_start).grid(row=4, column=1, padx=6, pady=8)
        ttk.Button(self, text="Stop", command=self._on_stop).grid(row=4, column=2, padx=6, pady=8)

        for column in range(6):
            self.columnconfigure(column, weight=1)

    def rate_code(self) -> int:
        """Return the selected numeric sample-rate code."""
        return int(self.rate_combo.get().split(":", maxsplit=1)[0])

    def sample_rate(self) -> float:
        """Return the selected sample rate in samples per second."""
        return RATE_LABELS[self.rate_code()][1]

    def channel_names(self) -> list[str]:
        """Return the current channel labels."""
        return [var.get().strip() or f"ch{index}" for index, var in enumerate(self.channel_vars)]

