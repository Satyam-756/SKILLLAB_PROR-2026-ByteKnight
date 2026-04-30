"""Simple software protocol decoders for captured digital samples."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DecodeEvent:
    """One decoded protocol event."""

    time_s: float
    kind: str
    value: str
    detail: str


def bit_at(sample: int, channel: int) -> int:
    """Return one channel bit from an 8-bit sample."""
    return (sample >> channel) & 1


def decode_uart(samples: list[int], sample_rate: float, tx_ch: int, baud: int) -> list[DecodeEvent]:
    """Decode 8N1 UART bytes from one channel."""
    events: list[DecodeEvent] = []
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
            events.append(
                DecodeEvent(
                    time_s=index / sample_rate,
                    kind="UART",
                    value=f"0x{value:02X}",
                    detail=f"char={chr(value)!r}, stop={'ok' if stop_ok else 'bad'}",
                )
            )
            index += bit_samples * 10
        else:
            index += 1
    return events


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
    events: list[DecodeEvent] = []
    mosi = 0
    miso = 0
    count = 0
    for index in range(1, len(samples)):
        cs_active = bit_at(samples[index], cs_ch) == 0
        old_clk = bit_at(samples[index - 1], sclk_ch)
        new_clk = bit_at(samples[index], sclk_ch)
        edge = old_clk == 0 and new_clk == 1 if rising_edge else old_clk == 1 and new_clk == 0
        if not cs_active:
            count = 0
            mosi = 0
            miso = 0
            continue
        if edge:
            mosi = (mosi << 1) | bit_at(samples[index], mosi_ch)
            miso = (miso << 1) | bit_at(samples[index], miso_ch)
            count += 1
            if count == 8:
                events.append(
                    DecodeEvent(index / sample_rate, "SPI", f"MOSI=0x{mosi:02X}", f"MISO=0x{miso:02X}")
                )
                count = 0
                mosi = 0
                miso = 0
    return events


def decode_i2c(samples: list[int], sample_rate: float, scl_ch: int, sda_ch: int) -> list[DecodeEvent]:
    """Decode basic I2C address/data bytes with ACK markers."""
    events: list[DecodeEvent] = []
    in_frame = False
    value = 0
    count = 0
    for index in range(1, len(samples)):
        old_scl = bit_at(samples[index - 1], scl_ch)
        new_scl = bit_at(samples[index], scl_ch)
        old_sda = bit_at(samples[index - 1], sda_ch)
        new_sda = bit_at(samples[index], sda_ch)

        if old_sda == 1 and new_sda == 0 and new_scl == 1:
            in_frame = True
            value = 0
            count = 0
            events.append(DecodeEvent(index / sample_rate, "I2C", "START", ""))
            continue
        if old_sda == 0 and new_sda == 1 and new_scl == 1:
            in_frame = False
            events.append(DecodeEvent(index / sample_rate, "I2C", "STOP", ""))
            continue
        if in_frame and old_scl == 0 and new_scl == 1:
            if count < 8:
                value = (value << 1) | new_sda
                count += 1
                if count == 8:
                    events.append(DecodeEvent(index / sample_rate, "I2C", f"0x{value:02X}", "byte"))
            else:
                events.append(DecodeEvent(index / sample_rate, "I2C", "ACK" if new_sda == 0 else "NAK", ""))
                value = 0
                count = 0
    return events

