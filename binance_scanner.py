import requests
import pandas as pd


BINANCE_URL = "https://fapi.binance.com/fapi/v1/ticker/24hr"


def get_market_data():

    try:

        response = requests.get(
            BINANCE_URL,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )


        if response.status_code != 200:
            print("BINANCE ERROR:", response.text)
            return pd.DataFrame()


        data = response.json()


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


        df = pd.DataFrame(coins)

        return df



    except Exception as e:

        print("ERROR:",e)

        return pd.DataFrame()
