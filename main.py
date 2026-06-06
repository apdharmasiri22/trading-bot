import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from binance_feed import get_top_coins, get_price

st.set_page_config(layout="wide")

st.title("📊 SMC Quantum Dashboard - Part 2")

# 🔁 refresh safe
st_autorefresh(interval=30000, key="refresh")

# =========================
# 🪙 LIVE COINS (BINANCE)
# =========================
coins = get_top_coins(100)
st.write("DEBUG COIN COUNT:", len(coins))

coin = st.selectbox("🔍 Select Coin (Live Binance)", coins)

st.markdown(f"### Selected: {coin}")

# =========================
# 💰 LIVE PRICE
# =========================
price = get_price(coin)

if price:
    st.success(f"💰 Live Price: {price}")
else:
    st.error("Price loading failed")

# =========================
# 📊 PLACEHOLDER (Next Parts)
# =========================
st.subheader("🧠 SMC Engine")
st.info("Coming in Part 3")

st.subheader("🎯 Signal Engine")
st.info("Coming in Part 4")

st.subheader("📊 Accuracy System")
st.info("Coming in Part 6")
