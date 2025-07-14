"""Pydantic models for SourceWatch API responses."""

from typing import List, Optional, Dict
from pydantic import BaseModel


class BasicServerModel(BaseModel):
    """Server connection information."""

    ip: str
    port: int
    ping: float


class ServerInfoModel(BaseModel):
    """Server information model."""

    server_protocol_version: int
    server_name: str
    game_map: str
    game_directory: str
    game_title: str
    game_app_id: int
    players_current: int
    players_max_slots: int
    players_bots: int
    server_type: str
    server_os: str
    server_password_protected: int
    server_vac_secured: int
    game_version: str
    players_humans: int
    players_free_slots: int
    # Optional extra data fields
    server_port: Optional[int] = None
    server_steam_id: Optional[int] = None
    server_spectator_port: Optional[int] = None
    server_spectator_name: Optional[str] = None
    server_tags: Optional[str] = None


class InfoResponseModel(BaseModel):
    """Server information response model."""

    info: ServerInfoModel
    server: BasicServerModel


class PlayerModel(BaseModel):
    """Individual player information."""

    index: int
    id: int
    name: str
    kills: int
    play_time: float


class PlayersResponseModel(BaseModel):
    """Players response model."""

    players: List[PlayerModel]
    server: BasicServerModel


class RulesResponseModel(BaseModel):
    """Server rules response model."""

    rules: Dict[str, str]
    server: BasicServerModel


class InfoGoldSrcResponseModel(BaseModel):
    """GoldSrc server information response model."""

    server_address: str
    server_name: str
    game_map: str
    game_directory: str
    game_title: str
    players_current: int
    players_max_slots: int
    server_protocol_version: int
    server_type: str
    server_os: str
    server_password_protected: int
    game_mod: int
    server_vac_secured: int
    players_bots: int
    players_humans: int
    players_free_slots: int
    server: BasicServerModel
