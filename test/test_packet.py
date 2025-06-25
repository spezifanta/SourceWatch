import unittest
import SourceWatch


class TestInfoGoldSrcResponse(unittest.TestCase):
    def test_info_goldsrc_response_parsing(self):
        """Test InfoGoldSrcResponse correctly parses server info data."""
        # Given a buffer with mock GoldSrc server response data
        buffer = SourceWatch.buffer.SteamPacketBuffer()

        # Write test data to buffer (including header byte)
        buffer.write_byte(SourceWatch.packet.InfoGoldSrcResponse.RESPONSE_HEADER)
        buffer.write_string("192.168.1.1:27015")  # server_address
        buffer.write_string("Test GoldSrc Server")  # server_name
        buffer.write_string("de_dust2")  # game_map
        buffer.write_string("cstrike")  # game_directory
        buffer.write_string("Counter-Strike")  # game_title
        buffer.write_byte(16)  # players_current
        buffer.write_byte(32)  # players_max_slots
        buffer.write_byte(48)  # server_protocol_version
        buffer.write_byte(ord("d"))  # server_type (dedicated)
        buffer.write_byte(ord("l"))  # server_os (linux)
        buffer.write_byte(0)  # server_password_protected (false)
        buffer.write_byte(1)  # game_mod (true)
        buffer.write_byte(1)  # server_vac_secured (true)
        buffer.write_byte(2)  # players_bots

        # Reset buffer position to beginning for reading
        buffer.seek(0)

        # When creating InfoGoldSrcResponse with the buffer and ping time
        ping_time = 50.0  # Mock ping time in milliseconds
        response = SourceWatch.packet.InfoGoldSrcResponse(buffer, ping_time)
        result = response.result()

        # Then the parsed info should match our test data
        expected_info = {
            "server_address": "192.168.1.1:27015",
            "server_name": "Test GoldSrc Server",
            "game_map": "de_dust2",
            "game_directory": "cstrike",
            "game_title": "Counter-Strike",
            "players_current": 16,
            "players_max_slots": 32,
            "server_protocol_version": 48,
            "server_type": "d",
            "server_os": "l",
            "server_password_protected": 0,
            "game_mod": 1,
            "server_vac_secured": 1,
            "players_bots": 2,
            "players_humans": 16,  # same as players_current
            "players_free_slots": 16,  # max_slots - current
        }

        self.assertEqual(result["info"], expected_info)

    def test_info_goldsrc_response_multipackage(self):
        """Test InfoGoldSrcResponse with multipackage response reconstruction."""
        # Given a complete server response that needs to be split across packets
        # First create the complete response data
        complete_data = SourceWatch.buffer.SteamPacketBuffer()
        complete_data.write_string("192.168.1.1:27015")  # server_address
        complete_data.write_string("Test Multipackage Server")  # server_name
        complete_data.write_string("de_dust2")  # game_map
        complete_data.write_string("cstrike")  # game_directory
        complete_data.write_string("Counter-Strike")  # game_title
        complete_data.write_byte(10)  # players_current
        complete_data.write_byte(20)  # players_max_slots
        complete_data.write_byte(48)  # server_protocol_version
        complete_data.write_byte(ord("d"))  # server_type
        complete_data.write_byte(ord("l"))  # server_os
        complete_data.write_byte(0)  # password_protected
        complete_data.write_byte(1)  # game_mod
        complete_data.write_byte(1)  # vac_secured
        complete_data.write_byte(1)  # players_bots

        full_response_data = complete_data.getvalue()

        # Split the data into 3 fragments
        request_id = 12345
        total_packets = 3
        chunk_size = len(full_response_data) // total_packets

        fragments = []
        for i in range(total_packets):
            fragment = SourceWatch.buffer.SteamPacketBuffer()
            fragment.write_long(-2)  # MULTIPLE_PACKET_RESPONSE
            fragment.write_long(request_id)
            fragment.write_byte(total_packets)
            fragment.write_byte(i)  # current packet number
            fragment.write_short(100)  # packet size

            # Get the chunk for this fragment
            start = i * chunk_size
            if i == total_packets - 1:  # Last fragment gets remainder
                chunk = full_response_data[start:]
            else:
                chunk = full_response_data[start : start + chunk_size]

            fragment.write(chunk)
            fragments.append(fragment.getvalue())

        # When reassembling the multipackage response
        packet_buffer = {request_id: [None] * total_packets}

        for fragment_data in fragments:
            packet = SourceWatch.buffer.SteamPacketBuffer(fragment_data)
            response_format = packet.read_long()
            self.assertEqual(response_format, -2)  # MULTIPLE_PACKET_RESPONSE

            rid = packet.read_long()
            self.assertEqual(rid, request_id)

            packet.read_byte()  # total packets (not used)
            current = packet.read_byte()
            packet.read_short()  # packet size (not used)

            packet_buffer[rid][current] = packet.read()

        # Reconstruct the full packet
        reconstructed_data = b"".join(packet_buffer[request_id])

        # Create final buffer with the reconstructed data (including header)
        final_buffer = SourceWatch.buffer.SteamPacketBuffer()
        final_buffer.write_byte(SourceWatch.packet.InfoGoldSrcResponse.RESPONSE_HEADER)
        final_buffer.write(reconstructed_data)
        final_buffer.seek(0)

        # Then create InfoGoldSrcResponse with the reconstructed buffer
        ping_time = 75.0
        response = SourceWatch.packet.InfoGoldSrcResponse(final_buffer, ping_time)
        result = response.result()

        # Verify the reconstructed data was parsed correctly
        expected_info = {
            "server_address": "192.168.1.1:27015",
            "server_name": "Test Multipackage Server",
            "game_map": "de_dust2",
            "game_directory": "cstrike",
            "game_title": "Counter-Strike",
            "players_current": 10,
            "players_max_slots": 20,
            "server_protocol_version": 48,
            "server_type": "d",
            "server_os": "l",
            "server_password_protected": 0,
            "game_mod": 1,
            "server_vac_secured": 1,
            "players_bots": 1,
            "players_humans": 10,
            "players_free_slots": 10,
        }

        self.assertEqual(result["info"], expected_info)


if __name__ == "__main__":
    unittest.main()
