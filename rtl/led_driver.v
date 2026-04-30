`timescale 1ns / 1ps
/*
 * Entity: led_driver
 * Description: Maps analyzer state to onboard status LEDs.
 * Ports: clk, reset, command_seen, fsm_state -> led
 * Author: OpenAI Codex
 */
module led_driver (
    input  wire       clk,
    input  wire       reset,
    input  wire       command_seen,
    input  wire [2:0] fsm_state,
    output reg  [4:0] led
);
    reg [25:0] blink_counter;
    wire idle_blink = blink_counter[25];

    always @(posedge clk) begin
        if (reset) begin
            blink_counter <= 26'd0;
            led <= 5'b00000;
        end else begin
            blink_counter <= blink_counter + 1'b1;
            led[0] <= command_seen;
            led[1] <= (fsm_state == 3'd1);
            led[2] <= (fsm_state == 3'd2);
            led[3] <= (fsm_state == 3'd3);
            led[4] <= (fsm_state == 3'd0) ? idle_blink : 1'b0;
        end
    end
endmodule
