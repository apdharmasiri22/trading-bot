import requests
import pandas as pd


def get_all_coins():

    def get_all_coins():

    url = "https://api.binance.com/api/v3/ticker/24hr"

    try:
        response = requests.get(url, timeout=10)

        print("STATUS:", response.status_code)

        data = response.json()

        print("COINS:", len(data))

        coins = []

        for item in data:
            if item["symbol"].endswith("USDT"):
                coins.append({
                    "symbol": item["symbol"],
                    "volume": float(item["quoteVolume"])
                })

        return coins

    except Exception as e:
        print("ERROR:", e)
        return []



def get_top_coins(limit=20):

    coins = get_all_coins()

    if not coins:
        return []

    df = pd.DataFrame(coins)

    df = df.sort_values(
        by="volume",
        ascending=False
    )

    return df.head(limit)["symbol"].tolist()



def get_price(symbol):

    try:

        url = (
            "https://api.binance.com/api/v3/ticker/price"
            f"?symbol={symbol}"
        )

        data = requests.get(
            url,
            timeout=10
        ).json()

        return float(data["price"])

    except:
        return None
