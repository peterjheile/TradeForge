###
# DESCR: Maps uniform/domain names and objects to BROKER specific names/requirements for retrieving market data (i.e. candles)
# EDITS:
# 10/7/2025: added Tradier Market Data Class
###

from __future__ import annotations
from typing import List
import requests
from core.ports.market_data import MarketData
from core.domain.models import Bar, Timeframe
from adapters.tradier.mappers import map_timeframe
from app.settings import TradierSettings




class TradierMarketData(MarketData):
    def __init__(self, TRDRSettings: TradierSettings):
        self._token = TRDRSettings.access_token
        self._base = TRDRSettings.base_url.rstrip("/")

    def get_bars(self, symbol: str, timeframe: Timeframe, limit: int = 100) -> List[Bar]:
        interval = map_timeframe(timeframe)
        url = f"{self._base}/markets/bars"
        params = {"symbol": symbol, "interval": interval, "limit": limit, "session_filter": "all"}
        r = requests.get(url, headers={"Authorization": f"Bearer {self._token}", "Accept": "application/json"},
                         params=params, timeout=15)
        r.raise_for_status()
        bars = r.json().get("bars", {}).get("bar", [])  # can be dict or list
        if isinstance(bars, dict):
            bars = [bars]
        out: List[Bar] = []
        for b in bars:
            out.append(Bar(
                t=b.get("time") or b.get("timestamp") or "",
                o=float(b.get("open", 0.0)),
                h=float(b.get("high", 0.0)),
                l=float(b.get("low", 0.0)),
                c=float(b.get("close", 0.0)),
                v=float(b.get("volume", 0.0)),
            ))
        return out

    def stream_trades(self, symbol: str, on_trade):
        raise NotImplementedError("Tradier streaming not wired yet.")


