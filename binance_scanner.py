import requests
import pandas as pd


BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"


def get_market_data():

    try:
        response = requests.get(
            BINANCE_URL,
            timeout=10
        )

        data = response.json()

        coins = []

        for item in data:

            symbol = item["symbol"]

            # USDT pairs only
            if symbol.endswith("USDT"):

                coins.append({

                    "Symbol": symbol,
                    "Price": float(item["lastPrice"]),
                    "Change %": float(item["priceChangePercent"]),
                    "Volume": float(item["quoteVolume"])

                })


        df = pd.DataFrame(coins)

        return df


    except Exception as e:

        return pd.DataFrame()
