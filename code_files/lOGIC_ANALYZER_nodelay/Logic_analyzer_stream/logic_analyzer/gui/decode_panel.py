"""Protocol decode panel."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from logic_analyzer.decoder import DecodeEvent


class DecodePanel(ttk.Frame):
    """Table of decoded events."""

    def __init__(self, master: tk.Widget, on_decode: Callable[[], None] | None = None) -> None:
        super().__init__(master)
        self._on_decode = on_decode
        self.protocol_var = tk.StringVar(value="I2C")
        self.scl_var = tk.IntVar(value=0)
        self.sda_var = tk.IntVar(value=1)
        self.sclk_var = tk.IntVar(value=2)
        self.mosi_var = tk.IntVar(value=3)
        self.miso_var = tk.IntVar(value=4)
        self.cs_var = tk.IntVar(value=5)
        self.spi_edge_var = tk.StringVar(value="Rising")
        self.uart_tx_var = tk.IntVar(value=6)
        self.uart_baud_var = tk.IntVar(value=115200)

        controls = ttk.Frame(self)
        controls.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        ttk.Label(controls, text="Protocol").grid(row=0, column=0, padx=4, sticky="w")
        ttk.Combobox(
            controls,
            textvariable=self.protocol_var,
            values=["I2C", "SPI", "UART", "All"],
            state="readonly",
            width=8,
        ).grid(row=0, column=1, padx=4)
        ttk.Button(controls, text="Decode", command=self._decode_requested).grid(row=0, column=2, padx=4)

        self.settings = ttk.Notebook(self)
        self.settings.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 6))
        self._build_i2c_controls()
        self._build_spi_controls()
        self._build_uart_controls()

        self.tree = ttk.Treeview(self, columns=("time", "type", "value", "detail"), show="headings")
        for column, title in [("time", "Time s"), ("type", "Type"), ("value", "Value"), ("detail", "Detail")]:
            self.tree.heading(column, text=title)
            self.tree.column(column, width=120)
        self.tree.column("detail", width=260)
        self.tree.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 6))

        ttk.Label(self, text="Summary").grid(row=3, column=0, sticky="w", padx=6)
        self.summary = tk.Text(self, height=7, wrap="word")
        self.summary.grid(row=4, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.summary.configure(state="disabled")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=2)
        self.rowconfigure(4, weight=1)

    def _channel_spinbox(self, master: tk.Widget, variable: tk.IntVar, column: int) -> None:
        ttk.Spinbox(master, from_=0, to=7, textvariable=variable, width=4).grid(row=0, column=column, padx=4)

    def _build_i2c_controls(self) -> None:
        frame = ttk.Frame(self.settings)
        ttk.Label(frame, text="SCL").grid(row=0, column=0, padx=4)
        self._channel_spinbox(frame, self.scl_var, 1)
        ttk.Label(frame, text="SDA").grid(row=0, column=2, padx=4)
        self._channel_spinbox(frame, self.sda_var, 3)
        self.settings.add(frame, text="I2C")

    def _build_spi_controls(self) -> None:
        frame = ttk.Frame(self.settings)
        for column, (label, variable) in enumerate(
            [("SCLK", self.sclk_var), ("MOSI", self.mosi_var), ("MISO", self.miso_var), ("CS", self.cs_var)]
        ):
            ttk.Label(frame, text=label).grid(row=0, column=column * 2, padx=4)
            self._channel_spinbox(frame, variable, column * 2 + 1)
        ttk.Label(frame, text="Edge").grid(row=0, column=8, padx=4)
        ttk.Combobox(
            frame,
            textvariable=self.spi_edge_var,
            values=["Rising", "Falling"],
            state="readonly",
            width=8,
        ).grid(row=0, column=9, padx=4)
        self.settings.add(frame, text="SPI")

    def _build_uart_controls(self) -> None:
        frame = ttk.Frame(self.settings)
        ttk.Label(frame, text="TX").grid(row=0, column=0, padx=4)
        self._channel_spinbox(frame, self.uart_tx_var, 1)
        ttk.Label(frame, text="Baud").grid(row=0, column=2, padx=4)
        ttk.Entry(frame, textvariable=self.uart_baud_var, width=9).grid(row=0, column=3, padx=4)
        self.settings.add(frame, text="UART")

    def _decode_requested(self) -> None:
        if self._on_decode is not None:
            self._on_decode()

    def show_events(self, events: list[DecodeEvent]) -> None:
        """Replace table contents with decoded events."""
        self.tree.delete(*self.tree.get_children())
        for event in events:
            self.tree.insert("", "end", values=(f"{event.time_s:.9f}", event.kind, event.value, event.detail))

    def show_summary(self, lines: list[str]) -> None:
        """Replace the protocol summary text."""
        self.summary.configure(state="normal")
        self.summary.delete("1.0", "end")
        if lines:
            self.summary.insert("1.0", "\n".join(lines))
        self.summary.configure(state="disabled")
