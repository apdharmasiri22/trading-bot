import requests
import pandas as pd

URL = "https://api.coingecko.com/api/v3/coins/markets"


def get_market_data():

    try:

        params = {
            "vs_currency": "usd",
            "order": "volume_desc",
            "per_page": 20,
            "page": 1,
            "sparkline": False
        }

        r = requests.get(URL, params=params, timeout=10)

        print("STATUS:", r.status_code)

        if r.status_code != 200:
            return pd.DataFrame()

        data = r.json()

        rows = []

        for c in data:

            rows.append({
                "Symbol": c["symbol"].upper(),
                "Price": c["current_price"],
                "Volume": c["total_volume"],
                "Change %": c["price_change_percentage_24h"]
            })

        print("ROWS:", len(rows))

        return pd.DataFrame(rows)

    except Exception as e:
        print("ERROR:", e)
        return pd.DataFrame()
