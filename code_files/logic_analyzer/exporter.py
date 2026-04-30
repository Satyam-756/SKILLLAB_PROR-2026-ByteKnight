"""CSV and VCD export for captured 8-channel samples."""

from __future__ import annotations

import csv
from pathlib import Path


def export_csv(path: str | Path, samples: list[int], sample_rate: float) -> None:
    """Export samples to CSV with seconds and one column per channel."""
    output = Path(path)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_s", *[f"ch{i}" for i in range(8)]])
        for index, sample in enumerate(samples):
            writer.writerow(
                [index / sample_rate, *[(sample >> bit) & 1 for bit in range(8)]]
            )


def export_vcd(
    path: str | Path,
    samples: list[int],
    sample_rate: float,
    channel_names: list[str] | None = None,
) -> None:
    """Export value changes to a GTKWave-compatible VCD file."""
    output = Path(path)
    names = channel_names or [f"ch{i}" for i in range(8)]
    symbols = ["!", '"', "#", "$", "%", "&", "'", "("]
    tick_ns = max(1, round(1_000_000_000 / sample_rate))
    previous = [None] * 8

    with output.open("w", encoding="utf-8") as handle:
        handle.write("$timescale 1 ns $end\n")
        handle.write("$scope module logic_analyzer $end\n")
        for bit, symbol in enumerate(symbols):
            safe_name = names[bit].replace(" ", "_")
            handle.write(f"$var wire 1 {symbol} {safe_name} $end\n")
        handle.write("$upscope $end\n$enddefinitions $end\n")

        for index, sample in enumerate(samples):
            changes: list[str] = []
            for bit, symbol in enumerate(symbols):
                value = (sample >> bit) & 1
                if previous[bit] != value:
                    previous[bit] = value
                    changes.append(f"{value}{symbol}\n")
            if changes:
                handle.write(f"#{index * tick_ns}\n")
                handle.writelines(changes)

