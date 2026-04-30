`timescale 1ns / 1ps
/*
 * Entity: trigger
 * Description: Immediate, edge, and 8-bit pattern trigger detector.
 * Ports: clk, reset, arm, sample_tick, sample_data, config -> triggered
 * Author: OpenAI Codex
 */
module trigger (
    input  wire       clk,
    input  wire       reset,
    input  wire       arm,
    input  wire       sample_tick,
    input  wire [7:0] sample_data,
    input  wire [1:0] trig_mode,
    input  wire [2:0] trig_channel,
    input  wire [7:0] trig_pattern,
    output reg        triggered
);
    reg [7:0] prev_sample;

    wire selected_now = sample_data[trig_channel];
    wire selected_prev = prev_sample[trig_channel];

    always @(posedge clk) begin
        if (reset || !arm) begin
            triggered <= 1'b0;
            prev_sample <= sample_data;
        end else if (sample_tick) begin
            prev_sample <= sample_data;
            if (!triggered) begin
                case (trig_mode)
                    2'b00: triggered <= 1'b1;
                    2'b01: triggered <= !selected_prev && selected_now;
                    2'b10: triggered <= selected_prev && !selected_now;
                    2'b11: triggered <= (sample_data == trig_pattern);
                    default: triggered <= 1'b0;
                endcase
            end
        end
    end
endmodule
