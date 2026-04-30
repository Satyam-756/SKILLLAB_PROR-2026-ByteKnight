`timescale 1ns / 1ps
/*
 * Entity: uart
 * Description: Full-duplex UART, 115200 baud, 8N1, 100 MHz clock.
 * Ports: clk, reset, rx, tx_byte/tx_start -> tx, rx_byte/rx_valid/tx_busy
 * Author: OpenAI Codex
 */
module uart (
    input  wire       clk,
    input  wire       reset,
    input  wire       rx,
    output wire       tx,
    input  wire [7:0] tx_byte,
    input  wire       tx_start,
    output reg        tx_busy,
    output reg  [7:0] rx_byte,
    output reg        rx_valid
);
    localparam integer CLKS_PER_BIT = 868;

    reg [9:0] tx_shift;
    reg [3:0] tx_bit_index;
    reg [15:0] tx_clk_count;
    reg tx_reg;
    assign tx = tx_reg;

    reg rx_meta;
    reg rx_sync;
    reg rx_prev;
    reg [3:0] rx_bit_index;
    reg [15:0] rx_clk_count;
    reg [7:0] rx_shift;
    reg [1:0] rx_state;

    localparam RX_IDLE  = 2'd0;
    localparam RX_START = 2'd1;
    localparam RX_DATA  = 2'd2;
    localparam RX_STOP  = 2'd3;

    always @(posedge clk) begin
        if (reset) begin
            tx_reg <= 1'b1;
            tx_busy <= 1'b0;
            tx_shift <= 10'h3ff;
            tx_bit_index <= 4'd0;
            tx_clk_count <= 16'd0;
        end else if (tx_start && !tx_busy) begin
            tx_shift <= {1'b1, tx_byte, 1'b0};
            tx_busy <= 1'b1;
            tx_bit_index <= 4'd0;
            tx_clk_count <= 16'd0;
        end else if (tx_busy) begin
            tx_reg <= tx_shift[tx_bit_index];
            if (tx_clk_count == CLKS_PER_BIT - 1) begin
                tx_clk_count <= 16'd0;
                if (tx_bit_index == 4'd9) begin
                    tx_busy <= 1'b0;
                    tx_reg <= 1'b1;
                end else begin
                    tx_bit_index <= tx_bit_index + 1'b1;
                end
            end else begin
                tx_clk_count <= tx_clk_count + 1'b1;
            end
        end
    end

    always @(posedge clk) begin
        rx_meta <= rx;
        rx_sync <= rx_meta;
        rx_prev <= rx_sync;

        if (reset) begin
            rx_state <= RX_IDLE;
            rx_valid <= 1'b0;
            rx_byte <= 8'h00;
            rx_shift <= 8'h00;
            rx_bit_index <= 4'd0;
            rx_clk_count <= 16'd0;
        end else begin
            rx_valid <= 1'b0;
            case (rx_state)
                RX_IDLE: begin
                    if (rx_prev && !rx_sync) begin
                        rx_state <= RX_START;
                        rx_clk_count <= CLKS_PER_BIT / 2;
                    end
                end
                RX_START: begin
                    if (rx_clk_count == 0) begin
                        if (!rx_sync) begin
                            rx_state <= RX_DATA;
                            rx_clk_count <= CLKS_PER_BIT - 1;
                            rx_bit_index <= 4'd0;
                        end else begin
                            rx_state <= RX_IDLE;
                        end
                    end else begin
                        rx_clk_count <= rx_clk_count - 1'b1;
                    end
                end
                RX_DATA: begin
                    if (rx_clk_count == 0) begin
                        rx_shift[rx_bit_index] <= rx_sync;
                        rx_clk_count <= CLKS_PER_BIT - 1;
                        if (rx_bit_index == 4'd7) begin
                            rx_state <= RX_STOP;
                        end else begin
                            rx_bit_index <= rx_bit_index + 1'b1;
                        end
                    end else begin
                        rx_clk_count <= rx_clk_count - 1'b1;
                    end
                end
                RX_STOP: begin
                    if (rx_clk_count == 0) begin
                        rx_byte <= rx_shift;
                        rx_valid <= 1'b1;
                        rx_state <= RX_IDLE;
                    end else begin
                        rx_clk_count <= rx_clk_count - 1'b1;
                    end
                end
                default: rx_state <= RX_IDLE;
            endcase
        end
    end
endmodule
