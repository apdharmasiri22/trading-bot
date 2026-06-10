import requests
import pandas as pd


URL = "https://api.coingecko.com/api/v3/coins/markets"


def get_market_data():

    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 250,
        "page": 1,
        "sparkline": "false"
    }


    r = requests.get(
        URL,
        params=params,
        timeout=15
    )


    data = r.json()


    coins=[]


    for c in data:

        symbol = c["symbol"].upper()


        # remove stable coins
        blacklist = [
            "USDT",
            "USDC",
            "BUSD",
            "DAI",
            "TUSD"
        ]


        if symbol in blacklist:
            continue


        coins.append({

            "Symbol": symbol+"USDT",
            "Price": c["current_price"],
            "Change %": c["price_change_percentage_24h"],
            "Volume": c["total_volume"]

        })


    return pd.DataFrame(coins)
