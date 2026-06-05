import requests
import streamlit as st


URL = "https://min-api.cryptocompare.com/data/top/mktcapfull"


@st.cache_data(ttl=60)
def get_top_coins(limit=200):

    try:

        params = {
            "tsym": "USD",
            "limit": limit
        }


        r = requests.get(
            URL,
            params=params,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )


        data = r.json()


        coins = []


        for item in data.get("Data", []):

            symbol = item["CoinInfo"]["Name"]

            coins.append(
                symbol + "USDT"
            )


        return coins


    except Exception as e:

        st.error(f"Data Error: {e}")
        return []



@st.cache_data(ttl=15)
def get_price(symbol):

    try:

        coin = symbol.replace(
            "USDT",
            ""
        )


        url = (
            "https://min-api.cryptocompare.com/data/price"
        )


        params = {
            "fsym": coin,
            "tsyms": "USD"
        }


        r = requests.get(
            url,
            params=params,
            timeout=10
        )


        data = r.json()


        return data.get("USD")


    except:

        return None
