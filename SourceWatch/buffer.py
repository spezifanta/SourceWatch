import struct
import io


class SteamPacketBuffer(io.BytesIO):
    """In-memory byte buffer for reading and writing binary data."""

    __NULL_BYTE = b"\x00"

    def __len__(self) -> int:
        return len(self.getvalue())

    def __repr__(self) -> str:
        data = self.getvalue()
        max_display = 20  # Limit display length for readability
        data_display = data[:max_display] + (b"..." if len(data) > max_display else b"")
        return f"<SteamPacketBuffer length={len(self)} data={data_display!r}>"

    def __str__(self) -> str:
        return str(self.getvalue())

    def _read_line(self) -> bytearray:
        result = bytearray()
        while True:
            char = self.read(1)
            if not char or char == self.__NULL_BYTE:
                break
            result.extend(char)
        return result

    def read_byte(self) -> int:
        """Read a 8 bit character or unsigned integer (1 byte)."""
        return struct.unpack("<B", self.read(1))[0]

    def read_char(self) -> str:
        """Read a single ASCII character."""
        return chr(self.read_byte())

    def write_byte(self, value: int):
        """Write a 8 bit character or unsigned integer. From 0 to 255"""
        self.write(struct.pack("<B", value))

    def write_char(self, value: str):
        """Write a single ASCII character."""
        self.write_byte(ord(value))

    def read_short(self) -> int:
        """Read a 16 bit signed integer (2 bytes)."""
        return struct.unpack("<h", self.read(2))[0]

    def write_short(self, value: int):
        """Write a 16 bit signed integer. From -32768 to 32767."""
        self.write(struct.pack("<h", value))

    def read_float(self) -> float:
        """Read a 32 bit floating point (4 bytes)."""
        return struct.unpack("<f", self.read(4))[0]

    def write_float(self, value: float):
        """Write a 32 bit floating point."""
        self.write(struct.pack("<f", value))

    def read_long(self) -> int:
        """Read a 32 bit signed integer (4 bytes)."""
        return struct.unpack("<l", self.read(4))[0]

    def write_long(self, value: int):
        """Write a 32 bit signed integer. From -2147483648 to 2147483647."""
        self.write(struct.pack("<l", value))

    def read_long_long(self) -> int:
        """Read a 64 bit unsigned integer (8 bytes)."""
        return struct.unpack("<Q", self.read(8))[0]

    def write_long_long(self, value: int):
        """Write a 64 bit unsigned integer. From 0 to 18446744073709551615."""
        self.write(struct.pack("<Q", value))

    def read_string(self) -> str:
        """Read a null-terminated UTF-8 string."""
        return self._read_line().decode("utf-8")

    def write_string(self, value: str):
        """Write a UTF-8 string followed by a null terminator."""
        self.write(value.encode("utf-8") + self.__NULL_BYTE)
