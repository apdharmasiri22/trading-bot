import requests
import pandas as pd
import streamlit as st


COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"


@st.cache_data(ttl=30)
def get_top_coins(limit=200):

    try:

        params = {
            "vs_currency": "usd",
            "order": "volume_desc",
            "per_page": limit,
            "page": 1
        }

        r = requests.get(
            COINGECKO_URL,
            params=params,
            timeout=10
        )

        data = r.json()

        coins = []

        for item in data:

            symbol = item["symbol"].upper()

            coins.append(
                symbol + "USDT"
            )

        return coins


    except Exception as e:

        st.error(f"Data Error: {e}")
        return []



@st.cache_data(ttl=10)
def get_price(symbol):

    try:

        coin = symbol.replace("USDT","").lower()

        url = (
        f"https://api.coingecko.com/api/v3/simple/price"
        f"?ids={coin}&vs_currencies=usd"
        )

        data = requests.get(
            url,
            timeout=10
        ).json()


        return data[coin]["usd"]


    except:

        return None
