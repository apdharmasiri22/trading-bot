import requests
import pandas as pd


MARKET_URL = "https://api.coingecko.com/api/v3/coins/markets"
KLINE_URL = "https://api.binance.com/api/v3/klines"


def get_market_data():

    try:

        params = {
            "vs_currency": "usd",
            "order": "volume_desc",
            "per_page": 20,
            "page": 1,
            "sparkline": False
        }


        r = requests.get(
            MARKET_URL,
            params=params,
            timeout=10
        )


        if r.status_code != 200:
            return pd.DataFrame()


        coins = r.json()

        rows = []


        for c in coins:

            symbol = c.get("symbol","").upper()+"USDT"


            try:

                url = (
                    f"{KLINE_URL}"
                    f"?symbol={symbol}"
                    f"&interval=1h"
                    f"&limit=1"
                )


                candle = requests.get(
                    url,
                    timeout=10
                ).json()[0]


                rows.append({

                    "Symbol": symbol,

                    "Open": float(candle[1]),

                    "High": float(candle[2]),

                    "Low": float(candle[3]),

                    "Close": float(candle[4]),

                    "Volume": float(candle[5]),

                    "Change %":
                    float(c.get(
                        "price_change_percentage_24h",
                        0
                    ))

                })


            except:
                continue


        return pd.DataFrame(rows)


    except Exception as e:
        print(e)
        return pd.DataFrame()
