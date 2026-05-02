read_verilog [glob ./rtl/*.v]
read_xdc ./arty7_logic_analyser.xdc
synth_design -top top -part xc7a100tcsg324-1
