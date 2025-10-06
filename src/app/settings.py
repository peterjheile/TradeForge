###
# Last edit: 10/6/2025
#
# Desc: Pulls setting configurations for the .env file. Works for just alpaca for now, but will be expanded
###

from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict



#broker specific settings for alpaca
class AlpacaSettings(BaseModel):
    key: str = Field(default="", alias="APCA_API_KEY_ID")
    secret: str = Field(default="", alias="APCA_API_SECRET_KEY")
    paper: bool = Field(default=True, alias="APCA_API_PAPER")
    feed: str = Field(default="iex", alias="APCA_FEED")  # free-tier default



#consolidated App setting interface each broker settings will flow through
class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_nested_delimiter="__",
        case_sensitive=False,

        extra = "forbid"
    )

    provider: Literal["alpaca"] = "alpaca"
    alpaca: AlpacaSettings = AlpacaSettings()

    #thgis is here so ALLOW_REAL_TRADES is recognized
    allow_real_trades: bool = Field(default=False, alias="ALLOW_REAL_TRADES")

#returns a chached validated setting object
def get_settings() -> AppSettings:
    return AppSettings()