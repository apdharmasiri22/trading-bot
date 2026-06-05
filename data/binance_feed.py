import ccxt
import pandas as pd
import streamlit as st


exchange = ccxt.binance({
    "enableRateLimit": True
})


@st.cache_data(ttl=30)
def get_top_coins(limit=200):

    try:
        markets = exchange.load_markets()

        coins = []

        for symbol, info in markets.items():

            if symbol.endswith("/USDT") and info.get("active"):

                coins.append(
                    symbol.replace("/", "")
                )

        return coins[:limit]

    except Exception as e:
        st.error(f"CCXT Error: {e}")
        return []



@st.cache_data(ttl=10)
def get_price(symbol):

    try:

        pair = symbol.replace("USDT", "/USDT")

        ticker = exchange.fetch_ticker(pair)

        return ticker["last"]

    except:

        return None
