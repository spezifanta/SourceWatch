import struct
from .buffer import SteamPacketBuffer


class SourceWatchError(Exception):
    pass


def create_response(request_type: int, *args) -> "ResponsePacket":
    """Create a ResponsePacket instance from a RequestPacket class name."""
    if request_type == InfoResponse.RESPONSE_HEADER:
        ResponsePacket = InfoResponse
    elif request_type == InfoGoldSrcResponse.RESPONSE_HEADER:
        ResponsePacket = InfoGoldSrcResponse
    elif request_type == PlayersResponse.RESPONSE_HEADER:
        ResponsePacket = PlayersResponse
    elif request_type == RulesResponse.RESPONSE_HEADER:
        ResponsePacket = RulesResponse
    elif request_type == ChallengeResponse.RESPONSE_HEADER:
        ResponsePacket = ChallengeResponse
    else:
        raise SourceWatchError("Unknown response type", request_type)

    return ResponsePacket(*args)


class Challengeable:
    """Flag a Packet to request a challenge."""

    pass


class BasePacket:
    def __init__(self):
        self._buffer = SteamPacketBuffer()
        self._header = None

    def __repr__(self):
        return f"<{self.class_name()}> buffer:{self._buffer.getvalue()}"

    def class_name(self):
        return self.__class__.__name__


class RequestPacket(BasePacket):
    PACKET_HEADER = -1

    def __init__(self):
        super().__init__()
        self._buffer.write_long(self.PACKET_HEADER)
        self._buffer.write_byte(self.REQUEST_HEADER)
        self._challenge = None

    def as_bytes(self):
        return self._buffer.getvalue()

    @property
    def challenge(self):
        return self._challenge

    @challenge.setter
    def challenge(self, value):
        self._challenge = value
        self._buffer.write_long(value)


class ResponsePacket(BasePacket):
    def __init__(self, buffer, ping):
        super().__init__()
        self._buffer = buffer
        self._ping = ping
        self._result = None
        self.header = self._buffer.read_byte()

    def is_valid(self):
        return self.header == self.RESPONSE_HEADER

    @property
    def ping(self):
        return self._ping

    def result(self):
        """Change stream position back to the beginning."""
        self._buffer.seek(0)
        return self._result


class InfoRequest(RequestPacket):
    REQUEST_HEADER = 0x54
    REQUEST_PAYLOAD = "Source Engine Query"

    def __init__(self):
        super().__init__()
        self._buffer.write_string(self.REQUEST_PAYLOAD)


class InfoResponse(ResponsePacket):
    RESPONSE_HEADER = 0x49  # 0x6D  Counter-Strike 1.6

    def result(self):
        info = {
            "server_protocol_version": self._buffer.read_byte(),
            "server_name": self._buffer.read_string(),
            "game_map": self._buffer.read_string(),
            "game_directory": self._buffer.read_string(),
            "game_title": self._buffer.read_string(),
            "game_app_id": self._buffer.read_short(),
            "players_current": self._buffer.read_byte(),
            "players_max_slots": self._buffer.read_byte(),
            "players_bots": self._buffer.read_byte(),
            "server_type": self._buffer.read_char(),
            "server_os": self._buffer.read_char(),
            "server_password_protected": self._buffer.read_byte(),
            "server_vac_secured": self._buffer.read_byte(),
            "game_version": self._buffer.read_string(),
        }

        try:
            extra_data_flags = self._buffer.read_byte()
        except (IndexError, struct.error):
            # No extra data flags available. skip the rest.
            pass
        else:
            if extra_data_flags & 0x80:
                info["server_port"] = self._buffer.read_short()
            if extra_data_flags & 0x10:
                info["server_steam_id"] = self._buffer.read_long_long()
            if extra_data_flags & 0x40:
                info["server_spectator_port"] = self._buffer.read_short()
                info["server_spectator_name"] = self._buffer.read_string()
            if extra_data_flags & 0x20:
                info["server_tags"] = self._buffer.read_string()
            if extra_data_flags & 0x01:
                # A more accurate AppID as the earlier appID could have been truncated.
                info["game_app_id"] = self._buffer.read_long_long()
        finally:
            info["players_humans"] = info["players_current"] - info["players_bots"]
            info["players_free_slots"] = (
                info["players_max_slots"] - info["players_current"]
            )

        return {"info": info}


class InfoGoldSrcResponse(ResponsePacket):
    RESPONSE_HEADER = 0x6D

    def result(self):
        info = {
            "server_address": self._buffer.read_string(),
            "server_name": self._buffer.read_string(),
            "game_map": self._buffer.read_string(),
            "game_directory": self._buffer.read_string(),
            "game_title": self._buffer.read_string(),
            "players_current": self._buffer.read_byte(),
            "players_max_slots": self._buffer.read_byte(),
            "server_protocol_version": self._buffer.read_byte(),
            "server_type": chr(self._buffer.read_byte()),
            "server_os": chr(self._buffer.read_byte()),
            "server_password_protected": self._buffer.read_byte(),
            "game_mod": self._buffer.read_byte(),
            "server_vac_secured": self._buffer.read_byte(),
            "players_bots": self._buffer.read_byte(),
        }

        # TODO handle non-Mod

        info["players_humans"] = info["players_current"]
        info["players_free_slots"] = info["players_max_slots"] - info["players_current"]

        return {"info": info}


class ChallengeRequest(RequestPacket):
    REQUEST_HEADER = 0x56
    REQUEST_CHALLENGE = -1

    def __init__(self):
        super().__init__()
        self.challenge = self.REQUEST_CHALLENGE


class ChallengeResponse(ResponsePacket):
    RESPONSE_HEADER = 0x41

    @property
    def raw(self):
        self._buffer.seek(0)
        self._buffer.read_long()
        self._buffer.read_byte()
        return self._buffer.read_long()


class RulesRequest(RequestPacket, Challengeable):
    REQUEST_HEADER = 0x56


class RulesResponse(ResponsePacket):
    RESPONSE_HEADER = 0x45

    def result(self):
        rules = {}
        total_rules = self._buffer.read_short()
        for _ in range(total_rules):
            key = self._buffer.read_string()
            value = self._buffer.read_string()
            rules[key] = value
        return {"rules": rules}


class PlayersRequest(RequestPacket, Challengeable):
    REQUEST_HEADER = 0x55


class PlayersResponse(ResponsePacket):
    RESPONSE_HEADER = 0x44

    def result(self):
        total_players = self._buffer.read_byte()
        players = []
        for i in range(total_players):
            player = {
                "index": i,
                "id": self._buffer.read_byte(),
                "name": self._buffer.read_string(),
                "kills": self._buffer.read_long(),
                "play_time": self._buffer.read_float(),
            }
            players.append(player)
        return {"players": players}
