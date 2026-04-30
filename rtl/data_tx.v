`timescale 1ns / 1ps
/*
 * Entity: data_tx
 * Description: Streams captured 8-bit samples as ASCII hex lines, then DONE.
 * Ports: clk, reset, start, depth, BRAM read port, UART TX port -> busy/done
 * Author: OpenAI Codex
 */
module data_tx (
    input  wire        clk,
    input  wire        reset,
    input  wire        start,
    input  wire [15:0] depth,
    output reg         rd_en,
    output reg  [14:0] rd_addr,
    input  wire [7:0]  rd_data,
    output reg  [7:0]  tx_byte,
    output reg         tx_start,
    input  wire        tx_busy,
    output reg         busy,
    output reg         done
);
    localparam S_IDLE    = 4'd0;
    localparam S_READ    = 4'd1;
    localparam S_WAIT    = 4'd2;
    localparam S_SEND_HI = 4'd3;
    localparam S_SEND_LO = 4'd4;
    localparam S_SEND_NL = 4'd5;
    localparam S_DONE_D  = 4'd6;
    localparam S_DONE_O  = 4'd7;
    localparam S_DONE_N  = 4'd8;
    localparam S_DONE_E  = 4'd9;
    localparam S_DONE_NL = 4'd10;

    reg [3:0] state;
    reg [7:0] sample;
    reg [15:0] sample_index;

    function [7:0] hex_char;
        input [3:0] nibble;
        begin
            if (nibble < 4'd10) hex_char = "0" + nibble;
            else hex_char = "A" + (nibble - 4'd10);
        end
    endfunction

    task send_when_ready;
        input [7:0] value;
        input [3:0] next_state;
        begin
            if (!tx_busy && !tx_start) begin
                tx_byte <= value;
                tx_start <= 1'b1;
                state <= next_state;
            end
        end
    endtask

    always @(posedge clk) begin
        if (reset) begin
            state <= S_IDLE;
            rd_en <= 1'b0;
            rd_addr <= 15'd0;
            tx_byte <= 8'h00;
            tx_start <= 1'b0;
            busy <= 1'b0;
            done <= 1'b0;
            sample <= 8'h00;
            sample_index <= 16'd0;
        end else begin
            rd_en <= 1'b0;
            tx_start <= 1'b0;
            done <= 1'b0;

            case (state)
                S_IDLE: begin
                    busy <= 1'b0;
                    if (start) begin
                        busy <= 1'b1;
                        rd_addr <= 15'd0;
                        sample_index <= 16'd0;
                        state <= S_READ;
                    end
                end
                S_READ: begin
                    rd_en <= 1'b1;
                    state <= S_WAIT;
                end
                S_WAIT: begin
                    sample <= rd_data;
                    state <= S_SEND_HI;
                end
                S_SEND_HI: send_when_ready(hex_char(sample[7:4]), S_SEND_LO);
                S_SEND_LO: send_when_ready(hex_char(sample[3:0]), S_SEND_NL);
                S_SEND_NL: begin
                    if (!tx_busy && !tx_start) begin
                        tx_byte <= 8'h0A;
                        tx_start <= 1'b1;
                        sample_index <= sample_index + 1'b1;
                        if (sample_index + 16'd1 >= depth) begin
                            state <= S_DONE_D;
                        end else begin
                            rd_addr <= rd_addr + 1'b1;
                            state <= S_READ;
                        end
                    end
                end
                S_DONE_D: send_when_ready("D", S_DONE_O);
                S_DONE_O: send_when_ready("O", S_DONE_N);
                S_DONE_N: send_when_ready("N", S_DONE_E);
                S_DONE_E: send_when_ready("E", S_DONE_NL);
                S_DONE_NL: begin
                    if (!tx_busy && !tx_start) begin
                        tx_byte <= 8'h0A;
                        tx_start <= 1'b1;
                        busy <= 1'b0;
                        done <= 1'b1;
                        state <= S_IDLE;
                    end
                end
                default: state <= S_IDLE;
            endcase
        end
    end
endmodule
