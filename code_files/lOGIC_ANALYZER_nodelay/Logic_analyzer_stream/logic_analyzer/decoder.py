"""Protocol decoders and summary formatting for captured digital samples."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DecodeEvent:
    """One decoded protocol event."""

    time_s: float
    kind: str
    value: str
    detail: str


@dataclass(frozen=True)
class DecodeReport:
    """Decoded events plus a short human-readable summary."""

    events: list[DecodeEvent]
    summary_lines: list[str]


def bit_at(sample: int, channel: int) -> int:
    """Return one channel bit from an 8-bit sample."""
    return (sample >> channel) & 1


def _ascii_text(values: list[int]) -> str:
    return "".join(chr(value) if 32 <= value <= 126 else "." for value in values)


def _hex_list(values: list[int]) -> str:
    return " ".join(f"{value:02X}" for value in values) if values else "-"


def decode_uart(samples: list[int], sample_rate: float, tx_ch: int, baud: int) -> list[DecodeEvent]:
    """Decode 8N1 UART bytes from one channel."""
    return decode_uart_report(samples, sample_rate, tx_ch, baud).events


def decode_uart_report(samples: list[int], sample_rate: float, tx_ch: int, baud: int) -> DecodeReport:
    """Decode UART and summarize the resulting byte stream."""
    events: list[DecodeEvent] = []
    values: list[int] = []
    bit_samples = max(1, round(sample_rate / baud))
    index = 1
    while index + bit_samples * 10 < len(samples):
        if bit_at(samples[index - 1], tx_ch) == 1 and bit_at(samples[index], tx_ch) == 0:
            value = 0
            for bit in range(8):
                sample_index = index + round((1.5 + bit) * bit_samples)
                value |= bit_at(samples[sample_index], tx_ch) << bit
            stop_index = index + round(9.5 * bit_samples)
            stop_ok = bit_at(samples[stop_index], tx_ch) == 1
            values.append(value)
            events.append(
                DecodeEvent(
                    time_s=index / sample_rate,
                    kind="UART",
                    value=f"0x{value:02X}",
                    detail=f"ASCII={chr(value)!r}, stop={'ok' if stop_ok else 'bad'}",
                )
            )
            index += bit_samples * 10
        else:
            index += 1

    summary_lines = [
        f"UART hex: {_hex_list(values)}",
        f"UART text: {_ascii_text(values)}",
    ] if values else ["UART: no bytes decoded"]
    return DecodeReport(events=events, summary_lines=summary_lines)


def decode_spi(
    samples: list[int],
    sample_rate: float,
    sclk_ch: int,
    mosi_ch: int,
    miso_ch: int,
    cs_ch: int,
    rising_edge: bool = True,
) -> list[DecodeEvent]:
    """Decode SPI bytes while CS is low."""
    return decode_spi_report(samples, sample_rate, sclk_ch, mosi_ch, miso_ch, cs_ch, rising_edge).events


def decode_spi_report(
    samples: list[int],
    sample_rate: float,
    sclk_ch: int,
    mosi_ch: int,
    miso_ch: int,
    cs_ch: int,
    rising_edge: bool = True,
) -> DecodeReport:
    """Decode SPI transactions and summarize MOSI/MISO byte groups."""
    events: list[DecodeEvent] = []
    summary_lines: list[str] = []
    transaction_id = 0
    mosi = 0
    miso = 0
    bit_count = 0
    byte_index = 0
    mosi_bytes: list[int] = []
    miso_bytes: list[int] = []
    transaction_start_time = 0.0
    transaction_active = False

    for index in range(1, len(samples)):
        prev_active = bit_at(samples[index - 1], cs_ch) == 0
        active = bit_at(samples[index], cs_ch) == 0
        old_clk = bit_at(samples[index - 1], sclk_ch)
        new_clk = bit_at(samples[index], sclk_ch)
        edge = old_clk == 0 and new_clk == 1 if rising_edge else old_clk == 1 and new_clk == 0

        if active and not prev_active:
            transaction_id += 1
            transaction_active = True
            transaction_start_time = index / sample_rate
            mosi = 0
            miso = 0
            bit_count = 0
            byte_index = 0
            mosi_bytes = []
            miso_bytes = []
            events.append(DecodeEvent(transaction_start_time, "SPI", "START", f"T{transaction_id}"))

        if transaction_active and edge and active:
            mosi = (mosi << 1) | bit_at(samples[index], mosi_ch)
            miso = (miso << 1) | bit_at(samples[index], miso_ch)
            bit_count += 1
            if bit_count == 8:
                mosi_bytes.append(mosi)
                miso_bytes.append(miso)
                events.append(
                    DecodeEvent(
                        index / sample_rate,
                        "SPI",
                        f"MOSI 0x{mosi:02X}",
                        f"T{transaction_id} byte {byte_index}, MISO 0x{miso:02X}",
                    )
                )
                byte_index += 1
                bit_count = 0
                mosi = 0
                miso = 0

        if transaction_active and not active and prev_active:
            events.append(DecodeEvent(index / sample_rate, "SPI", "END", f"T{transaction_id}"))
            summary_lines.append(
                f"SPI T{transaction_id} @{transaction_start_time:.6f}s: "
                f"MOSI [{_hex_list(mosi_bytes)}], MISO [{_hex_list(miso_bytes)}]"
            )
            transaction_active = False

    if transaction_active:
        summary_lines.append(
            f"SPI T{transaction_id} @{transaction_start_time:.6f}s: "
            f"MOSI [{_hex_list(mosi_bytes)}], MISO [{_hex_list(miso_bytes)}], unterminated"
        )

    if not summary_lines:
        summary_lines.append("SPI: no transactions decoded")
    return DecodeReport(events=events, summary_lines=summary_lines)


def decode_i2c(samples: list[int], sample_rate: float, scl_ch: int, sda_ch: int) -> list[DecodeEvent]:
    """Decode basic I2C address/data bytes with ACK markers."""
    return decode_i2c_report(samples, sample_rate, scl_ch, sda_ch).events


def decode_i2c_report(samples: list[int], sample_rate: float, scl_ch: int, sda_ch: int) -> DecodeReport:
    """Decode I2C transactions and summarize address, direction, and data bytes."""
    events: list[DecodeEvent] = []
    summary_lines: list[str] = []
    transaction_id = 0
    in_frame = False
    expecting_address = False
    value = 0
    count = 0
    address = 0
    direction = "W"
    data_bytes: list[int] = []
    ack_bits: list[str] = []
    transaction_start_time = 0.0

    def flush_summary(reason: str) -> None:
        if not in_frame and not data_bytes and not expecting_address:
            return
        if transaction_id == 0:
            return
        data_text = _hex_list(data_bytes)
        ack_text = " ".join(ack_bits) if ack_bits else "-"
        summary_lines.append(
            f"I2C T{transaction_id} @{transaction_start_time:.6f}s: "
            f"ADDR 0x{address:02X} {direction}, DATA [{data_text}], ACKS [{ack_text}], {reason}"
        )

    for index in range(1, len(samples)):
        old_scl = bit_at(samples[index - 1], scl_ch)
        new_scl = bit_at(samples[index], scl_ch)
        old_sda = bit_at(samples[index - 1], sda_ch)
        new_sda = bit_at(samples[index], sda_ch)

        if old_sda == 1 and new_sda == 0 and new_scl == 1:
            if in_frame:
                flush_summary("repeated START")
            transaction_id += 1
            in_frame = True
            expecting_address = True
            value = 0
            count = 0
            address = 0
            direction = "W"
            data_bytes = []
            ack_bits = []
            transaction_start_time = index / sample_rate
            events.append(DecodeEvent(transaction_start_time, "I2C", "START", f"T{transaction_id}"))
            continue

        if old_sda == 0 and new_sda == 1 and new_scl == 1 and in_frame:
            events.append(DecodeEvent(index / sample_rate, "I2C", "STOP", f"T{transaction_id}"))
            flush_summary("STOP")
            in_frame = False
            expecting_address = False
            value = 0
            count = 0
            continue

        if in_frame and old_scl == 0 and new_scl == 1:
            if count < 8:
                value = (value << 1) | new_sda
                count += 1
                if count == 8:
                    if expecting_address:
                        address = value >> 1
                        direction = "R" if (value & 1) else "W"
                        events.append(
                            DecodeEvent(index / sample_rate, "I2C", f"ADDR 0x{address:02X}", f"T{transaction_id} {direction}")
                        )
                        expecting_address = False
                    else:
                        data_bytes.append(value)
                        events.append(
                            DecodeEvent(
                                index / sample_rate,
                                "I2C",
                                f"DATA 0x{value:02X}",
                                f"T{transaction_id} byte {len(data_bytes) - 1}",
                            )
                        )
            else:
                ack = "ACK" if new_sda == 0 else "NAK"
                ack_bits.append(ack)
                events.append(DecodeEvent(index / sample_rate, "I2C", ack, f"T{transaction_id}"))
                value = 0
                count = 0

    if in_frame:
        flush_summary("unterminated")
    if not summary_lines:
        summary_lines.append("I2C: no transactions decoded")
    return DecodeReport(events=events, summary_lines=summary_lines)
