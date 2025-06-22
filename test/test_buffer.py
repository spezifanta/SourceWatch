import unittest
import SourceWatch


class TestBuffer(unittest.TestCase):
    def setUp(self):
        self.buffer = SourceWatch.buffer.SteamPacketBuffer()

    def test_char(self):
        """Ensure single ASCII characters round-trip correctly."""
        # Given a character which we want to write to the buffer
        message = "A"
        self.buffer.write_char(message)

        # When reading the buffer from the beginning...
        self.buffer.seek(0)
        decoded = self.buffer.read_char()

        # Then the message from the buffer should match our original character.
        self.assertEqual(message, decoded)

    def test_byte(self):
        # Given a message which we want to write to the buffer
        message = 0
        self.buffer.write_byte(message)

        # When reading the buffer from the beginning...
        self.buffer.seek(0)
        decoded = self.buffer.read_byte()

        # Than the message from the buffer should match our original message.
        self.assertEqual(message, decoded)

    def test_short(self):
        # Given a message which we want to write to the buffer
        message = 32767
        self.buffer.write_short(message)

        # When reading the buffer from the beginning...
        self.buffer.seek(0)
        decoded = self.buffer.read_short()

        # Than the message from the buffer should match our original message.
        self.assertEqual(message, decoded)

    def test_float(self):
        # Given a message which we want to write to the buffer
        message = 1.23456789
        self.buffer.write_float(message)

        # When reading the buffer from the beginning...
        self.buffer.seek(0)
        decoded = self.buffer.read_float()

        # Than the message from the buffer should almost match our original message.
        self.assertAlmostEqual(message, decoded, 7)

    def test_long(self):
        # Given a message which we want to write to the buffer
        message = 2147483647
        self.buffer.write_long(message)

        # When reading the buffer from the beginning...
        self.buffer.seek(0)
        decoded = self.buffer.read_long()

        # Than the message from the buffer should match our original message.
        self.assertEqual(message, decoded)

    def test_long_long(self):
        # Given a message which we want to write to the buffer
        message = 18446744073709551615
        self.buffer.write_long_long(message)

        # When reading the buffer from the beginning...
        self.buffer.seek(0)
        decoded = self.buffer.read_long_long()

        # Than the message from the buffer should match our original message.
        self.assertEqual(message, decoded)

    def test_string(self):
        # Given a message which we want to write to the buffer
        message = "This is a test payload. 𝑯äḽϝ-ℒᶖ𝚏é Ṽẩᶅ𝞶ẹ 𝐒𝓸𝒻𝝉ware"
        self.buffer.write_string(message)

        # When reading the buffer from the beginning...
        self.buffer.seek(0)
        decoded = self.buffer.read_string()

        # Than the message from the buffer should match our original message.
        self.assertEqual(message, decoded)
