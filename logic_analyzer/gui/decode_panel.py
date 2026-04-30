"""Protocol decode panel."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from logic_analyzer.decoder import DecodeEvent


class DecodePanel(ttk.Frame):
    """Table of decoded events."""

    def __init__(self, master: tk.Widget) -> None:
        super().__init__(master)
        self.tree = ttk.Treeview(self, columns=("time", "type", "value", "detail"), show="headings")
        for column, title in [("time", "Time s"), ("type", "Type"), ("value", "Value"), ("detail", "Detail")]:
            self.tree.heading(column, text=title)
            self.tree.column(column, width=120)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def show_events(self, events: list[DecodeEvent]) -> None:
        """Replace table contents with decoded events."""
        self.tree.delete(*self.tree.get_children())
        for event in events:
            self.tree.insert("", "end", values=(f"{event.time_s:.9f}", event.kind, event.value, event.detail))

