"""Raw serial monitor panel."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class MonitorPanel(ttk.Frame):
    """Display raw lines received from the FPGA."""

    def __init__(self, master: tk.Widget) -> None:
        super().__init__(master)
        self.text = tk.Text(self, height=12, wrap="none")
        self.scroll = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.scroll.set)
        ttk.Button(self, text="Clear", command=self.clear).grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.text.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid(row=1, column=1, sticky="ns")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def append_line(self, line: str) -> None:
        """Append one received line."""
        self.text.after(0, self._append_line, line)

    def clear(self) -> None:
        """Clear the monitor."""
        self.text.delete("1.0", "end")

    def _append_line(self, line: str) -> None:
        self.text.insert("end", f"{line}\n")
        self.text.see("end")

