`timescale 1ns / 1ps
/*
 * Entity: clk_manager
 * Description: Generates one-cycle sample ticks from the 100 MHz board clock.
 * Ports: clk, reset, rate_code -> sample_tick
 * Author: OpenAI Codex
 */
module clk_manager (
    input  wire       clk,
    input  wire       reset,
    input  wire [3:0] rate_code,
    output reg        sample_tick
);
    reg [31:0] counter;
    reg [31:0] divider;

    always @(*) begin
        case (rate_code)
            4'd0: divider = 32'd100_000_000; // 1 Hz
            4'd1: divider = 32'd10_000_000;  // 10 Hz
            4'd2: divider = 32'd1_000_000;   // 100 Hz
            4'd3: divider = 32'd100_000;     // 1 kHz
            4'd4: divider = 32'd10_000;      // 10 kHz
            4'd5: divider = 32'd1_000;       // 100 kHz
            4'd6: divider = 32'd100;         // 1 MHz
            4'd7: divider = 32'd10;          // 10 MHz
            4'd8: divider = 32'd2;           // 50 MHz
            4'd9: divider = 32'd1;           // 100 MHz
            default: divider = 32'd1_000;    // 100 kHz
        endcase
    end

    always @(posedge clk) begin
        if (reset) begin
            counter <= 32'd0;
            sample_tick <= 1'b0;
        end else if (divider <= 32'd1) begin
            counter <= 32'd0;
            sample_tick <= 1'b1;
        end else if (counter == divider - 1) begin
            counter <= 32'd0;
            sample_tick <= 1'b1;
        end else begin
            counter <= counter + 1'b1;
            sample_tick <= 1'b0;
        end
    end
endmodule
