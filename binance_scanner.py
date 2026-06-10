import requests
import pandas as pd


URL = "https://api.coingecko.com/api/v3/coins/markets"


import requests
import pandas as pd


URL = "https://api.coingecko.com/api/v3/coins/markets"


def get_market_data():

    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": "false"
    }

    try:

        r = requests.get(
            URL,
            params=params,
            timeout=15
        )

        data = r.json()

        coins = []


        for c in data:

            # skip invalid data
            if "symbol" not in c:
                continue


            symbol = c["symbol"].upper()


            coins.append({

                "Symbol": symbol + "USDT",
                "Price": c.get("current_price",0),
                "Change %": c.get("price_change_percentage_24h",0),
                "Volume": c.get("total_volume",0)

            })


        return pd.DataFrame(coins)


    except Exception as e:

        print("ERROR:", e)

        return pd.DataFrame()
