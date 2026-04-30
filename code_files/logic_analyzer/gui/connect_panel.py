"""Serial connection controls."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from collections.abc import Callable


class ConnectPanel(ttk.LabelFrame):
    """Panel for selecting and opening a serial port."""

    def __init__(
        self,
        master: tk.Widget,
        list_ports: Callable[[], list[str]],
        on_connect: Callable[[str], bool],
        on_disconnect: Callable[[], None],
    ) -> None:
        super().__init__(master, text="Connection")
        self._list_ports = list_ports
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self.connected = False

        self.port_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Disconnected")
        self.port_combo = ttk.Combobox(self, textvariable=self.port_var, width=18, state="readonly")
        self.refresh_button = ttk.Button(self, text="Refresh", command=self.refresh_ports)
        self.connect_button = ttk.Button(self, text="Connect", command=self.toggle_connection)
        self.status_label = ttk.Label(self, textvariable=self.status_var)

        self.port_combo.grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.refresh_button.grid(row=0, column=1, padx=6, pady=6)
        self.connect_button.grid(row=0, column=2, padx=6, pady=6)
        self.status_label.grid(row=0, column=3, padx=6, pady=6)
        self.columnconfigure(0, weight=1)
        self.refresh_ports()

    def refresh_ports(self) -> None:
        """Refresh the available serial port list."""
        ports = self._list_ports()
        self.port_combo["values"] = ports
        if ports and not self.port_var.get():
            self.port_var.set(ports[0])

    def toggle_connection(self) -> None:
        """Connect or disconnect depending on current state."""
        if self.connected:
            self._on_disconnect()
            self.connected = False
            self.connect_button.configure(text="Connect")
            self.status_var.set("Disconnected")
            return

        port = self.port_var.get()
        if not port:
            self.status_var.set("Select a port")
            return
        if self._on_connect(port):
            self.connected = True
            self.connect_button.configure(text="Disconnect")
            self.status_var.set(f"Connected: {port}")
        else:
            self.status_var.set("Open failed")

