`timescale 1ns / 1ps
/*
 * Entity: cmd_parser
 * Description: Parses ASCII commands from the PC GUI.
 * Ports: clk, reset, rx_byte, rx_valid -> control registers and command strobes
 * Author: OpenAI Codex
 */
module cmd_parser (
    input  wire       clk,
    input  wire       reset,
    input  wire [7:0] rx_byte,
    input  wire       rx_valid,
    output reg        start_pulse,
    output reg        stop_pulse,
    output reg [3:0]  rate_code,
    output reg [15:0] depth,
    output reg [1:0]  trig_mode,
    output reg [2:0]  trig_channel,
    output reg [7:0]  trig_pattern,
    output reg        command_seen
);
    reg [7:0] line [0:31];
    reg [5:0] len;
    integer i;
    reg [15:0] parsed_depth;

    function [3:0] dec_value;
        input [7:0] c;
        begin
            if (c >= "0" && c <= "9") dec_value = c - "0";
            else dec_value = 4'd0;
        end
    endfunction

    function [3:0] hex_value;
        input [7:0] c;
        begin
            if (c >= "0" && c <= "9") hex_value = c - "0";
            else if (c >= "A" && c <= "F") hex_value = c - "A" + 4'd10;
            else if (c >= "a" && c <= "f") hex_value = c - "a" + 4'd10;
            else hex_value = 4'd0;
        end
    endfunction

    always @(posedge clk) begin
        if (reset) begin
            len <= 6'd0;
            start_pulse <= 1'b0;
            stop_pulse <= 1'b0;
            rate_code <= 4'd5;
            depth <= 16'd1024;
            trig_mode <= 2'b00;
            trig_channel <= 3'd0;
            trig_pattern <= 8'h00;
            command_seen <= 1'b0;
            for (i = 0; i < 32; i = i + 1) begin
                line[i] <= 8'h00;
            end
        end else begin
            start_pulse <= 1'b0;
            stop_pulse <= 1'b0;

            if (rx_valid) begin
                command_seen <= 1'b1;
                if (rx_byte == 8'h0A || rx_byte == 8'h0D) begin
                    if (len != 0) begin
                        if (len == 5 &&
                            line[0] == "S" && line[1] == "T" && line[2] == "A" &&
                            line[3] == "R" && line[4] == "T") begin
                            start_pulse <= 1'b1;
                        end else if (len == 4 &&
                            line[0] == "S" && line[1] == "T" && line[2] == "O" &&
                            line[3] == "P") begin
                            stop_pulse <= 1'b1;
                        end else if (len >= 7 &&
                            line[0] == "R" && line[1] == "A" && line[2] == "T" &&
                            line[3] == "E" && line[4] == ":") begin
                            rate_code <= (dec_value(line[5]) * 4'd10) + dec_value(line[6]);
                        end else if (len >= 7 &&
                            line[0] == "D" && line[1] == "E" && line[2] == "P" &&
                            line[3] == "T" && line[4] == "H" && line[5] == ":") begin
                            parsed_depth = 16'd0;
                            for (i = 6; i < 16; i = i + 1) begin
                                if (i < len && line[i] >= "0" && line[i] <= "9") begin
                                    parsed_depth = (parsed_depth * 16'd10) + dec_value(line[i]);
                                end
                            end
                            if (parsed_depth == 16'd0) depth <= 16'd1;
                            else if (parsed_depth > 16'd32768) depth <= 16'd32768;
                            else depth <= parsed_depth;
                        end else if (len >= 8 &&
                            line[0] == "T" && line[1] == "R" && line[2] == "I" &&
                            line[3] == "G" && line[4] == ":" &&
                            line[5] == "I" && line[6] == "M" && line[7] == "M") begin
                            trig_mode <= 2'b00;
                        end else if (len >= 11 &&
                            line[0] == "T" && line[1] == "R" && line[2] == "I" &&
                            line[3] == "G" && line[4] == ":" &&
                            line[5] == "R" && line[6] == "I" && line[7] == "S" &&
                            line[8] == "E" && line[9] == ":") begin
                            trig_mode <= 2'b01;
                            trig_channel <= dec_value(line[10]);
                        end else if (len >= 11 &&
                            line[0] == "T" && line[1] == "R" && line[2] == "I" &&
                            line[3] == "G" && line[4] == ":" &&
                            line[5] == "F" && line[6] == "A" && line[7] == "L" &&
                            line[8] == "L" && line[9] == ":") begin
                            trig_mode <= 2'b10;
                            trig_channel <= dec_value(line[10]);
                        end else if (len >= 11 &&
                            line[0] == "T" && line[1] == "R" && line[2] == "I" &&
                            line[3] == "G" && line[4] == ":" &&
                            line[5] == "P" && line[6] == "A" && line[7] == "T" &&
                            line[8] == ":") begin
                            trig_mode <= 2'b11;
                            trig_pattern <= {hex_value(line[9]), hex_value(line[10])};
                        end
                    end
                    len <= 6'd0;
                end else if (len < 6'd32) begin
                    line[len] <= rx_byte;
                    len <= len + 1'b1;
                end
            end
        end
    end
endmodule
