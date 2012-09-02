#!/usr/bin/python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# SourceQuery - Python class for querying info from Source Dedicated Servers
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
import io
import struct
import time

PACKET_SIZE = 1400
PACKET_HEAD = -1
PACKET_SPLIT = -2

A2S_INFO = ord('T')
A2S_INFO_STRING = 'Source Engine Query'
A2S_INFO_REPLY = ord('I')
A2S_PLAYER = ord('U')
A2S_PLAYER_REPLY = ord('D')
A2S_RULES = ord('V')
A2S_RULES_REPLY = ord('E')
EMPTY_CHALLENGE = -1
S2C_CHALLENGE = ord('A')


class SourceQueryPacket(io.BytesIO):
    def putByte(self, value):
        self.write(struct.pack('<B', value))

    def getByte(self):
        return struct.unpack('<B', self.read(1))[0]

    def putShort(self, value):
        self.write(struct.pack('<h', value))

    def getShort(self):
        return struct.unpack('<h', self.read(2))[0]

    def putLong(self, value):
        self.write(struct.pack('<l', value))

    def getLong(self):
        return struct.unpack('<l', self.read(4))[0]

    def getLongLong(self):
        return struct.unpack('<Q', self.read(8))[0]

    def putFloat(self, value):
        self.write(struct.pack('<f', value))

    def getFloat(self):
        return struct.unpack('<f', self.read(4))[0]

    def putString(self, value):
        self.write(bytearray('{0}\x00'.format(value), 'utf-8'))

    def getString(self):
        value = []
        while True:
            char = self.read(1)
            if char == b'\x00':
                break
            else:
                value.append(char)
        return ''.join(map(lambda c: chr(ord(c)), value))


class PacketType:
    Info, Challenge, Players, Rules = range(4)


class PacketFactory:
    def create(packet_type):
        packet = SourceQueryPacket()
        packet.putLong(PACKET_HEAD)

        if packet_type == PacketType.Info:
            packet.putByte(A2S_INFO)
            packet.putString(A2S_INFO_STRING)
        elif packet_type == PacketType.Challenge:
            packet.putByte(A2S_PLAYER)
            packet.putLong(PACKET_HEAD)
        elif packet_type == PacketType.Players:
            packet.putByte(A2S_PLAYER)
        elif packet_type == PacketType.Rules:
            packet.putByte(A2S_RULES)
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

    def __init__(self, host, port=27015, timeout=1.0):
        self.server = (host, port)
        self.timeout = timeout
        self.challenge = EMPTY_CHALLENGE
        self.connect()

    def __del__(self):
        self.udp.close()

    def connect(self):
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.settimeout(self.timeout)
        self.udp.connect(self.server)

    def query(self, packet, challenge=False):
        if challenge:
            packet.putLong(self.get_challenge())

        self.udp.send(packet.getvalue())
        return self.receive()

    def receive(self, packet_buffer={}):
        packet = SourceQueryPacket(self.udp.recv(PACKET_SIZE))
        packet_type = packet.getLong()

        if packet_type == PACKET_HEAD:
            return packet

        elif packet_type == PACKET_SPLIT:
            request_id = packet.getLong() # compressed?

            if request_id not in packet_buffer:
                packet_buffer.setdefault(request_id, [])

            total_packets = packet.getByte()
            current_packet_number = packet.getByte()
            paket_size = packet.getShort()
            packet_buffer[request_id].insert(current_packet_number, packet.read())

            if current_packet_number == total_packets - 1:
                full_packet = SourceQueryPacket(b''.join(packet_buffer[request_id]))

                if full_packet.getLong() == PACKET_HEAD:
                    return full_packet
            else:
                return self.receive(packet_buffer)

    def get_challenge(self):
        if self.challenge != EMPTY_CHALLENGE:
            return self.challenge

        packet = self.query(PacketFactory.create(PacketType.Challenge))

        if packet.getByte() == S2C_CHALLENGE:
            self.challenge = packet.getLong()
            return self.challenge

    def ping(self):
        return self.info()['ping']

    def info(self):
        timer_start = time.time()
        packet = self.query(PacketFactory.create(PacketType.Info))
        timer_end = time.time()

        if packet.getByte() == A2S_INFO_REPLY:
            result = {
                'ping': timer_end - timer_start,
                'network_version': packet.getByte(),
                'hostname': packet.getString(),
                'map': packet.getString(),
                'gamedir': packet.getString(),
                'gamedesc': packet.getString(),
                'appid': packet.getShort(),
                'numplayers':  packet.getByte(),
                'maxplayers': packet.getByte(),
                'numbots': packet.getByte(),
                'dedicated': chr(packet.getByte()),
                'os': chr(packet.getByte()),
                'passworded': packet.getByte(),
                'secure': packet.getByte(),
                'version': packet.getString()
            }

            try:
                edf = packet.getByte()
                result['edf'] = edf
            except:
                pass
            else:
                if edf & 0x80:
                    result['port'] = packet.getShort()
                if edf & 0x10:
                    result['steamid'] = packet.getLongLong()
                if edf & 0x40:
                    result['specport'] = packet.getShort()
                    result['specname'] = packet.getString()
                if edf & 0x20:
                    result['tag'] = packet.getString()
                if edf & 0x01:
                    result['game_id'] = packet.getLongLong()
            finally:
                return result

    def players(self):
        packet = self.query(PacketFactory.create(PacketType.Players), True)

        if packet.getByte() == A2S_PLAYER_REPLY:
            total_players = packet.getByte()
            player_list = []

            for i in range(total_players):
                player = {
                    'index': packet.getByte(),
                    'name': packet.getString(),
                    'kills': packet.getLong(),
                    'time': packet.getFloat()
                }
                player_list.append(player)

            return player_list

    def rules(self):
        packet = self.query(PacketFactory.create(PacketType.Rules), True)

        if packet.getByte() == A2S_RULES_REPLY:
            rules = {}
            total_rules = packet.getShort()

            for i in range(total_rules):
                rules.setdefault(packet.getString(), packet.getString())

            return rules
