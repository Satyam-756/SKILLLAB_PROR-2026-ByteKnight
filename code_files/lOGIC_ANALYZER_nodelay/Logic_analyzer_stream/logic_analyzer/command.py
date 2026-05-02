"""Command builders for the FPGA logic analyzer UART protocol."""

from __future__ import annotations


MAX_DEPTH = 32768


def cmd_start() -> str:
    """Return the command that arms and starts a capture."""
    return "START"


def cmd_stop() -> str:
    """Return the command that stops the current capture."""
    return "STOP"


def cmd_set_rate(rate_code: int) -> str:
    """Return a sample-rate command for rate code 0 through 9."""
    if not 0 <= rate_code <= 9:
        raise ValueError("rate_code must be between 0 and 9")
    return f"RATE:{rate_code:02d}"


def cmd_set_depth(depth: int) -> str:
    """Return a capture-depth command for 1 through 32768 samples."""
    if not 1 <= depth <= MAX_DEPTH:
        raise ValueError(f"depth must be between 1 and {MAX_DEPTH}")
    return f"DEPTH:{depth:05d}"


def cmd_set_pretrigger(count: int) -> str:
    """Return a pre-trigger sample-count command for 0 through 32767 samples."""
    if not 0 <= count < MAX_DEPTH:
        raise ValueError(f"pretrigger count must be between 0 and {MAX_DEPTH - 1}")
    return f"PRETRIG:{count:05d}"


def cmd_trig_immediate() -> str:
    """Return an immediate-trigger command."""
    return "TRIG:IMM"


def cmd_trig_rising(channel: int) -> str:
    """Return a rising-edge trigger command for channel 0 through 7."""
    if not 0 <= channel <= 7:
        raise ValueError("channel must be between 0 and 7")
    return f"TRIG:RISE:{channel}"


def cmd_trig_falling(channel: int) -> str:
    """Return a falling-edge trigger command for channel 0 through 7."""
    if not 0 <= channel <= 7:
        raise ValueError("channel must be between 0 and 7")
    return f"TRIG:FALL:{channel}"


def cmd_trig_pattern(pattern: int) -> str:
    """Return an 8-bit pattern trigger command."""
    if not 0 <= pattern <= 0xFF:
        raise ValueError("pattern must be an 8-bit value")
    return f"TRIG:PAT:{pattern:02X}"
