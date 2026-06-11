import requests
import pandas as pd

KLINE_URL = "https://api.binance.com/api/v3/klines"


def get_market_data():

    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]

    rows = []

    print("🚀 START FETCH")

    for symbol in symbols:

        try:
            url = f"{KLINE_URL}?symbol={symbol}&interval=1h&limit=1"

            r = requests.get(url, timeout=10)

            data = r.json()

            # ❌ Binance error check
            if isinstance(data, dict):
                print("ERROR:", symbol, data)
                continue

            if not isinstance(data, list) or len(data) == 0:
                continue

            c = data[0]

            rows.append({
                "Symbol": symbol,
                "Open": float(c[1]),
                "High": float(c[2]),
                "Low": float(c[3]),
                "Close": float(c[4]),
                "Volume": float(c[5]),
                "Change %": ((float(c[4]) - float(c[1])) / float(c[1])) * 100
            })

        except Exception as e:
            print("FAIL:", symbol, e)

    df = pd.DataFrame(rows)

    print("FINAL ROWS:", len(df))

    return df
