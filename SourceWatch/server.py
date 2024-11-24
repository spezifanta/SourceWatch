"""
A server should have it's own reprensentation.
"""


class Server:
    @classmethod
    def from_str(cls, server: str):
        """Create a Server instance from a string.
        Example: Server.from_str('10.0.0.3:27016')
        """
        try:
            ip, port = server.split(":")
            return cls(ip, int(port))
        except ValueError:
            raise ValueError('Invalid server format. Use "<IP-ADDRESS>:<PORT>"')

    def __init__(self, ip: str, port: int = 27015):
        self.ip = ip
        self.port = self._validate_port(port)

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            return self.__dict__.get(attr, None)

    def __repr__(self):
        return f"<Server: {self}>"

    def __str__(self):
        return f"{self.ip}:{self.port}"

    def __eq__(self, other):
        return isinstance(other, Server) and str(self) == str(other)

    def __ne__(self, other):
        return not (self == other)

    def __iter__(self):
        for attribute in self.__dict__:
            if not attribute.startswith("_"):
                yield attribute

    def _get_name(self):
        return self.__dict__.setdefault("name", self.ip)

    def _set_name(self, name):
        self.__dict__["name"] = name

    name = property(_get_name, _set_name)

    def as_tuple(self) -> tuple:
        """Return server IP and port as tuple."""
        return (self.ip, self.port)

    def _validate_port(self, port: int):
        if port < 1 or port > 65535:
            raise ValueError("Invalid port range.")
        return port
