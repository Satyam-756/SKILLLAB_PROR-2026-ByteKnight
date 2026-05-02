"""Threaded serial communication for streaming FPGA logic analyzer."""

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
        return self._serial is not None and self._serial.is_open

    @staticmethod
    def list_ports() -> list[str]:
        return [port.device for port in serial_list_ports.comports()]

    def add_monitor_callback(self, callback: Callable[[str], None]) -> None:
        self._monitor_callbacks.append(callback)

    def connect(self, port: str, baud: int = 921600) -> bool:
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

    # ===================== NEW STREAMING FUNCTION =====================

    def stream_samples(self, callback: Callable[[list[int]], None]) -> None:
        """
        Continuously read hex samples and send chunks to callback.
        """
        buffer: list[int] = []

        while not self._stop_event.is_set():
            try:
                line = self._lines.get(timeout=0.1).strip()
            except queue.Empty:
                continue

            if not line:
                continue

            # Ignore old protocol lines if any
            if line == "DONE" or line.startswith("TRIGPOS"):
                continue

            try:
                value = int(line, 16) & 0xFF
                buffer.append(value)
            except ValueError:
                LOGGER.debug("Ignoring non-sample line: %r", line)
                continue

            # Send chunk to UI
            if len(buffer) >= 200:
                callback(buffer.copy())
                buffer.clear()

    # ===================== SERIAL READ LOOP =====================

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
                if byte in (10, 13):  # newline
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