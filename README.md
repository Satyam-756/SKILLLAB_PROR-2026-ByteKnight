# FPGA Logic Analyzer With Python GUI

This project is an **8-bit FPGA logic analyzer** for the **Real Digital Boolean Board**.
It is based on the idea from the included research paper, but changed for our hardware
and project requirements:

- Research paper board: Xilinx Spartan-6 XC6SLX9
- Our board: Real Digital Boolean Board with Xilinx Spartan-7 XC7S50-CSGA324-1
- Research paper language: VHDL
- Our implementation: Verilog `.v`
- Research paper analyzer width: 8-bit
- Our implementation: 8-bit Pmod logic analyzer
- PC software: Python GUI showing captured waveforms

The FPGA captures digital input signals, stores them in block RAM, and sends the samples
to the PC over the board USB-UART. The Python GUI receives the data and displays the
logic waveforms.

## Hardware Used

- Real Digital Boolean Board
- Xilinx Spartan-7 XC7S50-CSGA324-1 FPGA
- 100 MHz onboard clock
- USB cable connected to the board `PROG UART` port
- Pmod/expansion input pins for the 8 logic analyzer channels
- Optional Arduino Nano waveform test source

The Boolean Board FPGA inputs are **3.3 V only**. Do not connect 5 V signals directly.
If using a normal 5 V Arduino Nano, use a level shifter or voltage divider.

## PC Connection

Connect the Boolean Board to the PC using the normal micro-USB cable:

```text
PC USB port -> Boolean Board PROG UART port
```

That same cable is used for:

- Vivado FPGA programming
- USB-UART serial communication with the Python GUI

No external USB-to-UART module is needed.

To find the serial port:

```bash
python3 -m serial.tools.list_ports -v
```

On Linux it may appear as `/dev/ttyUSB0`. On Windows it may appear as `COM3`, `COM4`,
or similar. The Boolean Board uses an FTDI USB controller, so look for `FTDI` in the
detailed port list.

## 8-Bit Analyzer Input Mapping

The Verilog top module uses:

```verilog
input wire [7:0] pmod_in
```

The supplied constraint file maps this to one Pmod-style group with 4 upper-row and
4 lower-row signals.

| Analyzer channel | Verilog signal | FPGA pin in XDC |
|---:|---|---|
| Ch0 | `pmod_in[0]` | T6 |
| Ch1 | `pmod_in[1]` | T5 |
| Ch2 | `pmod_in[2]` | R5 |
| Ch3 | `pmod_in[3]` | T4 |
| Ch4 | `pmod_in[4]` | R7 |
| Ch5 | `pmod_in[5]` | R6 |
| Ch6 | `pmod_in[6]` | P6 |
| Ch7 | `pmod_in[7]` | P5 |

If the physical Pmod orientation is different on your setup, change only:

```text
boolean_board_8ch_logic_analyzer.xdc
```

The Verilog and Python logic do not need to change.

## FPGA Design

Verilog source files are in `rtl/`.

| File | Purpose |
|---|---|
| `top.v` | Top-level Boolean Board design |
| `clk_manager.v` | Generates sample ticks from 100 MHz clock |
| `input_sampler.v` | Samples all 8 input pins together |
| `trigger.v` | Immediate, rising edge, falling edge, and pattern trigger |
| `bram_ctrl.v` | 32768 x 8 sample memory |
| `uart.v` | 115200 baud USB-UART interface |
| `cmd_parser.v` | Parses ASCII commands from PC |
| `data_tx.v` | Sends samples as hex text to PC |
| `led_driver.v` | Shows status on onboard LEDs |

Constraint file:

```text
boolean_board_8ch_logic_analyzer.xdc
```

Simulation file:

```text
sim/tb_top.v
```

## UART Protocol

The Python GUI sends ASCII commands to the FPGA:

| Command | Meaning |
|---|---|
| `START` | Start capture |
| `STOP` | Stop capture |
| `RATE:00` to `RATE:09` | Select sample rate |
| `DEPTH:00001` to `DEPTH:32768` | Select capture depth |
| `TRIG:IMM` | Immediate trigger |
| `TRIG:RISE:0` to `TRIG:RISE:7` | Rising edge trigger |
| `TRIG:FALL:0` to `TRIG:FALL:7` | Falling edge trigger |
| `TRIG:PAT:00` to `TRIG:PAT:FF` | 8-bit pattern trigger |

The FPGA sends each captured sample as two hex characters:

```text
00
1D
A5
FF
DONE
```

Each line is one 8-bit sample. `DONE` means capture transfer is complete.

## Vivado Build Steps

1. Open Vivado.
2. Create a new RTL project.
3. Select FPGA part `xc7s50csga324-1`.
4. Add all Verilog files from `rtl/`.
5. Add `boolean_board_8ch_logic_analyzer.xdc`.
6. Set `top` as the top module.
7. Run synthesis.
8. Run implementation.
9. Generate bitstream.
10. Program the Boolean Board through the `PROG UART` USB cable.

Quick synthesis check from terminal:

```bash
vivado -mode batch -source check_verilog.tcl
```

This project was checked in Vivado and synthesized with 0 errors.

## Python GUI

Install Python dependencies:

```bash
pip install -r requirements.txt
```

If Tkinter is missing on Linux:

```bash
sudo apt install python3-tk
```

Run the GUI:

```bash
python main.py
```

GUI flow:

1. Connect the Boolean Board USB cable.
2. Click Refresh.
3. Select the Boolean Board serial port.
4. Click Connect.
5. Select sample rate, sample depth, and trigger.
6. Click Apply.
7. Click Start.
8. View the 8 digital waveforms.
9. Export CSV or VCD if needed.

## Arduino Nano Test Waveform

A test sketch is included:

```text
arduino_nano_waveform/arduino_nano_waveform.ino
```

It generates two waveforms so you can test the analyzer with only two pins:

| Arduino Nano pin | Connect to analyzer | Signal |
|---|---:|---|
| D2 | Ch0 | 1 kHz square wave |
| D3 | Ch1 | 250 Hz square wave |
| GND | Board GND | common ground |

Connection:

```text
Arduino D2  -> Boolean Board Pmod Ch0
Arduino D3  -> Boolean Board Pmod Ch1
Arduino GND -> Boolean Board Pmod GND
```

Again, use level shifting if the Arduino Nano outputs 5 V.

## Project Structure

```text
.
├── arduino_nano_waveform/
├── logic_analyzer/
│   └── gui/
├── rtl/
├── sim/
├── main.py
├── requirements.txt
├── boolean_board_8ch_logic_analyzer.xdc
├── check_verilog.tcl
└── README.md
```

## Troubleshooting

- **No COM port appears:** unplug and replug the Boolean Board USB cable.
- **Wrong serial port:** run `python3 -m serial.tools.list_ports -v` and look for FTDI.
- **No waveform:** check common ground between DUT/Arduino and Boolean Board.
- **Bad/corrupt waveform:** lower sample rate first, then check signal voltage and wiring.
- **GUI error `_tkinter`:** install `python3-tk`.
- **5 V Arduino Nano:** do not connect directly to FPGA pins; use level shifting.
