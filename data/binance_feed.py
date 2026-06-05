import requests
import pandas as pd
import streamlit as st


BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"


@st.cache_data(ttl=30)
def get_all_coins():

    try:
        r = requests.get(
            BINANCE_URL,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        # debug
        if r.status_code != 200:
            st.error(f"Binance API Error: {r.status_code}")
            return []

        data = r.json()

        coins = []

        for item in data:

            symbol = item.get("symbol")

            if symbol and symbol.endswith("USDT"):

                coins.append({
                    "symbol": symbol,
                    "volume": float(item.get("quoteVolume", 0)),
                    "change": float(item.get("priceChangePercent", 0))
                })


        return coins


    except Exception as e:

        st.error(f"Connection Error: {e}")
        return []



@st.cache_data(ttl=30)
def get_top_coins(limit=100):

    coins = get_all_coins()


    if len(coins) == 0:
        return []


    df = pd.DataFrame(coins)


    df = df.sort_values(
        "volume",
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

        r = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent":"Mozilla/5.0"
            }
        )

        data = r.json()

        return float(data["price"])


    except Exception as e:

        return None
