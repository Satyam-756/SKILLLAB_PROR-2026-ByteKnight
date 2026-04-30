# 8-Channel FPGA Logic Analyzer

This project implements an 8-bit FPGA logic analyzer for the Real Digital Boolean Board
using Verilog on the FPGA and a Python GUI on the PC.

## Board

- Board: Real Digital Boolean Board
- FPGA: Xilinx Spartan-7 XC7S50-CSGA324-1
- Clock: onboard 100 MHz oscillator on FPGA pin F14
- PC link: onboard USB-UART through the `PROG UART` USB connector
- Logic level: 3.3 V LVCMOS only

Do not connect 5 V DUT signals directly to the FPGA. Use a level shifter and connect the
DUT ground to a Boolean Board GND pin.

## Input Pin Mapping

The design uses 8 inputs named `pmod_in[7:0]`. The provided XDC maps them to a Pmod A
style group with four upper-row and four lower-row signals.

| Channel | Verilog port | FPGA pin |
|---:|---|---|
| 0 | `pmod_in[0]` | T6 |
| 1 | `pmod_in[1]` | T5 |
| 2 | `pmod_in[2]` | R5 |
| 3 | `pmod_in[3]` | T4 |
| 4 | `pmod_in[4]` | R7 |
| 5 | `pmod_in[5]` | R6 |
| 6 | `pmod_in[6]` | P6 |
| 7 | `pmod_in[7]` | P5 |

If your physical Pmod orientation is different, edit only `boolean_board_8ch_logic_analyzer.xdc`.
The Verilog and Python logic do not depend on the physical pin order.

## FPGA Files

Verilog sources are in `rtl/`:

- `top.v`: top-level module
- `clk_manager.v`: sample tick generator
- `input_sampler.v`: simultaneous 8-bit sampler
- `trigger.v`: immediate, rising, falling, and pattern trigger
- `bram_ctrl.v`: 32768 x 8 sample buffer
- `uart.v`: 115200 baud 8N1 UART
- `cmd_parser.v`: ASCII command parser
- `data_tx.v`: BRAM-to-UART hex transmitter
- `led_driver.v`: LED status output

Use `boolean_board_8ch_logic_analyzer.xdc` as the Vivado constraints file.

## Serial Protocol

Commands are ASCII lines:

- `START`
- `STOP`
- `RATE:00` through `RATE:09`
- `DEPTH:00001` through `DEPTH:32768`
- `TRIG:IMM`
- `TRIG:RISE:0` through `TRIG:RISE:7`
- `TRIG:FALL:0` through `TRIG:FALL:7`
- `TRIG:PAT:00` through `TRIG:PAT:FF`

Captured samples are transmitted as two hex characters plus newline, then `DONE`.
Example:

```text
00
1D
3A
DONE
```

## Vivado Setup

1. Create a Vivado RTL project for `xc7s50csga324-1`.
2. Add all files from `rtl/` as design sources.
3. Add `sim/tb_top.v` as a simulation source if needed.
4. Add `boolean_board_8ch_logic_analyzer.xdc` as constraints.
5. Set `top` as the top module.
6. Run synthesis, implementation, generate bitstream, then program the board.

## Python GUI

Install dependencies:

```bash
pip install -r requirements.txt
```

Tkinter is part of many Python installs, but on Linux it is often a system package. If the
GUI fails with `No module named '_tkinter'`, install it with your OS package manager, for
example `sudo apt install python3-tk`.

Run:

```bash
python main.py
```

GUI workflow:

1. Connect the Boolean Board through `PROG UART`.
2. Select the serial port and click Connect.
3. Select sample rate, depth, trigger mode, and channel names.
4. Click Apply, then Start.
5. The FPGA captures samples and streams data back to the GUI.
6. Use the Waveform tab to inspect the signals.
7. Export CSV or VCD for external analysis.

## Notes From The Reference Paper

The included paper describes an 8-bit Spartan-6 logic analyzer with SRAM buffering,
UART communication, selectable sampling, and a Python GUI. This project keeps the same
main idea but targets the Boolean Board Spartan-7, uses Verilog, and supports a deeper
32768-sample buffer.

## Troubleshooting

- Wrong COM port: unplug/replug the board and press Refresh in the GUI.
- No data: confirm `PROG UART` USB is connected and the FPGA is programmed.
- Corrupted waveform: lower the sample rate or confirm DUT signals are clean 3.3 V logic.
- Timeout: reduce depth first, then verify the FPGA responds in the Serial Monitor.

## Arduino Nano Test Waveform

An Arduino Nano test sketch is included at:

```text
arduino_nano_waveform/arduino_nano_waveform.ino
```

It generates two square waves:

| Nano pin | Analyzer channel | Signal |
|---|---:|---|
| D2 | Ch 0 | 1 kHz square wave |
| D3 | Ch 1 | 250 Hz square wave |
| GND | GND | common ground |

Important: a common 5 V Arduino Nano outputs 5 V logic, but the Boolean Board FPGA
inputs are 3.3 V only. Use a level shifter or a 3.3 V Nano-compatible board before
connecting D2/D3 to the FPGA inputs.
