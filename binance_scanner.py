import requests
import pandas as pd
import streamlit as st

BINANCE_URL = "https://api1.binance.com/api/v3/ticker/24hr"

def get_market_data():

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(BINANCE_URL, headers=headers, timeout=10)

        st.write("STATUS:", r.status_code)
        st.write("RAW SAMPLE:", r.text[:150])

        if r.status_code != 200:
            return pd.DataFrame()

        data = r.json()

        coins = []

        for c in data:

            if not c.get("symbol", "").endswith("USDT"):
                continue

            coins.append({
                "Symbol": c["symbol"],
                "Price": float(c.get("lastPrice", 0)),
                "Change %": float(c.get("priceChangePercent", 0)),
                "Volume": float(c.get("volume", 0))
            })

        return pd.DataFrame(coins)

    except Exception as e:
        st.error(f"ERROR: {e}")
        return pd.DataFrame()
