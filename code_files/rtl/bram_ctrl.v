`timescale 1ns / 1ps
/*
 * Entity: bram_ctrl
 * Description: 32768 x 8 sample buffer with independent write/read controls.
 * Ports: clk, reset, capture_en, sample_tick, sample_data, depth, rd_* -> data_out/capture_done
 * Author: OpenAI Codex
 */
module bram_ctrl (
    input  wire        clk,
    input  wire        reset,
    input  wire        capture_en,
    input  wire        sample_tick,
    input  wire [7:0]  sample_data,
    input  wire [15:0] depth,
    input  wire        rd_en,
    input  wire [14:0] rd_addr,
    output reg  [7:0]  data_out,
    output reg         capture_done,
    output reg  [15:0] samples_written
);
    (* ram_style = "block" *) reg [7:0] mem [0:32767];
    reg [14:0] wr_addr;

    wire [15:0] effective_depth = (depth == 16'd0) ? 16'd1 : depth;
    wire last_sample = (samples_written + 16'd1 >= effective_depth);

    always @(posedge clk) begin
        if (reset) begin
            wr_addr <= 15'd0;
            samples_written <= 16'd0;
            capture_done <= 1'b0;
            data_out <= 8'h00;
        end else begin
            if (rd_en) begin
                data_out <= mem[rd_addr];
            end

            if (capture_en && sample_tick && !capture_done) begin
                mem[wr_addr] <= sample_data;
                wr_addr <= wr_addr + 1'b1;
                samples_written <= samples_written + 1'b1;
                if (last_sample) begin
                    capture_done <= 1'b1;
                end
            end
        end
    end
endmodule
