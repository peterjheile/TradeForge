###
# Last edit: 10/6/2025
#
# Desc: command line interface for the application.
###

from __future__ import annotations
import os
import sys
import typer
from typing import Optional

from app.factory import make_account
from app.settings import get_settings
from core.domain.models import Timeframe, Side, OrderType, TimeInForce


app = typer.Typer(help="Trading bot CLI")


#gaurd for trading commands
def _confirm_or_exit(message: str, yes: bool):
    settings = get_settings()
    allow_env = settings.allow_real_trades
    allow_cfg = getattr(settings, "allow_real_trades", False)
    if yes or allow_env or allow_cfg:
        return
    if not typer.confirm(f"{message} Proceed?"):
        typer.echo("Aborted.")
        raise typer.Exit(code=1)
    

#show the basci account information
@app.command()
def account():
    acct = make_account()
    info = acct.account()

    #prinf a small stable portion of the asccount rather than the giant blob
    for k in ("status", "cash", "portfolio_value", "buying_power"):
        if k in info:
            typer.echo(f"{k}: {info[k]}")



@app.command()
def positions():
    acct = make_account()
    pos=acct.positions()
    if not pos:
        typer.echo("No open positions.")

    cols = ["symbol", "qty", "avg_entry_price", "market_value", "unrealized_pl"]
    header = " | ".join(c.upper() for c in cols)
    typer.echo(header)
    typer.echo("-" * len(header))
    for p in pos:
        row = " | ".join(str(p.get(c, "")) for c in cols)
        typer.echo(row)



@app.command()
def bars(
    symbol: str = typer.Argument(..., help="Ticker, e.g., AAPL"),
    tf: Timeframe = typer.Option(Timeframe.ONE_MIN, "--tf", help="Timeframe"),
    limit: int = typer.Option(10, "--limit", "-n", min=1, max=1000, help="Number of bars"),
):
    """Fetch recent OHLCV bars."""
    acct = make_account()
    data = acct.latest_bars(symbol, tf, limit)
    if not data:
        typer.echo("No bars returned.")
        raise typer.Exit(code=2)
    # Show last 5 (or fewer)
    for b in data[-min(5, len(data)):]:
        typer.echo(f"{b.t}  O:{b.o} H:{b.h} L:{b.l} C:{b.c} V:{b.v}")

@app.command()
def buy(
    symbol: str = typer.Argument(..., help="Ticker, e.g., AAPL"),
    qty: float = typer.Argument(..., min=0.0001, help="Quantity"),
    tif: TimeInForce = typer.Option(TimeInForce.DAY, "--tif", help="Time in force"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Place a market BUY."""
    _confirm_or_exit(f"About to BUY {qty} {symbol} @ market.", yes)
    acct = make_account()
    order = acct.buy_market(symbol, qty, tif)
    typer.echo(f"Order {order.id} {order.status} for {order.symbol} (filled {order.filled_qty})")

@app.command()
def sell(
    symbol: str = typer.Argument(..., help="Ticker, e.g., AAPL"),
    qty: float = typer.Argument(..., min=0.0001, help="Quantity"),
    tif: TimeInForce = typer.Option(TimeInForce.DAY, "--tif", help="Time in force"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Place a market SELL."""
    _confirm_or_exit(f"About to SELL {qty} {symbol} @ market.", yes)
    acct = make_account()
    order = acct.sell_market(symbol, qty, tif)
    typer.echo(f"Order {order.id} {order.status} for {order.symbol} (filled {order.filled_qty})")





\
if __name__ == "__main__":
    # Allow `python -m app.cli ...`
    app()