"""Waveform display panel."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from logic_analyzer.analyzer import format_seconds
from logic_analyzer.plotter import plot_waveforms


class WaveformPanel(ttk.Frame):
    """Embedded Matplotlib waveform viewer."""

    def __init__(self, master: tk.Widget) -> None:
        super().__init__(master)
        self.figure = Figure(figsize=(9, 5), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        self.status_var = tk.StringVar(value="Capture a signal, then click two points to measure delta time.")
        self.samples: list[int] = []
        self.sample_rate = 1.0
        self.channel_names: list[str] = []
        self.trigger_index: int | None = None
        self.cursor_line = None
        self.click_a: float | None = None
        self.click_b: float | None = None

        self.toolbar.grid(row=0, column=0, sticky="ew")
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")
        ttk.Label(self, textvariable=self.status_var).grid(row=2, column=0, sticky="ew", padx=6, pady=4)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.canvas.mpl_connect("button_press_event", self._on_click)

    def show_samples(
        self,
        samples: list[int],
        sample_rate: float,
        channel_names: list[str],
        trigger_index: int | None = None,
    ) -> None:
        """Plot new captured samples."""
        self.samples = samples
        self.sample_rate = sample_rate
        self.channel_names = channel_names
        self.trigger_index = trigger_index
        self.cursor_line = None
        self.click_a = None
        self.click_b = None
        plot_waveforms(self.axes, samples, sample_rate, channel_names, trigger_index=trigger_index)
        if samples:
            duration = (len(samples) - 1) / sample_rate if len(samples) > 1 else 0.0
            trigger_text = ""
            if trigger_index is not None and 0 <= trigger_index < len(samples):
                trigger_text = f", trigger at {format_seconds(trigger_index / sample_rate)}"
            self.status_var.set(f"{len(samples)} samples, window {format_seconds(duration)}{trigger_text}")
        else:
            self.status_var.set("No capture")

    def _sample_at_x(self, x_value: float) -> tuple[int, float, int] | None:
        if not self.samples or self.sample_rate <= 0:
            return None
        index = round(x_value * self.sample_rate)
        index = max(0, min(len(self.samples) - 1, index))
        return index, index / self.sample_rate, self.samples[index]

    def _on_motion(self, event) -> None:  # type: ignore[no-untyped-def]
        if event.inaxes != self.axes or event.xdata is None:
            return
        point = self._sample_at_x(event.xdata)
        if point is None:
            return
        index, time_s, sample = point
        if self.cursor_line is None:
            self.cursor_line = self.axes.axvline(time_s, color="#111827", alpha=0.45, linewidth=0.9)
        else:
            self.cursor_line.set_xdata([time_s, time_s])
        bits = " ".join(f"{name}:{(sample >> channel) & 1}" for channel, name in enumerate(self.channel_names[:8]))
        self.status_var.set(f"sample {index}, t={format_seconds(time_s)}, value=0x{sample:02X}  {bits}")
        self.canvas.draw_idle()

    def _on_click(self, event) -> None:  # type: ignore[no-untyped-def]
        if event.inaxes != self.axes or event.xdata is None:
            return
        point = self._sample_at_x(event.xdata)
        if point is None:
            return
        _, time_s, _ = point
        if self.click_a is None or self.click_b is not None:
            self.click_a = time_s
            self.click_b = None
            self.status_var.set(f"marker A={format_seconds(time_s)}")
            return
        self.click_b = time_s
        delta = self.click_b - self.click_a
        frequency = 1.0 / abs(delta) if delta else None
        frequency_text = f", 1/dt={frequency:.3f} Hz" if frequency else ""
        self.status_var.set(
            f"A={format_seconds(self.click_a)}, B={format_seconds(self.click_b)}, "
            f"dt={format_seconds(delta)}{frequency_text}"
        )
