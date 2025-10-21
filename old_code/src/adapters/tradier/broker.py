###
# EDITS:
#
# 10/7/2025: my tradier adapter for the domain class commands to tradier api commands
###


from __future__ import annotations
from typing import Any, List
import requests

from core.ports.broker import Broker
from core.domain.models import OrderRequest, Order, OrderStatus, Side, OrderType, TimeInForce
from adapters.tradier.mappers import map_side, map_tif, map_type
from app.settings import TradierSettings




JSON = dict[str, Any]

def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}




class TradierBroker(Broker):

    def __init__(self, TRDTSettings: TradierSettings):
        self._token = TRDTSettings.access_token
        self._acct = TRDTSettings.account_id
        self._base = TRDTSettings.base_url.rstrip("/")


    def place_order(self, req: OrderRequest) -> Order:
        url = f"{self._base}/accounts/{self._acct}/orders"
        form = dict[str, Any] = {
            "class": "equity",
            "symbol": req.symbol,
            "side": map_side(req.side),
            "quantity": req.qty,
            "type": map_type(req.type),
            "duration": map_tif(req.time_in_force)
        }

        if req.type is OrderType.LIMIT and req.limit_price is not None:
            form['price'] = req.limit_price


        r = requests.post(url, headers=_headers(self._token), data=form, timeout=15)
        r.raise_for_status()
        j = r.json()
        # response shape: { "order": { "id": "...", "status": "...", "symbol": "...", ... } }
        o = j.get("order", j)
        status = (o.get("status") or "accepted").lower().replace(" ", "_")
        
        return Order(
            id=str(o.get("id", "")),
            symbol=o.get("symbol", req.symbol),
            status=OrderStatus(status) if status in OrderStatus.__members__.values() else OrderStatus.ACCEPTED,
            filled_qty=float(o.get("filled_quantity") or 0.0),
        )



    def cancel_order(self, order_id: str) -> None:
        url = f"{self._base}/accounts/{self._acct}/orders/{order_id}"
        r = requests.delete(url, headers=_headers(self._token), timeout=15)
        r.raise_for_status()


    def get_order(self, order_id: str) -> Order:
        url = f"{self._base}/accounts/{self._acct}/orders/{order_id}"
        r = requests.get(url, headers=_headers(self._token), timeout=15)
        r.raise_for_status()
        o = r.json().get("order", {})
        status = (o.get("status") or "accepted").lower().replace(" ", "_")
        return Order(
            id=str(o.get("id", order_id)),
            symbol=o.get("symbol", ""),
            status=OrderStatus(status) if status in OrderStatus.__members__.values() else OrderStatus.ACCEPTED,
            filled_qty=float(o.get("filled_quantity") or 0.0),
        )
    


    def get_positions(self) -> List[dict]:
        url = f"{self._base}/accounts/{self._acct}/positions"
        r = requests.get(url, headers=_headers(self._token), timeout=15)
        r.raise_for_status()
        # shape: { "positions": { "position": [ {..}, {..} ] } } (can be a dict or list)
        data = r.json().get("positions", {}).get("position", [])
        if isinstance(data, dict):  # single position case
            data = [data]
        return data

    def get_account(self) -> dict:
        url = f"{self._base}/accounts/{self._acct}/balances"
        r = requests.get(url, headers=_headers(self._token), timeout=15)
        print(r)
        r.raise_for_status()
        return r.json().get("balances", {})