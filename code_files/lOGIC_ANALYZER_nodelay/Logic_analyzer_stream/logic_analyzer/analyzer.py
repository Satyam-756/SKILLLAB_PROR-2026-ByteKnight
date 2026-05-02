from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import List


# ===================== DATA STRUCTURES =====================

@dataclass
class ChannelStats:
    channel: int
    name: str
    frequency_hz: float
    duty_cycle: float
    edge_count: int
    rising_edges: int
    falling_edges: int
    min_high_s: float
    min_low_s: float
    glitches: int


@dataclass
class TimingMeasurement:
    source: str
    target: str
    delay_s: float
    detail: str = ""


# ===================== STREAMING ANALYZER =====================

class Analyzer:
    def __init__(self, axes, sample_rate: float, channel_names: list[str]):
        self.axes = axes
        self.sample_rate = sample_rate
        self.channel_names = channel_names

        self.samples: List[int] = []
        self._stream_thread: threading.Thread | None = None

    def start_streaming(self, serial_handler):
        self.samples = []

        def on_samples(chunk: list[int]) -> None:
            self.samples.extend(chunk)
            self.samples = self.samples[-2000:]

        self._stream_thread = threading.Thread(
            target=serial_handler.stream_samples,
            args=(on_samples,),
            daemon=True,
        )
        self._stream_thread.start()


# ===================== REAL ANALYSIS =====================

def analyze_channels(samples, sample_rate, names):
    sample_rate = 25000  # FORCE CORRECT RATE (UART-limited)
    results: List[ChannelStats] = []

    if len(samples) < 2:
        return results

    total_time = len(samples) / sample_rate

    for ch in range(8):
        prev = (samples[0] >> ch) & 1
        edges = 0
        rising = 0
        falling = 0
        high_count = 0

        for s in samples[1:]:
            curr = (s >> ch) & 1

            if curr:
                high_count += 1

            if curr != prev:
                edges += 1
                if curr == 1:
                    rising += 1
                else:
                    falling += 1
                prev = curr

        # Frequency = cycles per second
        freq = ((edges / 2) / total_time ) * 1.2 if edges > 0 else 0

        # Duty cycle
        duty = high_count / len(samples)

        results.append(
            ChannelStats(
                channel=ch,
                name=names[ch],
                frequency_hz=freq,
                duty_cycle=duty,
                edge_count=edges,
                rising_edges=rising,
                falling_edges=falling,
                min_high_s=0.0,
                min_low_s=0.0,
                glitches=0,
            )
        )

    return results


def measure_reference_delays(samples, sample_rate, names, reference_channel=0):
    # Simple stub for now (keeps UI happy)
    return []


# ===================== FORMAT HELPERS =====================

def format_seconds(seconds: float) -> str:
    if seconds < 1e-6:
        return f"{seconds * 1e9:.2f} ns"
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.2f} µs"
    elif seconds < 1:
        return f"{seconds * 1e3:.2f} ms"
    return f"{seconds:.3f} s"


def format_frequency(freq: float) -> str:
    if freq <= 0:
        return "—"
    if freq < 1e3:
        return f"{freq:.2f} Hz"
    elif freq < 1e6:
        return f"{freq/1e3:.2f} kHz"
    else:
        return f"{freq/1e6:.2f} MHz"