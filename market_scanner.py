import requests
import pandas as pd

def get_market_data(symbol="BTCUSDT", interval="1h", limit=200):

    try:
        symbol = symbol.upper().strip()

        url = "https://api.binance.com/api/v3/klines"

        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        r = requests.get(url, params=params, timeout=10)

        if r.status_code != 200:
            print("BINANCE ERROR:", r.text)
            return pd.DataFrame()

        data = r.json()

        if not isinstance(data, list) or len(data) == 0:
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=[
            "Time","Open","High","Low","Close","Volume",
            "c","q","n","t1","t2","t3"
        ])

        df = df[["Open","High","Low","Close","Volume"]].astype(float)

        return df

    except Exception as e:
        print("ERROR:", e)
        return pd.DataFrame()
