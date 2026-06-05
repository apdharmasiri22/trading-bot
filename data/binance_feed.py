import requests
import streamlit as st


COINGECKO_MARKETS = "https://api.coingecko.com/api/v3/coins/markets"


@st.cache_data(ttl=60)
def get_top_coins(limit=200):

    try:

        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": "false"
        }


        r = requests.get(
            COINGECKO_MARKETS,
            params=params,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )


        data = r.json()


        # check response
        if not isinstance(data, list):
            st.error(f"CoinGecko response error: {data}")
            return []


        coins = []


        for item in data:

            if isinstance(item, dict):

                symbol = item.get("symbol")

                if symbol:
                    coins.append(
                        symbol.upper() + "USDT"
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
        ).lower()


        url = (
            "https://api.coingecko.com/api/v3/simple/price"
        )


        params = {
            "ids": coin,
            "vs_currencies": "usd"
        }


        r = requests.get(
            url,
            params=params,
            timeout=10,
            headers={
                "User-Agent":"Mozilla/5.0"
            }
        )


        data = r.json()


        if coin in data:
            return data[coin]["usd"]


        return None


    except:

        return None
