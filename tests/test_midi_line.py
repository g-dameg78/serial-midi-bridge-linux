import unittest

from midi_line import parse_midi_line


class MidiParserTests(unittest.TestCase):
    def test_note_on(self):
        self.assertEqual(parse_midi_line("C5MIDI,42,90,60,100"), [0x90, 60, 100])

    def test_note_off(self):
        self.assertEqual(parse_midi_line("C5MIDI,43,80,60,0"), [0x80, 60, 0])

    def test_control_change(self):
        self.assertEqual(parse_midi_line("C5MIDI,44,B3,74,64"), [0xB3, 74, 64])

    def test_program_change_two_bytes(self):
        self.assertEqual(parse_midi_line("C5MIDI,10,C0,12,0"), [0xC0, 12])

    def test_channel_pressure_two_bytes(self):
        self.assertEqual(parse_midi_line("C5MIDI,10,D1,99,0"), [0xD1, 99])

    def test_pitch_bend(self):
        self.assertEqual(parse_midi_line("C5MIDI,10,E0,1,127"), [0xE0, 1, 127])

    def test_missing_prefix(self):
        self.assertIsNone(parse_midi_line("ordinary status log"))

    def test_missing_fields(self):
        self.assertIsNone(parse_midi_line("C5MIDI,11,90,60"))

    def test_bad_counter(self):
        self.assertIsNone(parse_midi_line("C5MIDI,broken,90,60,90"))

    def test_bad_hex(self):
        self.assertIsNone(parse_midi_line("C5MIDI,11,Z0,60,90"))

    def test_bad_data(self):
        self.assertIsNone(parse_midi_line("C5MIDI,11,90,128,90"))

    def test_sysex_ignored(self):
        self.assertIsNone(parse_midi_line("C5MIDI,11,F0,60,90"))

    def test_midi_clock_ignored(self):
        self.assertIsNone(parse_midi_line("C5MIDI,11,F8,0,0"))

    def test_channel_16(self):
        self.assertEqual(parse_midi_line("C5MIDI,11,9F,66,127"), [0x9F, 66, 127])


if __name__ == "__main__":
    unittest.main()
