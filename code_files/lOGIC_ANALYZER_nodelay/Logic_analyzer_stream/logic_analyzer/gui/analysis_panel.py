"""Timing analysis and signal-quality panel."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from logic_analyzer.analyzer import (
    ChannelStats,
    TimingMeasurement,
    format_frequency,
    format_seconds,
)


class AnalysisPanel(ttk.Frame):
    """Display frequency, pulse, glitch, and inter-channel timing measurements."""

    def __init__(self, master: tk.Widget) -> None:
        super().__init__(master)

        self.summary_var = tk.StringVar(value="Capture a signal to see timing analysis.")
        ttk.Label(self, textvariable=self.summary_var).grid(row=0, column=0, sticky="ew", padx=6, pady=6)

        self.channel_tree = ttk.Treeview(
            self,
            columns=("channel", "frequency", "duty", "edges", "min_high", "min_low", "glitches"),
            show="headings",
            height=9,
        )
        headings = [
            ("channel", "Channel"),
            ("frequency", "Frequency"),
            ("duty", "Duty"),
            ("edges", "Edges"),
            ("min_high", "Min high"),
            ("min_low", "Min low"),
            ("glitches", "Glitches"),
        ]
        for column, title in headings:
            self.channel_tree.heading(column, text=title)
            self.channel_tree.column(column, width=110, anchor="center")
        self.channel_tree.column("channel", width=150, anchor="w")
        self.channel_tree.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))

        self.delay_tree = ttk.Treeview(
            self,
            columns=("source", "target", "delay", "detail"),
            show="headings",
            height=7,
        )
        for column, title in [("source", "From"), ("target", "To"), ("delay", "Delay"), ("detail", "Detail")]:
            self.delay_tree.heading(column, text=title)
            self.delay_tree.column(column, width=130, anchor="center")
        self.delay_tree.column("detail", width=260, anchor="w")
        self.delay_tree.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 6))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

    def show_analysis(
        self,
        stats: list[ChannelStats],
        delays: list[TimingMeasurement],
        sample_count: int,
        sample_rate: float,
    ) -> None:
        """Replace timing analysis contents."""
        self.channel_tree.delete(*self.channel_tree.get_children())
        self.delay_tree.delete(*self.delay_tree.get_children())

        if not stats:
            self.summary_var.set("Capture a signal to see timing analysis.")
            return

        duration = (sample_count - 1) / sample_rate if sample_count > 1 and sample_rate > 0 else 0.0
        self.summary_var.set(
            f"{sample_count} samples at {format_frequency(sample_rate)} "
            f"({format_seconds(duration)} capture window)"
        )

        for item in stats:
            self.channel_tree.insert(
                "",
                "end",
                values=(
                    f"ch{item.channel}: {item.name}",
                    format_frequency(item.frequency_hz),
                    f"{item.duty_cycle * 100:.1f}%",
                    f"{item.edge_count} ({item.rising_edges}R/{item.falling_edges}F)",
                    format_seconds(item.min_high_s),
                    format_seconds(item.min_low_s),
                    item.glitches,
                ),
            )

        for item in delays:
            self.delay_tree.insert(
                "",
                "end",
                values=(item.source, item.target, format_seconds(item.delay_s), item.detail),
            )
