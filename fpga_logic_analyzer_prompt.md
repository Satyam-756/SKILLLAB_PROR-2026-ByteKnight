# FPGA Logic Analyzer — Complete Project Prompt
## Target Hardware: Digilent Boolean Board (Xilinx Spartan-7 XC7S50CSGA324-1)

---

## Project Overview

Build a 16-channel digital logic analyzer using the Digilent Boolean Board (Xilinx Spartan-7
XC7S50CSGA324-1 FPGA). The system has two parts:

1. **FPGA firmware** written in VHDL, synthesized using Vivado 2020.x or later
2. **Python 3.10+ desktop GUI** running on a PC, communicating with the FPGA over USB-UART

The user connects up to 16 digital signal wires from a device under test (DUT) to the PMOD
headers on the Boolean board (JA, JB, JC, JD — 4 pins each = 16 total channels). Each pin
reads a single logic level: 0 (GND/LOW) or 1 (3.3V/HIGH). The FPGA samples all 16 channels
simultaneously, stores the data in on-chip BRAM, then streams it to the PC over UART when
capture is complete. The Python GUI controls the device and displays the captured waveforms.

---

## Hardware Constraints & Facts

- **FPGA:** Xilinx Spartan-7 XC7S50CSGA324-1
- **Logic cells:** 52,160 | **Flip-Flops:** 65,200 | **Block RAM:** 2,700 Kb
- **Onboard clock:** 100 MHz
- **I/O voltage:** 3.3V logic on PMOD pins (warn user if DUT uses 5V — level shifter needed)
- **USB-UART bridge:** onboard (no external RS232 chip needed)
- **PMOD connectors:** JA, JB, JC, JD — 4 usable I/O pins each = 16 channels total
- **Channel mapping:**
  - Ch 0–3  → PMOD JA pins [0..3]
  - Ch 4–7  → PMOD JB pins [0..3]
  - Ch 8–11 → PMOD JC pins [0..3]
  - Ch 12–15 → PMOD JD pins [0..3]
- **GND:** DUT GND must be connected to any GND pin on the PMOD header

---

## Part 1 — FPGA Firmware (VHDL)

### 1.1 Top-Level Architecture

Create a top-level VHDL file `top.vhd` that instantiates and connects all components below.
Use the onboard 100 MHz clock as the master clock input. Map all PMOD pins in the XDC
constraints file.

### 1.2 Component List

#### A. Clock Manager (`clk_manager.vhd`)
- Use Xilinx MMCM (Mixed-Mode Clock Manager) primitive to generate selectable sample clocks
- Support the following sample rates selectable at runtime via a 5-bit control signal:

| Rate code | Sample rate     |
|-----------|----------------|
| 00000     | 1 Hz           |
| 00001     | 10 Hz          |
| 00010     | 100 Hz         |
| 00011     | 1 kHz          |
| 00100     | 10 kHz         |
| 00101     | 100 kHz        |
| 00110     | 1 MHz          |
| 00111     | 10 MHz         |
| 01000     | 50 MHz         |
| 01001     | 100 MHz        |

- Output: `sample_clk` — the selected sampling clock fed to the input sampler

#### B. Input Sampler (`input_sampler.vhd`)
- 16-bit wide input port `data_in[15:0]` connected directly to the 16 PMOD pins
- On every rising edge of `sample_clk`, latch all 16 bits simultaneously into a register
- Output: `sample_data[15:0]` — the captured 16-bit snapshot

#### C. Trigger Unit (`trigger.vhd`)
- Inputs: `sample_data[15:0]`, trigger configuration registers
- Support three trigger modes selected by a 2-bit `trig_mode` signal:
  - `00` = immediate (start capturing instantly on START command)
  - `01` = rising edge on a selected channel (`trig_channel[3:0]`)
  - `10` = falling edge on a selected channel
  - `11` = 16-bit pattern match — capture starts when `sample_data == trig_pattern[15:0]`
- Output: `triggered` — goes HIGH when trigger condition is met, stays HIGH until reset

