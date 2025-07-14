# SourceWatch

[![Python Version](https://img.shields.io/pypi/pyversions/sourcewatch)](https://pypi.org/project/sourcewatch/)
[![PyPI Version](https://img.shields.io/pypi/v/sourcewatch)](https://pypi.org/project/sourcewatch/)
[![License](https://img.shields.io/pypi/l/sourcewatch)](https://github.com/SourceWatch/SourceWatch/blob/master/LICENSE)

A Python 3 library for querying information from Valve's GoldSrc and Source game servers. This library provides a complete implementation of the [Server Queries protocol](http://developer.valvesoftware.com/wiki/Server_Queries) used by games like Counter-Strike, Half-Life, Team Fortress, and many others.

## Features

- Support for both GoldSrc and Source engine servers
- Query server information, player lists, and server rules
- Ping measurement functionality
- Multi-packet response handling
- Modern Python 3.8+ support with type hints (Pydantic)
- MCP ready

## Installation

Install SourceWatch using pip:

```bash
pip install sourcewatch
```

## Quick Start

```python
import SourceWatch

# Connect to a server
server = SourceWatch.Query('server.example.com', 27015)

# Get basic server information
info = server.info()
print(f"Server: {info['info']['server_name']}")
print(f"Map: {info['info']['game_map']}")
print(f"Players: {info['info']['players_current']}/{info['info']['players_max_slots']}")

# Get player list
players = server.players()
for player in players['players']:
    print(f"Player: {player['name']} (Score: {player['kills']})")

# Get server rules/settings
rules = server.rules()
for key, value in rules['rules'].items():
    print(f"{key}: {value}")

# Measure ping
ping = server.ping()
print(f"Ping: {ping}ms")
```

## API Reference

### SourceWatch.Query(host, port=27015, timeout=10)

Main class for querying game servers.

**Parameters:**
- `host` (str): Server hostname or IP address
- `port` (int, optional): Server port (default: 27015)
- `timeout` (int, optional): Connection timeout in seconds (default: 10)

**Methods:**

#### `info()`
Returns basic server information including name, map, player count, and game details.

**Returns:** Dictionary with server information

```python
{
    "info": {
        "server_name": "My Game Server",
        "game_map": "de_dust2",
        "game_title": "Counter-Strike: Source",
        "players_current": 12,
        "players_max_slots": 24,
        "players_bots": 2,
        "players_humans": 10,
        "server_type": "d",  # 'd' for dedicated, 'l' for listen
        "server_os": "l",    # 'l' for Linux, 'w' for Windows
        "server_password_protected": 0,
        "server_vac_secured": 1,
        # ... additional fields
    },
    "server": {
        "ip": "127.0.0.1",
        "port": 27015,
        "ping": 42.5
    }
}
```

#### `players()`
Returns list of players currently on the server.

**Returns:** Dictionary with player information

```python
{
    "players": [
        {
            "index": 0,
            "name": "PlayerName",
            "kills": 15,
            "play_time": 1234.5
        },
        # ... more players
    ],
    "server": {
        "ip": "127.0.0.1",
        "port": 27015,
        "ping": 45.2
    }
}
```

#### `rules()`
Returns server configuration and rules.

**Returns:** Dictionary with server rules

```python
{
    "rules": {
        "sv_gravity": "800",
        "mp_friendlyfire": "1",
        "mp_timelimit": "30",
        # ... more rules
    },
    "server": {
        "ip": "127.0.0.1",
        "port": 27015,
        "ping": 38.7
    }
}
```

#### `ping(num_requests=3)`
Measures server response time by sending multiple info requests.

**Parameters:**
- `num_requests` (int, optional): Number of ping requests to average (default: 3)

**Returns:** Average ping in milliseconds (float)

## Supported Games

This library works with servers running games that use Valve's server query protocol, including:

- **Source Engine Games:**
  - Counter-Strike: Source
  - Half-Life 2: Deathmatch
  - Team Fortress 2
  - Garry's Mod
  - Left 4 Dead series
  - Portal 2

- **GoldSrc Engine Games:**
  - Counter-Strike 1.6
  - Half-Life
  - Team Fortress Classic
  - Day of Defeat

## Error Handling

The library raises `SourceWatchError` for various error conditions:

```python
import SourceWatch

try:
    server = SourceWatch.Query('invalid-server.com')
    info = server.info()
except SourceWatch.SourceWatchError as e:
    print(f"Query failed: {e}")
except socket.timeout:
    print("Connection timed out")
except socket.gaierror:
    print("Could not resolve hostname")
```

## Advanced Usage

### Custom Timeout

```python
# Set a custom timeout for slow connections
server = SourceWatch.Query('server.example.com', timeout=30)
```

### Logging

Enable debug logging to see detailed protocol communication:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

server = SourceWatch.Query('server.example.com')
```

## Development

### Running Tests

```bash
python -m pytest test/
```

### Requirements

- Python 3.8 or higher
- No external dependencies for core functionality

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- **Alex Kuhrt** - Current maintainer
- **Andreas Klauer** - Original SourceLib implementation

This project is a modernized fork of [SourceLib](https://github.com/frostschutz/SourceLib).

## Changelog

### Version 0.0.4
- Modernized packaging with pyproject.toml
- Fixed server query protocol implementation
- Added comprehensive test suite
- Improved error handling and logging

---

For more information, visit the [GitHub repository](https://github.com/SourceWatch/SourceWatch) or check out the [issues page](https://github.com/SourceWatch/SourceWatch/issues) for bug reports and feature requests.
