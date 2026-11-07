#!/usr/bin/env python3
"""Public-safe serial event -> Linux virtual MIDI port adapter.

Adapted/refactored from a personal BOSS/ANTEROS serial-to-ALSA bridge.
No firmware flashing or automatic ALSA port connection.
"""

import argparse
import signal
import time

from midi_line import parse_midi_line

_running = True


def _stop(*_args):
    global _running
    _running = False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", required=True, help="Explicit serial path, e.g. /dev/ttyACM0")
    parser.add_argument("--port-name", default="Serial BLE MIDI", help="Name for virtual ALSA output")
    args = parser.parse_args()

    # Import hardware dependencies only after arguments have been checked.
    import serial
    import rtmidi

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    midi = rtmidi.MidiOut(rtmidi.API_LINUX_ALSA)
    midi.open_virtual_port(args.port_name)
    count, malformed = 0, 0

    try:
        while _running:
            try:
                port = serial.Serial()
                port.port = args.device
                port.baudrate = 115200
                port.timeout = 0.3
                port.dtr = False
                port.rts = False
                try:
                    port.open()
                    print("SERIAL_OPEN", flush=True)
                    while _running:
                        line = port.readline().decode("ascii", errors="ignore").strip()
                        if "C5MIDI," not in line:
                            continue
                        event = parse_midi_line(line)
                        if event is None:
                            malformed += 1
                            continue
                        midi.send_message(event)
                        count += 1
                        if count <= 8 or count % 100 == 0:
                            print(f"MIDI_FORWARDED total={count}", flush=True)
                finally:
                    if port.is_open:
                        port.close()
            except (serial.SerialException, OSError) as exc:
                print(f"SERIAL_RECOVERING error_type={type(exc).__name__}", flush=True)
                if _running:
                    time.sleep(2)
    finally:
        try:
            # Best-effort panic for a dropped Note Off or connection.
            for channel in range(16):
                midi.send_message([0xB0 | channel, 123, 0])
        finally:
            midi.close_port()
    print(f"BRIDGE_EXIT forwarded={count} malformed={malformed}", flush=True)


if __name__ == "__main__":
    main()
