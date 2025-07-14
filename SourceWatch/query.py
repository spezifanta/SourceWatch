# See: http://developer.valvesoftware.com/wiki/Server_Queries
#
# TODO: according to spec, packets may be bzip2 compressed.
#       not implemented yet because I couldn't find a server that does this.


import logging
import socket
import time
from .buffer import SteamPacketBuffer
from .server import Server
from .packet import (
    ChallengeRequest,
    Challengeable,
    InfoRequest,
    PlayersRequest,
    RulesRequest,
    SourceWatchError,
    create_response,
)
from .models import (
    InfoResponseModel,
    PlayersResponseModel,
    RulesResponseModel,
    BasicServerModel,
)

PACKET_SIZE = 1400
SINGLE_PACKET_RESPONSE = -1
MULTIPLE_PACKET_RESPONSE = -2


class Query:
    """
    Example usage:

    import SourceWatch
    server = SourceWatch.Query('1.2.3.4', 27015)
    print(server.ping())
    print(server.info())
    print(server.players())
    print(server.rules())
    """

    def __init__(self, host, port=27015, timeout=10):
        self.logger = logging.getLogger("SourceWatch")
        self.server = Server(socket.gethostbyname(host), port)
        self._timeout = timeout
        self._connect()

    def __del__(self):
        self._connection.close()

    def _connect(self):
        self.logger.info("Connecting to %s", self.server)
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._connection.settimeout(self._timeout)
        self._connection.connect(self.server.as_tuple())

    def _reconnect(self):
        """Reconnect to ensure fresh connection state"""
        self._connection.close()
        self._connect()

    def _receive(self, packet_buffer=None):
        response = self._connection.recv(PACKET_SIZE)
        self.logger.debug("Received: %s", response)
        packet = SteamPacketBuffer(response)
        response_format = packet.read_long()

        if response_format == SINGLE_PACKET_RESPONSE:
            self.logger.debug("Single packet response")
            return packet

        elif response_format == MULTIPLE_PACKET_RESPONSE:
            self.logger.debug("Multiple packet response")
            request_id = packet.read_long()  # TODO: compressed?

            if packet_buffer is None:
                packet_buffer = {}

            if request_id not in packet_buffer:
                packet_buffer[request_id] = []

            total_packets = packet.read_byte()
            current_packet_number = packet.read_byte()
            packet_size = packet.read_short()
            payload = packet.read()

            # Validate packet size matches what we received
            if len(payload) != packet_size:
                self.logger.warning(
                    "Packet size mismatch: expected %d, got %d",
                    packet_size,
                    len(payload),
                )

            packet_buffer[request_id].insert(current_packet_number, payload)

            if current_packet_number == total_packets - 1:
                full_packet = SteamPacketBuffer(b"".join(packet_buffer[request_id]))

                if full_packet.read_long() == SINGLE_PACKET_RESPONSE:
                    return full_packet
            else:
                return self._receive(packet_buffer)
        else:
            self.logger.error("Received invalid response type: %s", response_format)
            raise SourceWatchError("Received invalid response type")

    def _get_challenge(self):
        response = self._send(ChallengeRequest())
        response.is_valid()
        return response.raw

    def _send(self, packet):
        if isinstance(packet, Challengeable):
            # Reconnect to ensure fresh state for challenge-based queries
            self._reconnect()
            challenge = self._get_challenge()
            self.logger.debug("Using challenge: %s", challenge)
            packet.challenge = challenge

        self.logger.debug("Sending packet: %s", packet)
        timer_start = time.time()
        self.logger.debug("packet: %s", packet.as_bytes())
        self._connection.send(packet.as_bytes())
        result = self._receive()
        response_type = result.read_byte()
        # Reset buffer position and skip reading the request format.
        result.seek(0)
        result.read_long()
        ping = round((time.time() - timer_start) * 1000, 2)

        return create_response(response_type, result, ping)

    def request(request):
        def wrapper(self):
            response = request(self)
            result = response.result()
            if result is not None:
                result["server"] = {
                    "ip": self.server.ip,
                    "port": self.server.port,
                    "ping": response.ping,
                }
            return result

        return wrapper

    def ping(self, num_requests=3) -> BasicServerModel:
        """Fake ping request. Send three InfoRequests and calculate an average ping."""
        self.logger.info("Sending fake ping request")

        def fetch_ping(_):
            return self.info().get("server").get("ping")

        total = sum(map(fetch_ping, range(num_requests)))
        average = round(total / num_requests, 2)
        return average

    @request
    def info(self) -> InfoResponseModel:
        """Request basic server information."""
        self.logger.info("Sending info request")
        return self._send(InfoRequest())

    @request
    def players(self) -> PlayersResponseModel:
        """Request players."""
        self.logger.info("Sending players request")
        return self._send(PlayersRequest())

    @request
    def rules(self) -> RulesResponseModel:
        """Request server rules."""
        self.logger.info("Sending rules request")
        return self._send(RulesRequest())
