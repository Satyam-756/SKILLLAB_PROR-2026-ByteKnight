"""Main Tkinter window for the FPGA logic analyzer."""

from __future__ import annotations

import logging
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from logic_analyzer import command
from logic_analyzer.decoder import decode_i2c, decode_spi, decode_uart
from logic_analyzer.exporter import export_csv, export_vcd
from logic_analyzer.gui.config_panel import ConfigPanel
from logic_analyzer.gui.connect_panel import ConnectPanel
from logic_analyzer.gui.decode_panel import DecodePanel
from logic_analyzer.gui.export_panel import ExportPanel
from logic_analyzer.gui.monitor_panel import MonitorPanel
from logic_analyzer.gui.waveform_panel import WaveformPanel
from logic_analyzer.serial_handler import SerialHandler

LOGGER = logging.getLogger(__name__)


class MainWindow(tk.Tk):
    """Root application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("8-Channel FPGA Logic Analyzer")
        self.geometry("1120x760")
        self.serial = SerialHandler()
        self.samples: list[int] = []

        self.connect_panel = ConnectPanel(
            self,
            list_ports=self.serial.list_ports,
            on_connect=self._connect,
            on_disconnect=self.serial.disconnect,
        )
        self.config_panel = ConfigPanel(self, self._apply_config, self._start_capture, self._stop_capture)
        self.notebook = ttk.Notebook(self)
        self.waveform_panel = WaveformPanel(self.notebook)
        self.decode_panel = DecodePanel(self.notebook)
        self.monitor_panel = MonitorPanel(self.notebook)
        self.export_panel = ExportPanel(self, self._export_csv, self._export_vcd)

        self.notebook.add(self.waveform_panel, text="Waveform")
        self.notebook.add(self.decode_panel, text="Decode")
        self.notebook.add(self.monitor_panel, text="Serial Monitor")

        self.connect_panel.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        self.config_panel.grid(row=1, column=0, sticky="ew", padx=8, pady=6)
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=8, pady=6)
        self.export_panel.grid(row=3, column=0, sticky="ew", padx=8, pady=6)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.serial.add_monitor_callback(self.monitor_panel.append_line)

    def _connect(self, port: str) -> bool:
        return self.serial.connect(port)

    def _apply_config(self) -> None:
        if not self.serial.is_connected:
            messagebox.showerror("Not connected", "Connect to the Boolean Board serial port first.")
            return
        try:
            self.serial.send_command(command.cmd_set_rate(self.config_panel.rate_code()))
            self.serial.send_command(command.cmd_set_depth(self.config_panel.depth_var.get()))
            trigger = self.config_panel.trigger_var.get()
            channel = self.config_panel.trigger_channel_var.get()
            if trigger == "Immediate":
                self.serial.send_command(command.cmd_trig_immediate())
            elif trigger == "Rising":
                self.serial.send_command(command.cmd_trig_rising(channel))
            elif trigger == "Falling":
                self.serial.send_command(command.cmd_trig_falling(channel))
            else:
                self.serial.send_command(command.cmd_trig_pattern(int(self.config_panel.pattern_var.get(), 16)))
        except Exception as exc:
            LOGGER.exception("Failed to apply configuration")
            messagebox.showerror("Configuration error", str(exc))

    def _start_capture(self) -> None:
        if not self.serial.is_connected:
            messagebox.showerror("Not connected", "Connect to the Boolean Board serial port first.")
            return
        self._apply_config()
        threading.Thread(target=self._capture_worker, daemon=True).start()

    def _capture_worker(self) -> None:
        try:
            depth = self.config_panel.depth_var.get()
            self.serial.send_command(command.cmd_start())
            samples = self.serial.read_samples(depth, timeout=max(5.0, depth / 2000.0 + 5.0))
        except Exception as exc:
            LOGGER.exception("Capture failed")
            self.after(0, messagebox.showerror, "Capture failed", str(exc))
            return
        self.samples = samples
        self.after(0, self._show_capture)

    def _show_capture(self) -> None:
        sample_rate = self.config_panel.sample_rate()
        names = self.config_panel.channel_names()
        self.waveform_panel.show_samples(self.samples, sample_rate, names)
        events = []
        if len(self.samples) > 3:
            events.extend(decode_i2c(self.samples, sample_rate, scl_ch=0, sda_ch=1))
            events.extend(decode_spi(self.samples, sample_rate, sclk_ch=2, mosi_ch=3, miso_ch=4, cs_ch=5))
            events.extend(decode_uart(self.samples, sample_rate, tx_ch=6, baud=115200))
        self.decode_panel.show_events(events)
        self.notebook.select(self.waveform_panel)

    def _stop_capture(self) -> None:
        if self.serial.is_connected:
            self.serial.send_command(command.cmd_stop())

    def _export_csv(self, path: str) -> None:
        export_csv(path, self.samples, self.config_panel.sample_rate())

    def _export_vcd(self, path: str) -> None:
        export_vcd(path, self.samples, self.config_panel.sample_rate(), self.config_panel.channel_names())
