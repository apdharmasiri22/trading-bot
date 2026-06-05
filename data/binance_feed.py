import requests
import pandas as pd
import streamlit as st


BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"


@st.cache_data(ttl=30)
def get_all_coins():

    try:
        response = requests.get(
            BINANCE_URL,
            timeout=10
        )

        data = response.json()

        coins = []

        for item in data:

            symbol = item.get("symbol")

            if symbol and symbol.endswith("USDT"):

                coins.append({
                    "symbol": symbol,
                    "priceChangePercent": float(
                        item.get("priceChangePercent",0)
                    ),
                    "volume": float(
                        item.get("quoteVolume",0)
                    )
                })

        return coins


    except Exception as e:
        print("BINANCE ERROR:", e)
        return []



@st.cache_data(ttl=30)
def get_top_coins(limit=30):

    coins = get_all_coins()

    if not coins:
        return []


    df = pd.DataFrame(coins)

    df = df.sort_values(
        by="volume",
        ascending=False
    )


    return df.head(limit)["symbol"].tolist()



@st.cache_data(ttl=10)
def get_price(symbol):

    try:

        url = (
        "https://api.binance.com/api/v3/ticker/price"
        f"?symbol={symbol}"
        )


        data = requests.get(
            url,
            timeout=5
        ).json()


        return float(data["price"])


    except Exception as e:
        print("PRICE ERROR:", e)
        return None
