"""Decode the C5MIDI serial event format used in a personal MIDI bridge.

No I/O: independent of a serial device, ALSA, or private configuration.
The device-side packet source and real-time MIDI are outside this module.
"""

from typing import Optional


def parse_midi_line(line: str) -> Optional[list[int]]:
    """Return one valid channel MIDI message, else None.

    Expected: C5MIDI,<counter>,<status_hex>,<data1>,<data2>
    Two-byte MIDI channel messages ignore data2, which is still present in
    the serial transport frame.
    """
    prefix = "C5MIDI,"
    if prefix not in line:
        return None
    fields = line.split(prefix, 1)[1].strip().split(",")
    if len(fields) < 4:
        return None
    try:
        # Counter is metadata; must be numeric to reject corrupt frames.
        int(fields[0], 10)
        status = int(fields[1], 16)
        d1 = int(fields[2], 10)
        d2 = int(fields[3], 10)
    except (ValueError, IndexError):
        return None

    if not (0x80 <= status <= 0xEF):
        return None
    if not (0 <= d1 <= 127 and 0 <= d2 <= 127):
        return None

    kind = status & 0xF0
    if kind in (0xC0, 0xD0):  # Program Change, Channel Pressure
        return [status, d1]
    return [status, d1, d2]
