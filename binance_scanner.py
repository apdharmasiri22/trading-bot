import requests
import pandas as pd


BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"


def get_market_data():

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            BINANCE_URL,
            headers=headers,
            timeout=15
        )

        print(response.status_code)

        data = response.json()

        if response.status_code != 200:
            print(data)
            return pd.DataFrame()


        coins = []

        for item in data:

            symbol = item.get("symbol","")

            if symbol.endswith("USDT"):

                coins.append({

                    "Symbol": symbol,
                    "Price": float(item["lastPrice"]),
                    "Change %": float(item["priceChangePercent"]),
                    "Volume": float(item["quoteVolume"])

                })


        return pd.DataFrame(coins)


    except Exception as e:

        print("ERROR:",e)
        return pd.DataFrame()
