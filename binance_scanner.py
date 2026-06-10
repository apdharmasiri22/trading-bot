import requests
import pandas as pd


BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"


def get_market_data():

    try:

        response = requests.get(
            BINANCE_URL,
            timeout=15
        )

        print("STATUS:", response.status_code)
        print("TEXT:", response.text[:200])


        if response.status_code != 200:
            return pd.DataFrame()


        data = response.json()


        coins = []

        for item in data:

            if item["symbol"].endswith("USDT"):

                coins.append({

                    "Symbol": item["symbol"],
                    "Price": item["lastPrice"],
                    "Change %": item["priceChangePercent"],
                    "Volume": item["quoteVolume"]

                })


        df = pd.DataFrame(coins)

        return df


    except Exception as e:

        print("ERROR:", e)
        return pd.DataFrame()
