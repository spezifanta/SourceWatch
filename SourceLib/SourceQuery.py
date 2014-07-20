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

from packet import PacketBuffer
from server import Server

PACKET_SIZE = 1400
PACKET_HEAD = -1
PACKET_SPLIT = -2


class PacketType:
    Info, Challenge, Players, Rules = range(4)


class RequestType:
    Info = 'TSource Engine Query'
    Challenge = -1
    Players = 0x55
    Rules = 0x56


class ResponseType:
    Info = 0x49
    Challenge = 0x41
    Players = 0x44
    Rules = 0x45


class PacketFactory:
    def create(packet_type):
        packet = PacketBuffer()
        packet.put_long(PACKET_HEAD)

        if packet_type == PacketType.Info:
            packet.put_string(RequestType.Info)
        elif packet_type == PacketType.Challenge:
            packet.put_byte(RequestType.Players)
            packet.put_long(RequestType.Challenge)
        elif packet_type == PacketType.Players:
            packet.put_byte(RequestType.Players)
        elif packet_type == PacketType.Rules:
            packet.put_byte(RequestType.Rules)
        else:
            return None

        return packet


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
        self._challenge = RequestType.Challenge
        self._connect()

    def __del__(self):
        self._connection.close()

    def _connect(self):
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._connection.settimeout(self._timeout)
        self._connection.connect(self.server.as_tuple())

    def _query(self, packet, challenge=False):
        if challenge:
            packet.put_long(self._get_challenge())

        self._connection.send(packet.getvalue())
        return self._receive()

    def _receive(self, packet_buffer={}):
        packet = PacketBuffer(self._connection.recv(PACKET_SIZE))
        packet_type = packet.get_long()

        if packet_type == PACKET_HEAD:
            return packet

        elif packet_type == PACKET_SPLIT:
            request_id = packet.get_long()  # TODO: compressed?

            if request_id not in packet_buffer:
                packet_buffer.setdefault(request_id, [])

            total_packets = packet.get_byte()
            current_packet_number = packet.get_byte()
            paket_size = packet.get_short()
            packet_buffer[request_id].insert(current_packet_number, packet.read())

            if current_packet_number == total_packets - 1:
                full_packet = PacketBuffer(b''.join(packet_buffer[request_id]))

                if full_packet.get_long() == PACKET_HEAD:
                    return full_packet
            else:
                return self._receive(packet_buffer)

    def _get_challenge(self):
        if self._challenge != RequestType.Challenge:
            return self._challenge

        packet = self._query(PacketFactory.create(PacketType.Challenge))

        if packet.get_byte() == ResponseType.Challenge:
            self._challenge = packet.get_long()
            return self._challenge

    def ping(self):
        MAX_LOOPS = 3
        return round(sum(map(lambda ping: self.info()['ping'],
                             range(MAX_LOOPS))) / MAX_LOOPS, 2)


    def info(self):
        timer_start = time.time()
        packet = self._query(PacketFactory.create(PacketType.Info))
        timer_end = time.time()

        if packet.get_byte() == ResponseType.Info:
            result = {
                'protocol_version': packet.get_byte(),
                'server_name': packet.get_string(),
                'game_map': packet.get_string(),
                'game_directory': packet.get_string(),
                'game_description': packet.get_string(),
                'game_app_id': packet.get_short(),
                'players_current':  packet.get_byte(),
                'players_max': packet.get_byte(),
                'players_bot': packet.get_byte(),
                'server_type': chr(packet.get_byte()),
                'server_os': chr(packet.get_byte()),
                'password': packet.get_byte(),
                'secure': packet.get_byte(),
                'game_version': packet.get_string()
            }

            try:
                result['extra_data_flag'] = packet.get_byte()
            except:
                pass
            else:
                if result['extra_data_flag'] & 0x80:
                    result['server_port'] = packet.get_short()
                if result['extra_data_flag'] & 0x10:
                    result['server_steam_id'] = packet.get_long_long()
                if result['extra_data_flag'] & 0x40:
                    result['server_spectator_port'] = packet.get_short()
                    result['server_spectator_name'] = packet.get_string()
                if result['extra_data_flag'] & 0x20:
                    result['server_tags'] = packet.get_string()
                if result['extra_data_flag'] & 0x01:
                    result['server_game_id'] = packet.get_long_long()
            finally:
                result['server_ip'] =  self.server.ip
                result['ping'] = round((timer_end - timer_start) * 1000, 2)
                result['players_human'] = result['players_current'] \
                                          - result['players_bot']
                return result

    def players(self):
        packet = self._query(PacketFactory.create(PacketType.Players), True)

        if packet.get_byte() == ResponseType.Players:
            total_players = packet.get_byte()
            player_list = []

            for i in range(total_players):
                player = {
                    'index': packet.get_byte(),
                    'name': packet.get_string(),
                    'kills': packet.get_long(),
                    'playtime': packet.get_float()
                }
                player_list.append(player)

            return player_list

    def rules(self):
        packet = self._query(PacketFactory.create(PacketType.Rules), True)

        if packet.get_byte() == ResponseType.Rules:
            rules = {}
            total_rules = packet.get_short()

            for i in range(total_rules):
                rules.setdefault(packet.get_string(), packet.get_string())

            return rules
