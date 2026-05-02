# FPGA Logic Analyzer — Skill Lab Practical Hackathon

> **Team Name:** ByteKnight (`SKILLLAB_PROR-2026-ByteKnight`)  
> **Project Title:** FPGA-Logic Analyser  
> **Hardware:** Real Digital Boolean Board (Xilinx Spartan-7 XC7S50-CSGA324-1)

---

## 📖 Project Overview

This project is a high-performance Embedded Logic Analyzer designed to bridge the gap between low-cost microcontrollers and professional-grade debugging equipment. It transforms a Spartan-7 FPGA into a dedicated high-speed digital acquisition engine that monitors digital signals (e.g., from an Arduino). By capturing and buffering these signals at hardware speeds, the system identifies specific trigger events and then transmits the resulting waveform data back to a PC via a custom-built USB-UART serial interface. 

A custom Python desktop application allows developers to "see" exactly what their hardware logic is doing in real-time, providing deep insights like timing measurements, glitch detection, and automatic protocol decoding (I2C, SPI, UART).

---

## ✨ Key Features

- **8-Channel Digital Capture:** Samples signals precisely using the PMOD-A headers on the Boolean Board mapped from `B13` onwards.
- **Pre-Trigger Hardware Buffer:** A dedicated BRAM circular buffer on the FPGA captures and retains history *before* the trigger condition occurred.
- **Visual Trigger Markers:** Accurate timing tracking via `TRIGPOS` messages, plotted directly on the main waveform timeline.
- **Extensive Protocol Decoding:** Advanced data parsers to decode embedded communications (I2C, SPI, and UART) into readable, summarized trace reports. 
- **Full Custom GUI:** A cross-platform Python interface to configure captures (sample rate, depth, triggers) and analyze waveforms with precision cursors and multi-stage rendering.
- **Export Capabilities:** Instantly save out captured signal traces into standard representations like CSV or VCD files for further analysis.

---

## 📂 System Architecture & Repository Structure

### 1. Hardware (FPGA / Verilog)
The `rtl/` directory contains the Verilog synthesis files to run on the Boolean board at an onboard clock of 100 MHz.
* `boolean_board_8ch_logic_analyzer.xdc` — Physical FPGA pin constraints.
* `top.v` — The top-level design integrating all sub-modules.
* `bram_ctrl.v` — 32768 x 8 circular sample buffer with pre-trigger capture support.
* `uart.v` & `data_tx.v` — Handles RS-232 UART transmission connecting via the USB/PROG port.
* `cmd_parser.v` — Parses the serial commands from python (e.g., `START`, `TRIG`, `PRETRIG`).
* `trigger.v` & `input_sampler.v` — Evaluates logical constraints (rising edge, falling edge, pattern match).

### 2. Software (Python GUI)
The `logic_analyzer/` package contains the desktop Python application to control the FPGA.
* `main.py` — The entry point to start the Tkinter/desktop GUI.
* `logic_analyzer/serial_handler.py` — Opens the COM port, sets up the connection, and captures the streaming bytes (`TRIGPOS`, Hex payload).
* `logic_analyzer/plotter.py` — Uses Matplotlib to plot the multi-channel logic levels.
* `logic_analyzer/decoder.py` — Analyzes logic levels to reconstruct embedded protocols in detailed summaries.
* `logic_analyzer/gui/` — UI modules for Analysis, Configuration, Connection, Decoding, Export, Monitoring, and the Waveform render window.

---

## 🚀 Setup Instructions

### 1. Hardware Configuration (Vivado)
Make sure you have Xilinx Vivado installed. You can compile the Verilog representation and test syntax dynamically via the provided TCL script:
```bash
# In Vivado TCL console or Terminal:
vivado -mode batch -source check_verilog.tcl
```
Upload the compiled bitstream to your Boolean Board.

### 2. Software Configuration (Python)
Ensure Python 3.10+ is installed. In your terminal, initialize the project and load the dependencies:
```bash
# Activate your virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate

# Install the Python dependencies (PySerial, Matplotlib, NumPy)
pip install -r requirements.txt

# Run the Application
python main.py
```

---

## 🔄 User Flow (How to Use)

1. **Hardware Connection**: Connect the Device Under Test (DUT) digital pins to the **Pmod A** port on the Boolean Board. Make sure to share a common Ground (GND). 
2. **Launch the Tool**: Run `python main.py` to open the GUI.
3. **Serial Connect**: In the **Connection Panel**, select the appropriate COM port corresponding to the Boolean Board UART and connect.
4. **Configure Capture Variables**: Use the **Configuration Panel** to define:
   - Sample Rate / Clock Speed
   - Capture Depth (Total number of samples)
   - Pre-trigger Depth (How many samples to gather *before* the trigger hits)
   - Trigger Mode (Immediate, Rising Edge, Falling Edge, or customized Pattern Mask)
5. **Start Capture**: Hit the "Start" button in the GUI. The FPGA hardware will begin executing a background circular buffering until the specified trigger resolves.
6. **Data Analysis**: Once the trigger fires, the FPGA transmits the `TRIGPOS` coordinate followed by the data stream. The UI consumes this data and displays the logic analyzer waveform. Use the **Decode Panel** to view I2C/SPI/UART trace summaries!

---

## 📟 Control Commands (Internals)

Below are the internal UART commands used between the Python interface and the FPGA cmd_parser module for logic control:
- `START\n`: Begin capture (arm trigger, start sampling).
- `STOP\n`: Force abort of a running capture.
- `TRIG:IMM\n`: Set trigger mode to immediate.
- `TRIG:RISE:x\n`: Rising edge trigger on channel `x` (0–15).
- `TRIG:FALL:x\n`: Falling edge trigger on channel `x` (0–15).
- `TRIG:PAT:xxxx\n`: Pattern trigger (`xxxx` = 4 hex digits = 16-bit mask).
- `PRETRIG:xxxxx\n`: Instructs the FPGA to collect `xxxxx` samples before setting off the trigger condition.
