from app.factory import make_adapters

broker, data = make_adapters()

print("-------------------------------------")
print("✅ Factory returned:", type(broker).__name__, "and", type(data).__name__)
print("-------------------------------------")
print("Account:", broker.get_account())
print("-------------------------------------")
print("Bars:", data.get_bars("AAPL", "1Min", limit=3)[:1])
print("-------------------------------------")
