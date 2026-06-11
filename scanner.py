import requests
import pandas as pd

def get_market_data(symbol="BTCUSDT", interval="1h", limit=200):

    try:
        symbol = symbol.strip().upper()

        url = "https://api.binance.com/api/v3/klines"

        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        r = requests.get(url, params=params, timeout=10)

        print("STATUS:", r.status_code)
        print("RAW:", r.text[:200])

        data = r.json()

        if isinstance(data, dict):
            print("BINANCE ERROR:", data)
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=[
            "time","Open","High","Low","Close","Volume",
            "c","q","n","t1","t2","t3"
        ])

        df = df[["Open","High","Low","Close","Volume"]].astype(float)

        return df

    except Exception as e:
        print("ERROR:", e)
        return pd.DataFrame()
