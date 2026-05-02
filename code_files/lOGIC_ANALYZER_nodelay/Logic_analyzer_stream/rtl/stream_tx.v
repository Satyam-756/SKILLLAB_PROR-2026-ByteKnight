`timescale 1ns / 1ps

module stream_tx (
    input  wire       clk,
    input  wire       reset,
    input  wire [7:0] sample_data,
    input  wire       sample_tick,

    output reg [7:0]  tx_byte,
    output reg        tx_start,
    input  wire       tx_busy
);

    reg [1:0] state = 0;
    reg [7:0] data_buf;

    function [7:0] hex;
        input [3:0] n;
        begin
            if (n < 10)
                hex = "0" + n;
            else
                hex = "A" + (n - 10);
        end
    endfunction

    always @(posedge clk) begin
        if (reset) begin
            state <= 0;
            tx_start <= 0;
        end else begin
            tx_start <= 0;

            case (state)

            // WAIT FOR NEW SAMPLE (SYNCED)
            0: begin
                if (sample_tick && !tx_busy) begin
                    data_buf <= sample_data;
                    tx_byte  <= hex(sample_data[7:4]);
                    tx_start <= 1;
                    state    <= 1;
                end
            end

            // LOW NIBBLE
            1: begin
                if (!tx_busy) begin
                    tx_byte  <= hex(data_buf[3:0]);
                    tx_start <= 1;
                    state    <= 2;
                end
            end

            // NEWLINE
            2: begin
                if (!tx_busy) begin
                    tx_byte  <= "\n";
                    tx_start <= 1;
                    state    <= 0;
                end
            end

            endcase
        end
    end

endmodule