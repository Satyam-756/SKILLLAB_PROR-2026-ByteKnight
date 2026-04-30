"""Threaded serial communication for the FPGA logic analyzer."""

from __future__ import annotations

import logging
import queue
import threading
import time
from collections.abc import Callable

import serial
from serial.tools import list_ports as serial_list_ports

LOGGER = logging.getLogger(__name__)


class SerialHandler:
    """Manage one pyserial connection and receive lines in a background thread."""

    def __init__(self) -> None:
        self._serial: serial.Serial | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lines: queue.Queue[str] = queue.Queue()
        self._monitor_callbacks: list[Callable[[str], None]] = []

    @property
    def is_connected(self) -> bool:
        """Return True when the serial port is open."""
        return self._serial is not None and self._serial.is_open

    @staticmethod
    def list_ports() -> list[str]:
        """Return available serial port names."""
        return [port.device for port in serial_list_ports.comports()]

    def add_monitor_callback(self, callback: Callable[[str], None]) -> None:
        """Register a callback for every received text line."""
        self._monitor_callbacks.append(callback)

    def connect(self, port: str, baud: int = 115200) -> bool:
        """Open the serial port and start the receiver thread."""
        self.disconnect()
        try:
            self._serial = serial.Serial(port=port, baudrate=baud, timeout=0.1)
        except serial.SerialException:
            LOGGER.exception("Failed to open serial port %s", port)
            self._serial = None
            return False

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        return True

    def disconnect(self) -> None:
        """Stop the receiver thread and close the serial port."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None
        if self._serial is not None:
            try:
                self._serial.close()
            except serial.SerialException:
                LOGGER.exception("Failed to close serial port")
        self._serial = None
        self._drain_lines()

    def send_command(self, command: str) -> None:
        """Send one ASCII command, appending a newline if needed."""
        if not self.is_connected or self._serial is None:
            raise RuntimeError("serial port is not connected")
        line = command if command.endswith("\n") else f"{command}\n"
        LOGGER.debug("TX: %s", line.rstrip())
        self._serial.write(line.encode("ascii"))

    def read_samples(self, expected_depth: int, timeout: float = 20.0) -> list[int]:
        """Read hex sample lines until DONE or timeout."""
        deadline = time.monotonic() + timeout
        samples: list[int] = []
        while time.monotonic() < deadline:
            try:
                line = self._lines.get(timeout=0.1).strip()
            except queue.Empty:
                continue
            if not line:
                continue
            if line == "DONE":
                return samples
            try:
                samples.append(int(line, 16) & 0xFF)
            except ValueError:
                LOGGER.debug("Ignoring non-sample line from FPGA: %r", line)
            if len(samples) >= expected_depth:
                continue
        raise TimeoutError(f"capture timed out after {len(samples)} samples")

    def _read_loop(self) -> None:
        assert self._serial is not None
        buffer = bytearray()
        while not self._stop_event.is_set() and self._serial.is_open:
            try:
                chunk = self._serial.read(128)
            except serial.SerialException:
                LOGGER.exception("Serial read failed")
                break
            if not chunk:
                continue
            for byte in chunk:
                if byte in (10, 13):
                    if buffer:
                        text = buffer.decode("ascii", errors="replace")
                        self._lines.put(text)
                        for callback in self._monitor_callbacks:
                            callback(text)
                        buffer.clear()
                else:
                    buffer.append(byte)

    def _drain_lines(self) -> None:
        while True:
            try:
                self._lines.get_nowait()
            except queue.Empty:
                return

