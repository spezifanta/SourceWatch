# SourceWatch

Python 3 MIT library to query information from Valve's Goldsrc and Source servers.
A full implementation of http://developer.valvesoftware.com/wiki/Server_Queries

## Usage

```
import SourceWatch

server = SourceWatch.Query('steamcalculator.com', 27015)
print(server.ping())
print(server.info())
print(server.players())
print(server.rules())

```

Info output:

```
{
  "info": {
    "game_app_id": 70,
    "game_title": "Half-Life",
    "game_directory": "valve",
    "game_map": "crossfire",
    "game_version": "1.1.2.2/Stdio",
    "players_bots": 0,
    "players_current": 0,
    "players_humans": 0,
    "players_max_slots": 12,
    "server_name": "SteamCalculator.com #1 HLDM",
    "server_os": "l",
    "server_password_protected": 0,
    "server_port": 27015,
    "server_protocol_version": 48,
    "server_steam_id": 90119214309364746,
    "server_type": "d",
    "server_vac_secured": 1
  }
}
```

### Credits
 Andreas Klauer <Andreas.Klauer@metamorpher.de>
 This project is a fork of https://github.com/frostschutz/SourceLib
