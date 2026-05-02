"""Main Tkinter window for the FPGA logic analyzer (STREAMING MODE)."""

from __future__ import annotations

import logging
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from logic_analyzer import command
from logic_analyzer.analyzer import analyze_channels, measure_reference_delays
from logic_analyzer.decoder import decode_i2c_report, decode_spi_report, decode_uart_report
from logic_analyzer.exporter import export_csv, export_vcd
from logic_analyzer.gui.analysis_panel import AnalysisPanel
from logic_analyzer.gui.config_panel import ConfigPanel
from logic_analyzer.gui.connect_panel import ConnectPanel
from logic_analyzer.gui.decode_panel import DecodePanel
from logic_analyzer.gui.export_panel import ExportPanel
from logic_analyzer.gui.monitor_panel import MonitorPanel
from logic_analyzer.gui.waveform_panel import WaveformPanel
from logic_analyzer.serial_handler import SerialHandler

LOGGER = logging.getLogger(__name__)


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("8-Channel FPGA Logic Analyzer (Streaming)")
        self.geometry("1120x760")

        self.serial = SerialHandler()
        self.samples: list[int] = []
        self._capture_lock = threading.Lock()

        # ================= UI =================
        self.connect_panel = ConnectPanel(
            self,
            list_ports=self.serial.list_ports,
            on_connect=self._connect,
            on_disconnect=self.serial.disconnect,
        )

        self.config_panel = ConfigPanel(
            self,
            self._apply_config,
            self._start_capture,
            self._stop_capture,
        )

        self.notebook = ttk.Notebook(self)
        self.waveform_panel = WaveformPanel(self.notebook)
        self.decode_panel = DecodePanel(self.notebook, self._run_decode)
        self.analysis_panel = AnalysisPanel(self.notebook)
        self.monitor_panel = MonitorPanel(self.notebook)
        self.export_panel = ExportPanel(self, self._export_csv, self._export_vcd)

        self.notebook.add(self.waveform_panel, text="Waveform")
        self.notebook.add(self.analysis_panel, text="Analysis")
        self.notebook.add(self.decode_panel, text="Decode")
        self.notebook.add(self.monitor_panel, text="Serial Monitor")

        self.connect_panel.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        self.config_panel.grid(row=1, column=0, sticky="ew", padx=8, pady=6)
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=8, pady=6)
        self.export_panel.grid(row=3, column=0, sticky="ew", padx=8, pady=6)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.serial.add_monitor_callback(self.monitor_panel.append_line)

    # ================= CONNECTION =================

    def _connect(self, port: str) -> bool:
        return self.serial.connect(port)

    # ================= CONFIG =================

    def _apply_config(self) -> None:
        # Optional: keep for compatibility (can be removed later)
        pass

    # ================= START STREAM =================

    def _start_capture(self) -> None:
        if not self.serial.is_connected:
            messagebox.showerror("Not connected", "Connect to serial port first.")
            return

        self.config_panel.set_capture_busy(True)
        threading.Thread(target=self._stream_worker, daemon=True).start()

    # ================= STREAM WORKER =================

    def _stream_worker(self) -> None:
        def on_samples(chunk):
            with self._capture_lock:
                self.samples.extend(chunk)
                self.samples = self.samples[-2000:]

            self.after(0, self._update_stream_view)

        try:
            self.serial.stream_samples(on_samples)
        except Exception as exc:
            LOGGER.exception("Streaming failed")
            self.after(0, self._stream_error, str(exc))

    # ================= UPDATE UI =================

    def _update_stream_view(self) -> None:
        sample_rate = self.config_panel.sample_rate()
        names = self.config_panel.channel_names()

        self.waveform_panel.show_samples(
            self.samples,
            sample_rate,
            names,
            trigger_index=None,
        )

        if len(self.samples) > 10:
            stats = analyze_channels(self.samples, sample_rate, names)
            delays = measure_reference_delays(self.samples, sample_rate, names, reference_channel=0)

            self.analysis_panel.show_analysis(
                stats,
                delays,
                len(self.samples),
                sample_rate,
            )

    # ================= STOP =================

    def _stop_capture(self) -> None:
        self.serial.disconnect()
        self.config_panel.set_capture_busy(False)

    def _stream_error(self, error: str) -> None:
        self.config_panel.set_capture_busy(False)
        messagebox.showerror("Streaming Error", error)

    # ================= DECODE =================

    def _run_decode(self) -> None:
        sample_rate = self.config_panel.sample_rate()
        protocol = self.decode_panel.protocol_var.get()

        events = []
        summary_lines: list[str] = []

        if len(self.samples) > 3:
            if protocol in ("I2C", "All"):
                report = decode_i2c_report(
                    self.samples,
                    sample_rate,
                    scl_ch=self.decode_panel.scl_var.get(),
                    sda_ch=self.decode_panel.sda_var.get(),
                )
                events.extend(report.events)
                summary_lines.extend(report.summary_lines)

            if protocol in ("SPI", "All"):
                report = decode_spi_report(
                    self.samples,
                    sample_rate,
                    sclk_ch=self.decode_panel.sclk_var.get(),
                    mosi_ch=self.decode_panel.mosi_var.get(),
                    miso_ch=self.decode_panel.miso_var.get(),
                    cs_ch=self.decode_panel.cs_var.get(),
                    rising_edge=self.decode_panel.spi_edge_var.get() == "Rising",
                )
                events.extend(report.events)
                summary_lines.extend(report.summary_lines)

            if protocol in ("UART", "All"):
                report = decode_uart_report(
                    self.samples,
                    sample_rate,
                    tx_ch=self.decode_panel.uart_tx_var.get(),
                    baud=self.decode_panel.uart_baud_var.get(),
                )
                events.extend(report.events)
                summary_lines.extend(report.summary_lines)

        events.sort(key=lambda e: e.time_s)
        self.decode_panel.show_events(events)
        self.decode_panel.show_summary(summary_lines or ["Streaming..."])

    # ================= EXPORT =================

    def _export_csv(self, path: str) -> None:
        export_csv(path, self.samples, self.config_panel.sample_rate())

    def _export_vcd(self, path: str) -> None:
        export_vcd(path, self.samples, self.config_panel.sample_rate(), self.config_panel.channel_names())