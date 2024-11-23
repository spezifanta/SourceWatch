import struct
import io


class SteamPacketBuffer(io.BytesIO):
    """In-memory byte buffer."""

    __NULL_BYTE = b"\x00"

    def __len__(self):
        return len(self.getvalue())

    def __repr__(self):
        return f"<SteamPacketBuffer: {len(self)}: {self.getvalue}>"

    def __str__(self):
        return str(self.getvalue())

    def read_byte(self):
        return struct.unpack("<B", self.read(1))[0]

    def write_byte(self, value):
        self.write(struct.pack("<B", value))

    def read_short(self):
        return struct.unpack("<h", self.read(2))[0]

    def write_short(self, value):
        self.write(struct.pack("<h", value))

    def read_float(self):
        return struct.unpack("<f", self.read(4))[0]

    def write_float(self, value):
        self.write(struct.pack("<f", value))

    def read_long(self):
        return struct.unpack("<l", self.read(4))[0]

    def write_long(self, value):
        self.write(struct.pack("<l", value))

    def read_long_long(self):
        return struct.unpack("<Q", self.read(8))[0]

    def write_long_long(self, value):
        self.write(struct.pack("<Q", value))

    def read_char(self):
        return chr(self.read_byte())

    def read_string(self):
        """Read a null-terminated UTF-8 encoded string from the buffer."""
        value = bytearray()
        while True:
            char = self.read(1)
            if not char or char == self.__NULL_BYTE:
                break
            value.extend(char)
        return value.decode("utf-8")

    def write_string(self, value):
        """Write a null-terminated UTF-8 encoded string to the buffer."""
        self.write(value.encode("utf-8") + self.__NULL_BYTE)
