import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from binance_feed import get_top_coins, get_price


# =========================
# 🏁 APP CONFIG
# =========================
st.set_page_config(layout="wide")
st.title("📊 SMC Quantum Dashboard - Part 2")


# =========================
# 🔁 AUTO REFRESH (STABLE)
# =========================
st_autorefresh(interval=60000, key="refresh")  # 60 sec (safer than 30s)


# =========================
# 🪙 LIVE COINS (BINANCE)
# =========================
coins = get_top_coins(100)

st.write("DEBUG COIN COUNT:", len(coins))

if not coins:
    st.error("No coins loaded from Binance API")
    st.stop()

coin = st.selectbox("🔍 Select Coin (Live Binance)", coins)

st.markdown(f"### Selected: {coin}")


# =========================
# 💰 LIVE PRICE
# =========================
price = get_price(coin)

if price is not None:
    st.success(f"💰 Live Price: {price}")
else:
    st.error("Price loading failed (API / Network / Symbol issue)")


# =========================
# 🧠 PLACEHOLDERS
# =========================
st.subheader("🧠 SMC Engine")
st.info("Coming in Part 3")

st.subheader("🎯 Signal Engine")
st.info("Coming in Part 4")

st.subheader("📊 Accuracy System")
st.info("Coming in Part 6")
