import requests
import pandas as pd

URLS = [
    "https://api1.binance.com/api/v3/ticker/24hr",
    "https://fapi.binance.com/fapi/v1/ticker/24hr"
]

def get_market_data():

    for url in URLS:

        try:
            r = requests.get(url, timeout=10)

            if r.status_code != 200:
                continue

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

            if coins:
                return pd.DataFrame(coins)

        except:
            continue

    return pd.DataFrame()
