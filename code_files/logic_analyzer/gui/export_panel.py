"""Export controls."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk
from collections.abc import Callable


class ExportPanel(ttk.Frame):
    """Buttons for CSV and VCD export."""

    def __init__(
        self,
        master: tk.Widget,
        on_csv: Callable[[str], None],
        on_vcd: Callable[[str], None],
    ) -> None:
        super().__init__(master)
        self._on_csv = on_csv
        self._on_vcd = on_vcd
        ttk.Button(self, text="Export CSV", command=self._export_csv).grid(row=0, column=0, padx=6, pady=6)
        ttk.Button(self, text="Export VCD", command=self._export_vcd).grid(row=0, column=1, padx=6, pady=6)

    def _export_csv(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            self._on_csv(path)

    def _export_vcd(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".vcd", filetypes=[("VCD", "*.vcd")])
        if path:
            self._on_vcd(path)