#### D. BRAM Controller (`bram_ctrl.vhd`)
- Use Xilinx Block RAM (RAMB36E1 primitive or inferred BRAM)
- Memory configuration: 32,768 locations × 16 bits wide (uses ~512 Kb of the 2,700 Kb available)
- 15-bit write address counter, increments on each `sample_clk` when `triggered` is HIGH and
  `capture_done` is LOW
- Separate 15-bit read address counter, incremented by the UART transmitter during readout
- Signals: `wr_en`, `rd_en`, `wr_addr[14:0]`, `rd_addr[14:0]`, `data_in[15:0]`, `data_out[15:0]`
- Assert `capture_done` when write counter reaches the user-selected sample count

#### E. UART Controller (`uart.vhd`)
- Full-duplex UART, fixed at **115200 baud**, 8N1 format
- **RX side:** receives ASCII command bytes from PC, outputs `rx_byte[7:0]` with `rx_valid` strobe
- **TX side:** accepts `tx_byte[7:0]` with `tx_start` strobe, serialises and transmits
- Use the 100 MHz master clock with a baud rate divider (divisor = 868 for 115200 baud)

#### F. Command Parser (`cmd_parser.vhd`)
- Receives `rx_byte` stream from UART RX
- Parses the following ASCII command protocol:

| Command string     | Action                                              |
|--------------------|-----------------------------------------------------|
| `START\n`          | Begin capture (arm trigger, start sampling)         |
| `STOP\n`           | Abort capture, reset state machine                  |
| `RATE:xx\n`        | Set sample rate (xx = 2-digit rate code 00–09)      |
| `DEPTH:xxxxx\n`    | Set sample depth (xxxxx = decimal, max 32768)       |
| `TRIG:IMM\n`       | Set trigger mode to immediate                       |
| `TRIG:RISE:x\n`    | Rising edge trigger on channel x (0–15)             |
| `TRIG:FALL:x\n`    | Falling edge trigger on channel x (0–15)            |
| `TRIG:PAT:xxxx\n`  | Pattern trigger (xxxx = 4 hex digits = 16-bit mask) |

- Outputs decoded control registers to trigger unit, clock manager, and BRAM controller

#### G. Data Transmitter (`data_tx.vhd`)
- After `capture_done` goes HIGH, reads BRAM sequentially from address 0 to (depth-1)
- For each 16-bit sample, transmit 4 ASCII hex characters + newline (e.g. `1A3F\n`)
- After all samples sent, transmit `DONE\n` to signal end of data stream
- Uses UART TX to send bytes

#### H. Status LED Driver (`led_driver.vhd`)
- Drive the onboard LEDs of the Boolean board to show system state:
  - LED 0 ON = UART connected / receiving commands
  - LED 1 ON = waiting for trigger
  - LED 2 ON = capturing
  - LED 3 ON = transmitting data to PC
  - LED 4 blink = idle / ready

### 1.3 State Machine

Implement a top-level FSM with these states:

```
IDLE → ARMED → TRIGGERED → CAPTURING → TRANSMITTING → IDLE
```

- **IDLE:** waiting for `START` command
- **ARMED:** trigger unit active, waiting for trigger condition
- **TRIGGERED:** trigger fired, BRAM write counter starts
- **CAPTURING:** filling BRAM at sample_clk rate
- **TRANSMITTING:** BRAM read + UART TX of all samples
- Returns to IDLE after `DONE\n` sent or `STOP` received at any time

### 1.4 XDC Constraints File (`boolean_board.xdc`)

Provide a complete XDC file for the Boolean board including:
- 100 MHz onboard clock pin
- UART TX and RX pins (via onboard USB-UART bridge)
- All 16 PMOD pins (JA[0..3], JB[0..3], JC[0..3], JD[0..3]) as inputs
- Onboard LEDs (at least 5)
- Set all PMOD inputs to LVCMOS33 I/O standard
- Add timing constraints: create_clock for the 100 MHz master clock

---

## Part 2 — Python GUI (`logic_analyzer/`)

### 2.1 Project Structure

