import io
import struct
import importlib

from buffer import SteamPacketBuffer

def create_response(request_class_name):
    """Create a ResponsePackage instance from a RequestPackage class name."""
    name = request_class_name[:-len('Request')]
    ResponseClass = globals()['{}Response'.format(name)]
    return ResponseClass


class BasePackage:
    def __init__(self):
      self._buffer = SteamPacketBuffer()
      self._header = None


class RequestPackage(BasePackage):
    PACKAGE_HEADER = -1

    def __init__(self, challange=None):
        super(RequestPackage, self).__init__()
        self._challange = challange
        self._buffer.write_long(self.PACKAGE_HEADER)
        self._buffer.write_byte(self.REQUEST_HEADER)
        if 'REQUEST_PAYLOAD' in dir(self):
            self._buffer.write_string(self.REQUEST_PAYLOAD)
        if self._challange:
            self._buffer.write_long(self._challange)

    def as_bytes(self):
        return self._buffer.getvalue()

    def class_name(self):
        return self.__class__.__name__


class ResponsePackage(BasePackage):
    def __init__(self, buffer, ping):
        super(ResponsePackage, self).__init__()
        self._buffer = buffer
        self._ping = ping
        self._result = None

    def is_valid(self):
        return self.header == self.RESPONSE_HEADER

    @property
    def header(self):
        if self._header is None:
            self._header = self._buffer.read_byte()
        return self._header

    def result(self):
        """Change stream position back to the beginning."""
        self._buffer.seek(0)
        return self._result


class InfoRequest(RequestPackage):
    REQUEST_HEADER = 0x54
    REQUEST_PAYLOAD = 'Source Engine Query'


class InfoResponse(ResponsePackage):
    RESPONSE_HEADER = 0x49

    def result(self):
        self._result = {
            'server_protocol_version': self._buffer.read_byte(),
            'server_name': self._buffer.read_string(),
            'game_map': self._buffer.read_string(),
            'game_directory': self._buffer.read_string(),
            'game_description': self._buffer.read_string(),
            'game_app_id': self._buffer.read_short(),
            'players_current':  self._buffer.read_byte(),
            'players_max': self._buffer.read_byte(),
            'players_bot': self._buffer.read_byte(),
            'server_type': chr(self._buffer.read_byte()),
            'server_os': chr(self._buffer.read_byte()),
            'server_password_protected': self._buffer.read_byte(),
            'server_vac_secured': self._buffer.read_byte(),
            'game_version': self._buffer.read_string()
        }

        try:
            extra_data_flags = self._buffer.read_byte()
        except:
            pass
        else:
            if extra_data_flags & 0x80:
                self._result['server_port'] = self._buffer.read_short()
            if extra_data_flags & 0x10:
                self._result['server_steam_id'] = self._buffer.read_long_long()
            if extra_data_flags & 0x40:
                self._result['server_spectator_port'] = self._buffer.read_short()
                self._result['server_spectator_name'] = self._buffer.read_string()
            if extra_data_flags & 0x20:
                self._result['server_tags'] = self._buffer.read_string()
            if extra_data_flags & 0x01:
                """A more accurate AppID as the earlier appID could have benn truncated as it was forced into 16-bit storage"""
                self._result['game_app_id'] = self._buffer.read_long_long()
        finally:
            self._result['server_ping'] = self._ping
            self._result['players_human'] = self._result['players_current'] - self._result['players_bot']

        return super(InfoResponse, self).result()


class ChallangeRequest(RequestPackage):
    REQUEST_HEADER = 0x56
    REQUEST_CHALLANGE = -1

    def __init__(self):
        super(ChallangeRequest, self).__init__(self.REQUEST_CHALLANGE)



class ChallangeResponse(ResponsePackage):
    RESPONSE_HEADER = 0x41

    @property
    def raw(self):
        return self._buffer.read_long()


class RulesRequest(RequestPackage):
    REQUEST_HEADER = 0x56


class RulesResponse(ResponsePackage):
    RESPONSE_HEADER = 0x45

    def result(self):
        total_rules = self._buffer.read_short()
        for _ in range(total_rules):
            key = self._buffer.read_string()
            value = self._buffer.read_string()
            self._result.setdefault(key, value)
        return super(RulesResponse, self).result()


class PlayersRequest(RequestPackage):
    REQUEST_HEADER = 0x55


class PlayersResponse(ResponsePackage):
    RESPONSE_HEADER = 0x44

    def result(self):
        total_players = self._buffer.read_byte()
        players = []
        for _ in range(total_players):
            player = {
                'id': self._buffer.read_byte(),
                'name': self._buffer.read_string(),
                'kills': self._buffer.read_long(),
                'playtime': self._buffer.read_float()
            }
            players.append(player)
        self._result = players
        return super(PlayersResponse, self).result()
