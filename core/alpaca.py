#contains the env variables for the alpaca account to connect to
#also contians the alpaca api instance bound to the account

from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

@dataclass(frozen=True)
class AlpacaAccount:
    key: str = getenv("APCA_API_KEY_ID", "")
    secret: str = getenv("APCA_API_SECRET_KEY", "")
    paper: bool = getenv("APCA_API_PAPER", "True").lower() in ("true", "1", "t")


    #Just the base url to the overarching account to connect to. Which trade account (there can be multiple) is determined by the key/secret pair
    @property
    def base_url(self) -> str:
        return getenv("ENDPOINT_PAPER_URL" if self.paper else "ENDPOINT_LIVE_URL")
    

    #returns a REST api instance bound to this account
    @property
    def api(self):
        return tradeapi.REST(
            self.key,
            self.secret,
            self.base_url,
            api_version="v2"
        )