```
logic_analyzer/
├── main.py              # Entry point, launches GUI
├── serial_handler.py    # Serial port open/close/send/receive
├── command.py           # Command builder functions
├── decoder.py           # I2C, SPI, UART protocol decoders
├── plotter.py           # Waveform rendering (matplotlib)
├── exporter.py          # CSV and VCD export
└── gui/
    ├── main_window.py   # Root window, tab manager
    ├── connect_panel.py # COM port selector + Connect button
    ├── config_panel.py  # Sample rate, depth, trigger config
    ├── waveform_panel.py# 16-channel waveform display
    ├── decode_panel.py  # Protocol decode results
    ├── monitor_panel.py # Raw serial monitor
    └── export_panel.py  # Export buttons
```

### 2.2 Serial Handler (`serial_handler.py`)

- Use `pyserial` library
- Functions:
  - `connect(port, baud=115200)` → opens port, returns True/False
  - `disconnect()` → closes port cleanly
  - `send_command(cmd_string)` → encodes and sends ASCII command + `\n`
  - `read_samples(depth, timeout=10)` → reads hex lines until `DONE\n`, returns list of 16-bit ints
  - `list_ports()` → returns list of available COM ports
- Run receiver in a background thread; emit data via callbacks or a queue

### 2.3 Command Builder (`command.py`)

Provide clean helper functions that return the correct command strings:

```python
def cmd_start() -> str
def cmd_stop() -> str
def cmd_set_rate(rate_code: int) -> str        # rate_code 0–9
def cmd_set_depth(depth: int) -> str           # 1–32768
def cmd_trig_immediate() -> str
def cmd_trig_rising(channel: int) -> str       # channel 0–15
def cmd_trig_falling(channel: int) -> str
def cmd_trig_pattern(pattern: int) -> str      # 16-bit int
```

### 2.4 Connect Panel (`gui/connect_panel.py`)

- Dropdown: list of available COM ports (auto-refresh button)
- Connect / Disconnect button (toggles)
- Status indicator: green dot = connected, red dot = disconnected
- On connection failure: show clear error message with suggested fix

### 2.5 Configuration Panel (`gui/config_panel.py`)

- **Sample rate selector:** dropdown with all 10 rate options, shows human-readable label
  (e.g. "1 MHz") and sends `RATE:xx` on change
- **Sample depth:** spinbox 1–32768, sends `DEPTH:xxxxx` on change
- **Trigger mode:** radio buttons for Immediate / Rising Edge / Falling Edge / Pattern
  - Rising/Falling: show channel selector dropdown (Ch 0–15) with signal name labels
    (user can rename channels)
  - Pattern: show a 16-bit hex input field
- **Channel labels:** allow user to type a name for each of the 16 channels
  (e.g. "SCL", "SDA", "MOSI") — these names appear in the waveform view
- **Start / Stop buttons:** large, clearly labelled

### 2.6 Waveform Panel (`gui/waveform_panel.py`)

- Use `matplotlib` embedded in Tkinter (`FigureCanvasTkAgg`)
- Display 16 stacked waveform traces, one per channel
- Each trace shows logic level over time (0 = LOW, 1 = HIGH, drawn as a step plot)
- X-axis: time in appropriate unit (ns / µs / ms / s) based on sample rate
- Y-axis per trace: just 0 and 1 ticks, with channel name label on the left
- Color-code channels: use a consistent color per channel index
- Show a vertical cursor line on mouse hover, display time and all 16 logic values in a tooltip
- Zoom: support scroll-to-zoom on X axis, click-drag to pan
- Highlight trigger point with a vertical dashed line labeled "Trigger"

### 2.7 Protocol Decoder (`decoder.py`)

Implement software decoders for three protocols. Each decoder takes:
- `samples: list[int]` — list of 16-bit captured samples
- `sample_rate: float` — samples per second
- Channel assignments (which channel index carries which signal)

#### I2C Decoder
- Inputs: `scl_ch`, `sda_ch`
- Detects START condition (SDA falls while SCL high)
- Reads address byte (7-bit + R/W bit)
- Reads data bytes with ACK/NAK
- Output: list of decoded transactions with timestamp, address, data bytes, R/W flag

