read_verilog [glob ./rtl/*.v]
read_xdc ./boolean_board_8ch_logic_analyzer.xdc
synth_design -top top -part xc7s50csga324-1 -mode out_of_context
