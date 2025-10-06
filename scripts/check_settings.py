###
# Last edit: 10/6/2025
#
# Desc: Quick test to see if settings works and what exactly is printed
###

from app.settings import get_settings
s = get_settings()
print("provider:", s.provider)
print("alpaca.key present?:", bool(s.alpaca.key))
print("allow_trades:", s.allow_real_trades)
print("alpaca.paper:", s.alpaca.paper)