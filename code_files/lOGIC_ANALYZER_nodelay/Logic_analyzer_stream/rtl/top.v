`timescale 1ns / 1ps

module top (
    input  wire       clk,
    input  wire       UART_rxd,
    output wire       UART_txd,
    input  wire [7:0] pmod_in,
    output wire [4:0] led
);

    // ================= RESET =================
    reg [7:0] reset_counter = 8'hFF;
    wire reset = (reset_counter != 0);

    always @(posedge clk) begin
        if (reset_counter != 0)
            reset_counter <= reset_counter - 1;
    end

    // ================= UART =================
    wire [7:0] uart_tx_byte;
    wire uart_tx_start;
    wire uart_tx_busy;

    uart uart_inst (
        .clk(clk),
        .reset(reset),
        .rx(UART_rxd),
        .tx(UART_txd),
        .tx_byte(uart_tx_byte),
        .tx_start(uart_tx_start),
        .tx_busy(uart_tx_busy),
        .rx_byte(),
        .rx_valid()
    );

    // ================= SAMPLING (SYNCED WITH UART) =================
    reg sample_tick;
    reg [7:0] sample_data;

    always @(posedge clk) begin
        // Only sample when UART is free → no dropped samples
        sample_tick <= !uart_tx_busy;

        if (!uart_tx_busy)
            sample_data <= pmod_in;
    end

    // ================= STREAM TX =================
    stream_tx tx (
        .clk(clk),
        .reset(reset),
        .sample_data(sample_data),
        .sample_tick(sample_tick),   // IMPORTANT
        .tx_byte(uart_tx_byte),
        .tx_start(uart_tx_start),
        .tx_busy(uart_tx_busy)
    );

    // ================= DEBUG =================
    assign led[0] = sample_data[0];
    assign led[1] = sample_data[1];
    assign led[2] = uart_tx_busy;
    assign led[3] = uart_tx_start;
    assign led[4] = sample_data[2];

endmodule