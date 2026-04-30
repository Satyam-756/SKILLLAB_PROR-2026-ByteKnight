`timescale 1ns / 1ps
/*
 * Entity: input_sampler
 * Description: Simultaneously samples 8 digital probe inputs.
 * Ports: clk, reset, sample_tick, data_in -> sample_data
 * Author: OpenAI Codex
 */
module input_sampler (
    input  wire       clk,
    input  wire       reset,
    input  wire       sample_tick,
    input  wire [7:0] data_in,
    output reg  [7:0] sample_data
);
    always @(posedge clk) begin
        if (reset) begin
            sample_data <= 8'h00;
        end else if (sample_tick) begin
            sample_data <= data_in;
        end
    end
endmodule
