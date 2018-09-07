#!/usr/bin/python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# SourceQuery - Python class for querying info from Source Dedicated Servers
# Copyright (c) 2012 Alex Kuhrt <alex@qrt.de>
# Copyright (c) 2010 Andreas Klauer <Andreas.Klauer@metamorpher.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#------------------------------------------------------------------------------

"""http://developer.valvesoftware.com/wiki/Server_Queries"""

# TODO: according to spec, packets may be bzip2 compressed.
#       not implemented yet because I couldn't find a server that does this.


import socket
import time

from buffer import SteamPacketBuffer
from server import Server
from packet import create_response, InfoRequest, ChallangeRequest, RulesRequest, PlayersRequest

PACKET_SIZE = 1400
PACKET_HEAD = -1
PACKET_SPLIT = -2

class SourceQuery:
    """
    Example usage:

    import SourceQuery
    server = SourceQuery.SourceQuery('1.2.3.4', 27015)
    print server.ping()
    print server.info()
    print server.players()
    print server.rules()
    """

    def __init__(self, host, port=27015, timeout=1):
        self.server = Server(socket.gethostbyname(host), port)
        self._timeout = timeout
        self._connect()

    def __del__(self):
        self._connection.close()

    def _connect(self):
        print(self.server)
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._connection.settimeout(self._timeout)
        self._connection.connect(self.server.as_tuple())

    def _receive(self, packet_buffer={}):
        packet = SteamPacketBuffer(self._connection.recv(PACKET_SIZE))
        packet_type = packet.read_long()

        if packet_type == PACKET_HEAD:
            return packet

        elif packet_type == PACKET_SPLIT:
            request_id = packet.read_long()  # TODO: compressed?

            if request_id not in packet_buffer:
                packet_buffer.setdefault(request_id, [])

            total_packets = packet.read_byte()
            current_packet_number = packet.read_byte()
            paket_size = packet.read_short()
            packet_buffer[request_id].insert(current_packet_number, packet.read())

            if current_packet_number == total_packets - 1:
                full_packet = PacketBuffer(b''.join(packet_buffer[request_id]))

                if full_packet.read_long() == PACKET_HEAD:
                    return full_packet
            else:
                return self._receive(packet_buffer)

    def _get_challenge(self):
        response = self._send(ChallangeRequest())
        if not response.is_valid():
            return None
        return response.raw

    def _send(self, package):
        timer_start = time.time()
        self._connection.send(package.as_bytes())
        result = self._receive()
        ping = round((time.time() - timer_start) * 1000, 2)
        Response = create_response(package.class_name())
        return Response(result, ping)

    def _decorate(func):
        def wrapper():
            r = func()
            return r
        return wrapper

    def ping(self):
        """Fake ping. Send three InfoRequets and calculate an average ping."""
        MAX_LOOPS = 3
        return round(sum(map(lambda ping: self.info()['server_ping'],
                             range(MAX_LOOPS))) / MAX_LOOPS, 2)

    @ _decorate
    def info(self):
        """Request basic server information."""
        response = self._send(InfoRequest())
        if not response.is_valid():
            return None
        result = response.result()
        result['server_ip'] = self.server.ip
        a = response.result()
        return result

    def players(self):
        response = self._send(PlayersRequest(self._get_challenge()))
        if not response.is_valid():
           return None
        return response.result()

    def rules(self):
        response = self._send(RulesRequest(self._get_challenge()))
        if not response.is_valid():
           return None
        return response.result()

if __name__ == '__main__':
    s = SourceQuery('steamcalculator.com')
    print(s.info())
    #print(s.ping())
    #print(s.rules())
    #print(s.players())
