# import pytest
# from app.settings import get_settings
# from alpaca.trading.client import TradingClient

# @pytest.fixture(scope="session", autouse=True)
# def alpaca_preflight():
#     s = get_settings()
#     if s.provider != "alpaca": 
#         print("AHHH")
#         pytest.skip("PROVIDER != alpaca")
#     tc = TradingClient(s.alpaca.key, s.alpaca.secret, paper=s.alpaca.paper)
#     try:
#         acct = tc.get_account()
#     except Exception as e:
#         pytest.skip(f"Alpaca preflight failed: {e}")
#     return acct


