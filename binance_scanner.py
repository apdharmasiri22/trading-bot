import requests
import pandas as pd

URL = "https://api.binance.com/api/v3/ticker/24hr"

def get_market_data():

    try:
        r = requests.get(URL, timeout=10)

        if r.status_code != 200:
            return pd.DataFrame()

        data = r.json()

        coins = []

        for c in data:

            symbol = c.get("symbol", "")

            # 🔥 ONLY real USDT trading pairs
            if not symbol.endswith("USDT"):
                continue

            # ❌ skip stable / noise coins
            if symbol in ["USDCUSDT", "DAIUSDT", "TUSDUSDT"]:
                continue

            coins.append({
                "Symbol": symbol,
                "Price": float(c.get("lastPrice", 0)),
                "Change %": float(c.get("priceChangePercent", 0)),
                "Volume": float(c.get("volume", 0))
            })

        df = pd.DataFrame(coins)

        # 🔥 sort properly
        df = df.sort_values("Volume", ascending=False)

        return df

    except Exception as e:
        print("ERROR:", e)
        return pd.DataFrame()
