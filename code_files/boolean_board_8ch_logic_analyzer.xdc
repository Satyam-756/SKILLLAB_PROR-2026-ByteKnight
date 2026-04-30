## Real Digital Boolean Board - 8-channel logic analyzer constraints
## Board: Xilinx Spartan-7 XC7S50-CSGA324-1

## 100 MHz onboard oscillator
set_property -dict {PACKAGE_PIN F14 IOSTANDARD LVCMOS33} [get_ports {clk}]
create_clock -period 10.000 -name clk_100mhz [get_ports {clk}]

## USB-UART through PROG/UART connector
set_property -dict {PACKAGE_PIN V12 IOSTANDARD LVCMOS33} [get_ports {UART_rxd}]
set_property -dict {PACKAGE_PIN U11 IOSTANDARD LVCMOS33} [get_ports {UART_txd}]

## Status LEDs (led[0] to led[4])
set_property -dict {PACKAGE_PIN G1 IOSTANDARD LVCMOS33} [get_ports {led[0]}]
set_property -dict {PACKAGE_PIN G2 IOSTANDARD LVCMOS33} [get_ports {led[1]}]
set_property -dict {PACKAGE_PIN F1 IOSTANDARD LVCMOS33} [get_ports {led[2]}]
set_property -dict {PACKAGE_PIN F2 IOSTANDARD LVCMOS33} [get_ports {led[3]}]
set_property -dict {PACKAGE_PIN E1 IOSTANDARD LVCMOS33} [get_ports {led[4]}]

## 8 analyzer inputs on Pmod A
## Upper Row (Pins 1-4)
set_property -dict {PACKAGE_PIN B13 IOSTANDARD LVCMOS33} [get_ports {pmod_in[0]}]
set_property -dict {PACKAGE_PIN A13 IOSTANDARD LVCMOS33} [get_ports {pmod_in[1]}]
set_property -dict {PACKAGE_PIN B14 IOSTANDARD LVCMOS33} [get_ports {pmod_in[2]}]
set_property -dict {PACKAGE_PIN A14 IOSTANDARD LVCMOS33} [get_ports {pmod_in[3]}]
## Lower Row (Pins 7-10)
set_property -dict {PACKAGE_PIN E12 IOSTANDARD LVCMOS33} [get_ports {pmod_in[4]}]
set_property -dict {PACKAGE_PIN D12 IOSTANDARD LVCMOS33} [get_ports {pmod_in[5]}]
set_property -dict {PACKAGE_PIN C13 IOSTANDARD LVCMOS33} [get_ports {pmod_in[6]}]
set_property -dict {PACKAGE_PIN C14 IOSTANDARD LVCMOS33} [get_ports {pmod_in[7]}]

## Configuration voltage
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]