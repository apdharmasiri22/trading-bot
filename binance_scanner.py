import requests
import pandas as pd

BINANCE_URL = "https://fapi.binance.com/fapi/v1/ticker/24hr"

def get_market_data():

    try:
        r = requests.get(
            BINANCE_URL,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        if r.status_code != 200:
            return pd.DataFrame()

        data = r.json()

        coins = []

        for c in data:

            symbol = c.get("symbol", "")

            if not symbol.endswith("USDT"):
                continue

            coins.append({
                "Symbol": symbol,
                "Price": float(c.get("lastPrice", 0)),
                "Change %": float(c.get("priceChangePercent", 0)),
                "Volume": float(c.get("volume", 0))
            })

        return pd.DataFrame(coins)

    except Exception as e:
        print("ERROR:", e)
        return pd.DataFrame()