#### SPI Decoder
- Inputs: `sclk_ch`, `mosi_ch`, `miso_ch`, `cs_ch`
- Detects CS active low
- Samples MOSI and MISO on configured clock edge
- Output: list of decoded bytes with timestamps for MOSI and MISO

#### UART Decoder
- Inputs: `tx_ch` (and optionally `rx_ch`), `baud_rate`
- Detects start bit (falling edge)
- Samples 8 data bits, checks stop bit
- Output: list of decoded bytes with timestamps and parity status

Display decode results in the decode panel as a table: timestamp | type | value | interpretation.

### 2.8 Exporter (`exporter.py`)

#### CSV Export
```
time_us, ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12, ch13, ch14, ch15
0.00, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
...
```

#### VCD Export (Value Change Dump — compatible with GTKWave)
```
$timescale 1us $end
$var wire 1 ! ch0_SCL $end
...
#0
0!
...
```
- Write a proper VCD header with timescale derived from sample rate
- Write only value-change events (not every sample) to keep file size small

### 2.9 Serial Monitor (`gui/monitor_panel.py`)

- Raw scrolling text view of all bytes received from FPGA
- Toggle to show as ASCII or hex
- Clear button
- Useful for debugging communication issues

### 2.10 Error Handling & Edge Cases

Handle and display clear user-facing messages for:
- COM port not found or already in use
- FPGA not responding (timeout)
- Capture aborted mid-stream
- Sample depth too large for selected rate + BRAM size
- DUT voltage warning: display a banner if user selects a rate above 10 MHz reminding
  them to verify 3.3V logic compatibility
- Partial data received: show how many samples were captured vs expected

---

## Part 3 — Additional Requirements

### Code Quality
- All VHDL files: include a header comment with entity name, description, ports, and author
- All Python files: use type hints throughout, docstrings on all public functions
- Python: use `logging` module (not print statements) for debug output
- Python: follow PEP 8

### Dependencies (`requirements.txt`)
```
pyserial>=3.5
matplotlib>=3.7
numpy>=1.24
```

### VHDL Simulation
- Provide a testbench `tb_top.vhd` that:
  - Simulates the UART command `START\n` being sent
  - Drives 16 input pins with a simple alternating pattern
  - Verifies that BRAM receives correct data
  - Verifies that UART TX outputs the correct hex-encoded samples

### README (`README.md`)
Provide a README with:
1. Hardware setup: wiring diagram description (DUT signal → PMOD pin mapping table)
2. Voltage warning for 5V devices
3. Vivado project setup steps (create project, add sources, add XDC, synthesize, generate bitstream)
4. Python setup: `pip install -r requirements.txt`, how to run `python main.py`
5. How to use the GUI step by step
6. Troubleshooting: common issues (wrong COM port, no data, corrupted waveform)

---

## Deliverables Summary

| File | Description |
|------|-------------|
| `top.vhd` | Top-level FPGA design |
| `clk_manager.vhd` | MMCM-based clock selector |
| `input_sampler.vhd` | 16-ch simultaneous sampler |
| `trigger.vhd` | Trigger unit (4 modes) |
| `bram_ctrl.vhd` | BRAM read/write controller |
| `uart.vhd` | Full-duplex UART at 115200 |
| `cmd_parser.vhd` | ASCII command parser |
| `data_tx.vhd` | BRAM → UART transmitter |
| `led_driver.vhd` | Onboard LED state indicator |
| `tb_top.vhd` | Simulation testbench |
| `boolean_board.xdc` | Full pin constraints |
| `main.py` | Python app entry point |
| `serial_handler.py` | Serial comms + threading |
| `command.py` | Command string builder |
| `decoder.py` | I2C / SPI / UART decoders |
| `plotter.py` | Matplotlib waveform renderer |
| `exporter.py` | CSV + VCD file export |
| `gui/` | All GUI panel files |
| `requirements.txt` | Python dependencies |
| `README.md` | Full setup + usage guide |
