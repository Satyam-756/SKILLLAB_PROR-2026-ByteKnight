"""Matplotlib waveform rendering for 8-channel captures."""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.axes


RATE_LABELS = {
    0: ("1 Hz", 1.0),
    1: ("10 Hz", 10.0),
    2: ("100 Hz", 100.0),
    3: ("1 kHz", 1_000.0),
    4: ("10 kHz", 10_000.0),
    5: ("100 kHz", 100_000.0),
    6: ("1 MHz", 1_000_000.0),
    7: ("10 MHz", 10_000_000.0),
    8: ("50 MHz", 50_000_000.0),
    9: ("100 MHz", 100_000_000.0),
}


def plot_waveforms(
    axes: matplotlib.axes.Axes,
    samples: Sequence[int],
    sample_rate: float,
    channel_names: Sequence[str],
) -> None:
    """Draw stacked digital step waveforms on the given Matplotlib axes."""
    axes.clear()
    if not samples:
        axes.set_title("No capture")
        axes.figure.canvas.draw_idle()
        return

    times = [index / sample_rate for index in range(len(samples))]
    colors = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c", "#0891b2", "#4f46e5", "#65a30d"]
    yticks: list[float] = []
    ylabels: list[str] = []
    for channel in range(8):
        offset = channel * 2.0
        values = [offset + ((sample >> channel) & 1) for sample in samples]
        axes.step(times, values, where="post", linewidth=1.2, color=colors[channel])
        yticks.append(offset + 0.5)
        ylabels.append(channel_names[channel] if channel < len(channel_names) else f"ch{channel}")

    axes.set_yticks(yticks, ylabels)
    axes.set_xlabel("Time (s)")
    axes.set_xlim(times[0], times[-1] if len(times) > 1 else 1.0 / sample_rate)
    axes.grid(True, axis="x", alpha=0.25)
    axes.set_ylim(-0.5, 15.5)
    axes.figure.tight_layout()
    axes.figure.canvas.draw_idle()
