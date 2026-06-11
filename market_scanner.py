import requests
import pandas as pd

def get_market_data(symbol="BTCUSDT", interval="1h", limit=200):

    try:
        symbol = str(symbol).strip().upper()

        url = "https://api.binance.com/api/v3/klines"

        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        r = requests.get(url, params=params, timeout=10)

        print("STATUS:", r.status_code)
        print("RESPONSE:", r.text[:200])

        # ❗ HARD CHECK
        if r.status_code != 200:
            return pd.DataFrame()

        data = r.json()

        if not isinstance(data, list):
            return pd.DataFrame()

        if len(data) == 0:
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=[
            "time","Open","High","Low","Close","Volume",
            "c","q","n","t1","t2","t3"
        ])

        return df[["Open","High","Low","Close","Volume"]].astype(float)

    except Exception as e:
        print("ERROR:", e)
        return pd.DataFrame()
