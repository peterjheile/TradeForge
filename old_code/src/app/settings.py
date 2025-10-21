###
# EDITS:
#
# 10/6/2025: Pulls setting configurations for the .env file. Works for just alpaca for now, but will be expanded
# 10/7/2025: Added Tradier Broker settings configuration, added active config for active provider
###

from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict



#broker specific settings for alpaca
class AlpacaSettings(BaseModel):
    key: str = Field(default="", alias="APCA_API_KEY_ID", repr=False)
    secret: str = Field(default="", alias="APCA_API_SECRET_KEY", repr = False)
    paper: bool = Field(default=True, alias="APCA_API_PAPER")
    feed: str = Field(default="iex", alias="APCA_FEED")  # free-tier default


    #check for if it has the required tokens/data from .venv to link to interact with Broker account API
    def configured(self) -> bool:
        return bool(self.key and self.secret)
    

    #custom represent so that secrets and keys are not leaked.
    def __repr__(self) -> str:
        k = f"{self.key[:4]}..." if self.key else "None"
        s = "*" * 10
        return f"AlpacaSettings(key={k}, secret={s}, paper={self.paper}, feed='{self.feed}')"





class TradierSettings(BaseModel):
    access_token: str = Field(default="", alias = "TRDR_ACCESS_TOKEN", repr=False)
    account_id: str = Field(default="", alias="TRDR_ACCOUNT_ID", repr=False)
    paper: bool = Field(default=True, alias="TRDR_PAPER_ACCT")

    #changes respective url based on if a paper account or not
    @property
    def base_url(self) -> str:
        return (
            "https://sandbox.tradier.com/v1"
            if self.paper
            else "https://api.tradier.com/v1"
        )

    #check for if it has the required tokens/data from .venv to link to interact with Broker account API
    def configured(self) -> bool:
        return bool(self.access_token and self.account_id)
    
    #custom represent so that secrets and keys are not leaked.
    def __repr__(self) -> str:
        tok = "*" * 10
        acc = f"{self.account_id[:3]}..."   if self.account_id   else "None"
        return f"TradierSettings(account={acc}, token={tok}, paper={self.paper})"






#consolidated App setting interface each broker settings will flow through
class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_nested_delimiter="__",
        case_sensitive=False,

        extra = "forbid"
    )

    #default trading platform if alpaca because that is what I use and that is what I want lol
    provider: Literal["tradier", "alpaca"] = Field(default="alpaca", alias="PROVIDER")
    alpaca: AlpacaSettings = AlpacaSettings()
    tradier: TradierSettings = TradierSettings()

    #thgis is here so ALLOW_REAL_TRADES is recognized
    allow_real_trades: bool = Field(default=False, alias="ALLOW_REAL_TRADES")


    #ensures a provider has all keys/data required to connect to its respective api and be a valid account
    def assert_active_provider_configured(self) -> None:
        if self.provider == "alpaca" and not self.alpaca.configured():
            raise ValueError("Alpaca selected but APCA_API_KEY_ID/APCA_API_SECRET_KEY are missing.")
        if self.provider == "tradier" and not self.tradier.configured():
            raise ValueError("Tradier selected but ACCESS_TOKEN/ACCOUNT_ID are missing.")
        

    #returns a list of the properly configured providers that you can use
    def configured_providers(self) -> list[str]:
        out = []
        if self.alpaca.configured(): out.append("alpaca")
        if self.tradier.configured(): out.append("tradier")
        return out


    #short safe summary for loggings and prints
    def safe_summary(self) -> str:
        parts = [f"provider={self.provider}"]
        parts.append(f"alpaca(paper={self.alpaca.paper}, feed={self.alpaca.feed})")
        parts.append(f"tradier(paper={self.tradier.paper})")
        return " | ".join(parts)



#returns a chached validated setting object
def get_settings() -> AppSettings:
    return AppSettings()


