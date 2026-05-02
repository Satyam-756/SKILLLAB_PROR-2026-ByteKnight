`timescale 1ns / 1ps
/*
 * Entity: bram_ctrl
 * Description: 32768 x 8 circular sample buffer with pre-trigger capture support.
 * Ports: clk, reset, arm, trigger_hit, sample_tick, config, rd_* -> capture metadata and data_out
 */
module bram_ctrl (
    input  wire        clk,
    input  wire        reset,
    input  wire        arm,
    input  wire        trigger_hit,
    input  wire        sample_tick,
    input  wire [7:0]  sample_data,
    input  wire [15:0] depth,
    input  wire [15:0] pretrigger,
    input  wire        rd_en,
    input  wire [14:0] rd_addr,
    output reg  [7:0]  data_out,
    output reg         capture_done,
    output reg  [15:0] samples_written,
    output reg  [14:0] start_addr,
    output reg  [15:0] trigger_index
);
    (* ram_style = "block" *) reg [7:0] mem [0:32767];

    reg [14:0] wr_addr;
    reg        trigger_seen;
    reg [15:0] history_count;
    reg [15:0] post_count;
    reg [15:0] post_target;

    wire [15:0] effective_depth = (depth == 16'd0) ? 16'd1 : depth;
    wire [15:0] depth_minus_one = effective_depth - 16'd1;
    wire [15:0] effective_pretrigger = (pretrigger > depth_minus_one) ? depth_minus_one : pretrigger;
    wire [15:0] available_pretrigger = (history_count < effective_pretrigger) ? history_count : effective_pretrigger;
    wire [14:0] wrapped_start_addr = wr_addr - available_pretrigger[14:0];

    always @(posedge clk) begin
        if (reset) begin
            wr_addr <= 15'd0;
            trigger_seen <= 1'b0;
            history_count <= 16'd0;
            post_count <= 16'd0;
            post_target <= 16'd0;
            samples_written <= 16'd0;
            capture_done <= 1'b0;
            data_out <= 8'h00;
            start_addr <= 15'd0;
            trigger_index <= 16'd0;
        end else begin
            if (rd_en && capture_done) begin
                data_out <= mem[rd_addr];
            end

            if (arm && sample_tick && !capture_done) begin
                mem[wr_addr] <= sample_data;
                wr_addr <= wr_addr + 1'b1;

                if (!trigger_seen) begin
                    if (history_count < 16'd32768) begin
                        history_count <= history_count + 16'd1;
                    end

                    if (trigger_hit) begin
                        trigger_seen <= 1'b1;
                        trigger_index <= available_pretrigger;
                        start_addr <= wrapped_start_addr;
                        post_target <= effective_depth - available_pretrigger;
                        post_count <= 16'd1;
                        samples_written <= available_pretrigger + 16'd1;
                        if (effective_depth - available_pretrigger <= 16'd1) begin
                            capture_done <= 1'b1;
                        end
                    end else if (samples_written < effective_depth) begin
                        samples_written <= samples_written + 16'd1;
                    end
                end else begin
                    if (post_count < effective_depth) begin
                        post_count <= post_count + 16'd1;
                    end
                    if (samples_written < effective_depth) begin
                        samples_written <= samples_written + 16'd1;
                    end
                    if (post_count + 16'd1 >= post_target) begin
                        capture_done <= 1'b1;
                    end
                end
            end
        end
    end
endmodule
