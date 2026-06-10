import requests
import pandas as pd

URL = "https://api.coingecko.com/api/v3/coins/markets"

def get_market_data():

    try:
        params = {
            "vs_currency": "usd",
            "order": "volume_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": False
        }

        r = requests.get(URL, params=params, timeout=10)

        if r.status_code != 200:
            return pd.DataFrame()

        data = r.json()

        coins = []

        for c in data:

            symbol = c.get("symbol", "").upper()

            coins.append({
                "Symbol": symbol,   # 👈 FIXED (NO USDT force)
                "Price": c.get("current_price", 0),
                "Change %": c.get("price_change_percentage_24h", 0),
                "Volume": c.get("total_volume", 0)
            })

        return pd.DataFrame(coins)

    except Exception as e:
        print("ERROR:", e)
        return pd.DataFrame()
