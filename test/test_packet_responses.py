import unittest
import SourceWatch
from SourceWatch import buffer as buf_mod
from SourceWatch import packet

class TestPacketResponses(unittest.TestCase):
    def _make_info_packet(self):
        b = buf_mod.SteamPacketBuffer()
        b.write_long(-1)  # SINGLE_PACKET_RESPONSE
        b.write_byte(packet.InfoResponse.RESPONSE_HEADER)
        b.write_byte(17)  # server protocol version
        b.write_string('Test Server')
        b.write_string('test_map')
        b.write_string('test_dir')
        b.write_string('Test Game')
        b.write_short(10)
        b.write_byte(1)
        b.write_byte(10)
        b.write_byte(0)
        b.write_char('d')
        b.write_char('l')
        b.write_byte(0)
        b.write_byte(1)
        b.write_string('1.0')
        b.write_byte(0)  # no extra data flags
        # mimic Query._send behaviour
        b.seek(0)
        b.read_long()
        return b

    def test_info_response_parsing(self):
        buf = self._make_info_packet()
        resp = packet.InfoResponse(buf, 0)
        data = resp.result()
        self.assertEqual(data['info']['server_name'], 'Test Server')
        self.assertEqual(data['info']['server_type'], 'd')
        self.assertEqual(data['info']['server_os'], 'l')

