import requests
import pandas as pd

KLINE_URL = "https://api.binance.com/api/v3/klines"


def get_market_data():

    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]

    rows = []

    for symbol in symbols:

        try:

            url = f"{KLINE_URL}?symbol={symbol}&interval=1h&limit=1"

            r = requests.get(url, timeout=10)
            data = r.json()

            # ❌ skip invalid response
            if not isinstance(data, list):
                print("Skip:", symbol, data)
                continue

            candle = data[0]

            rows.append({
                "Symbol": symbol,
                "Open": float(candle[1]),
                "High": float(candle[2]),
                "Low": float(candle[3]),
                "Close": float(candle[4]),
                "Volume": float(candle[5]),
                "Change %": ((float(candle[4]) - float(candle[1])) / float(candle[1])) * 100
            })

        except Exception as e:
            print("Error:", symbol, e)

    df = pd.DataFrame(rows)

print("DEBUG ROWS:", len(rows))
print(df.head())

return df
