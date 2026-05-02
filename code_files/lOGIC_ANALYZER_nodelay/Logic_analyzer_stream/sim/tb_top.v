`timescale 1ns / 1ps
/*
 * Entity: tb_top
 * Description: Simulation testbench for UART-controlled 8-channel capture.
 * Ports: none
 * Author: OpenAI Codex
 */
module tb_top;
    reg clk = 1'b0;
    reg uart_rx = 1'b1;
    reg [7:0] pmod_in = 8'h00;
    wire uart_tx;
    wire [4:0] led;

    localparam integer CLK_PERIOD_NS = 10;
    localparam integer BIT_PERIOD_NS = 8680;

    top dut (
        .clk(clk),
        .UART_rxd(uart_rx),
        .UART_txd(uart_tx),
        .pmod_in(pmod_in),
        .led(led)
    );

    always #(CLK_PERIOD_NS / 2) clk = ~clk;

    always @(posedge clk) begin
        pmod_in <= pmod_in + 8'h1D;
    end

    task uart_send_byte;
        input [7:0] value;
        integer bit_index;
        begin
            uart_rx = 1'b0;
            #(BIT_PERIOD_NS);
            for (bit_index = 0; bit_index < 8; bit_index = bit_index + 1) begin
                uart_rx = value[bit_index];
                #(BIT_PERIOD_NS);
            end
            uart_rx = 1'b1;
            #(BIT_PERIOD_NS);
        end
    endtask

    task uart_send_string;
        input [8 * 16 - 1:0] text;
        input integer count;
        integer idx;
        reg [7:0] ch;
        begin
            for (idx = count - 1; idx >= 0; idx = idx - 1) begin
                ch = text[idx * 8 +: 8];
                uart_send_byte(ch);
            end
        end
    endtask

    initial begin
        $dumpfile("tb_top.vcd");
        $dumpvars(0, tb_top);
        #(5000);
        uart_send_string("RATE:09         ", 8);
        uart_send_byte(8'h0A);
        uart_send_string("DEPTH:00008     ", 11);
        uart_send_byte(8'h0A);
        uart_send_string("TRIG:IMM        ", 8);
        uart_send_byte(8'h0A);
        uart_send_string("START           ", 5);
        uart_send_byte(8'h0A);
        #(2_000_000);
        $display("Simulation finished. Inspect UART_txd for eight hex sample lines and DONE.");
        $finish;
    end
endmodule
