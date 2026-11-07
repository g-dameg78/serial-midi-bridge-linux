# Serial MIDI to ALSA bridge (Linux)

A minimal, documented Linux bridge that reads ASCII MIDI events from a serial-connected microcontroller and exposes them through a virtual ALSA MIDI output.

**Origin:** Adapted from a personal ESP32-C5 wireless MIDI experiment tested on October 19, 2026. The original host route delivered real USB-keyboard Note On/Off events to a separate receiver. This is a **cleaned public adaptation** of the bridge, not the unmodified deployed script, and it has not yet been separately tested on physical hardware.

## Why this exists

Getting a device to enumerate is not enough. To prove a digital-MIDI pipeline, I needed to see actual keyboard events arrive at the receiver, decode the serial transport, forward MIDI messages, and verify that Note Off events were not lost.

The bridge does not flash firmware, write to a microcontroller, require private network credentials, or alter system-wide sound routing. It only opens the serial port you explicitly select and creates a virtual MIDI output.

## Event format

Expected one event per line, like:

```text
C5MIDI,42,90,60,100
C5MIDI,43,80,60,0
C5MIDI,44,B0,74,64
```

Format: `C5MIDI,<counter>,<status in hex>,<data1 decimal>,<data2 decimal>`.
Three-byte channel messages and two-byte Program Change/Channel Pressure are parsed. SysEx and clock/transport messages are intentionally out of scope for this simplified receiver protocol.

## Requirements

- Linux with ALSA sequencer
- Python 3.10+ and packages `pyserial`, `python-rtmidi`
- A microcontroller already emitting the documented serial event format

## Usage

```bash
python3 -m pip install -r requirements.txt
python3 bridge.py --device /dev/ttyACM0 --port-name "Serial BLE MIDI"
aconnect -l  # Find the virtual MIDI port and connect it to your own destination.
```

No connection to a particular synthesizer or sound server is created automatically. `Ctrl+C` attempts to send All Notes Off on every MIDI channel before closing. Hardware and MIDI port setup remain your responsibility.

## Offline tests

```bash
python3 -m unittest discover -s tests -v
```

Tests cover Note On/Off, controller messages, channel pressure, program change, malformed input, and unsupported MIDI statuses. They do not claim wireless latency or successful physical playback.

## Attribution and limitations

Prepared from work directed and tested on personal hardware; AI coding assistants contributed to some source and review tasks. This repo includes an improved, independently testable parser adapted from the original bridge script. The original hardware project and its private configs have **not** been uploaded.

No separate open-source license has been selected for this repository.
