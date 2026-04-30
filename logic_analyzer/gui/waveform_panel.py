"""Waveform display panel."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from logic_analyzer.plotter import plot_waveforms


class WaveformPanel(ttk.Frame):
    """Embedded Matplotlib waveform viewer."""

    def __init__(self, master: tk.Widget) -> None:
        super().__init__(master)
        self.figure = Figure(figsize=(9, 5), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        self.toolbar.grid(row=0, column=0, sticky="ew")
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def show_samples(self, samples: list[int], sample_rate: float, channel_names: list[str]) -> None:
        """Plot new captured samples."""
        plot_waveforms(self.axes, samples, sample_rate, channel_names)

