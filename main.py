"""Launch the 8-channel FPGA logic analyzer GUI."""

from __future__ import annotations

import logging

from logic_analyzer.gui.main_window import MainWindow


def main() -> None:
    """Start the desktop application."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
