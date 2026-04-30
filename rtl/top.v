`timescale 1ns / 1ps
/*
 * Entity: top
 * Description: 8-channel FPGA logic analyzer for Real Digital Boolean Board.
 * Ports: clk, UART_rxd/UART_txd, pmod_in[7:0], led[4:0]
 * Author: OpenAI Codex
 */
module top (
    input  wire       clk,
    input  wire       UART_rxd,
    output wire       UART_txd,
    input  wire [7:0] pmod_in,
    output wire [4:0] led
);
    localparam ST_IDLE = 3'd0;
    localparam ST_ARMED = 3'd1;
    localparam ST_CAPTURE = 3'd2;
    localparam ST_TRANSMIT = 3'd3;

    reg [7:0] reset_counter = 8'hff;
    wire reset = (reset_counter != 8'h00);

    always @(posedge clk) begin
        if (reset_counter != 8'h00) begin
            reset_counter <= reset_counter - 1'b1;
        end
    end

    wire sample_tick;
    wire [7:0] sample_data;
    wire [7:0] rx_byte;
    wire rx_valid;
    wire [7:0] uart_tx_byte;
    wire uart_tx_start;
    wire uart_tx_busy;
    wire start_cmd;
    wire stop_cmd;
    wire [3:0] rate_code;
    wire [15:0] depth;
    wire [1:0] trig_mode;
    wire [2:0] trig_channel;
    wire [7:0] trig_pattern;
    wire command_seen;
    wire trigger_hit;
    wire bram_capture_done;
    wire [15:0] samples_written;
    wire rd_en;
    wire [14:0] rd_addr;
    wire [7:0] rd_data;
    wire tx_busy;
    wire tx_done;

    reg [2:0] state;
    reg tx_start_capture;

    clk_manager u_clk_manager (
        .clk(clk),
        .reset(reset),
        .rate_code(rate_code),
        .sample_tick(sample_tick)
    );

    input_sampler u_input_sampler (
        .clk(clk),
        .reset(reset),
        .sample_tick(sample_tick),
        .data_in(pmod_in),
        .sample_data(sample_data)
    );

    uart u_uart (
        .clk(clk),
        .reset(reset),
        .rx(UART_rxd),
        .tx(UART_txd),
        .tx_byte(uart_tx_byte),
        .tx_start(uart_tx_start),
        .tx_busy(uart_tx_busy),
        .rx_byte(rx_byte),
        .rx_valid(rx_valid)
    );

    cmd_parser u_cmd_parser (
        .clk(clk),
        .reset(reset),
        .rx_byte(rx_byte),
        .rx_valid(rx_valid),
        .start_pulse(start_cmd),
        .stop_pulse(stop_cmd),
        .rate_code(rate_code),
        .depth(depth),
        .trig_mode(trig_mode),
        .trig_channel(trig_channel),
        .trig_pattern(trig_pattern),
        .command_seen(command_seen)
    );

    trigger u_trigger (
        .clk(clk),
        .reset(reset || state == ST_IDLE || stop_cmd),
        .arm(state == ST_ARMED),
        .sample_tick(sample_tick),
        .sample_data(sample_data),
        .trig_mode(trig_mode),
        .trig_channel(trig_channel),
        .trig_pattern(trig_pattern),
        .triggered(trigger_hit)
    );

    bram_ctrl u_bram_ctrl (
        .clk(clk),
        .reset(reset || state == ST_IDLE || stop_cmd),
        .capture_en(state == ST_CAPTURE),
        .sample_tick(sample_tick),
        .sample_data(sample_data),
        .depth(depth),
        .rd_en(rd_en),
        .rd_addr(rd_addr),
        .data_out(rd_data),
        .capture_done(bram_capture_done),
        .samples_written(samples_written)
    );

    data_tx u_data_tx (
        .clk(clk),
        .reset(reset || stop_cmd),
        .start(tx_start_capture),
        .depth(depth),
        .rd_en(rd_en),
        .rd_addr(rd_addr),
        .rd_data(rd_data),
        .tx_byte(uart_tx_byte),
        .tx_start(uart_tx_start),
        .tx_busy(uart_tx_busy),
        .busy(tx_busy),
        .done(tx_done)
    );

    led_driver u_led_driver (
        .clk(clk),
        .reset(reset),
        .command_seen(command_seen),
        .fsm_state(state),
        .led(led)
    );

    always @(posedge clk) begin
        if (reset || stop_cmd) begin
            state <= ST_IDLE;
            tx_start_capture <= 1'b0;
        end else begin
            tx_start_capture <= 1'b0;
            case (state)
                ST_IDLE: begin
                    if (start_cmd) begin
                        state <= ST_ARMED;
                    end
                end
                ST_ARMED: begin
                    if (trigger_hit) begin
                        state <= ST_CAPTURE;
                    end
                end
                ST_CAPTURE: begin
                    if (bram_capture_done) begin
                        tx_start_capture <= 1'b1;
                        state <= ST_TRANSMIT;
                    end
                end
                ST_TRANSMIT: begin
                    if (tx_done) begin
                        state <= ST_IDLE;
                    end
                end
                default: state <= ST_IDLE;
            endcase
        end
    end
endmodule
