import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import numpy as np

# අපේ files import කරගැනීම
from data.binance_feed import get_top_coins, get_price
from engine.smc_logic import analyze_market_structure, find_liquidity_zones

st.set_page_config(layout="wide")

st.title("📊 SMC Quantum Dashboard - Part 3")

# 🔁 30 seconds refresh
st_autorefresh(interval=30000, key="refresh")

# =========================
# 🪙 LIVE COINS (BINANCE)
# =========================
coins = get_top_coins(20)
coin = st.selectbox("🔍 Select Coin (Live Binance)", coins)

st.markdown(f"### Selected: {coin}")

# Price display
price = get_price(coin)
if price:
    st.success(f"💰 Live Price: {price}")
else:
    st.error("Price loading failed")

st.markdown("---")

# =========================
# 🧠 SMC ENGINE
# =========================
st.subheader("🧠 SMC Engine")

# Testing සඳහා mock data (මෙතනින් එහාට අපි මේක live data වලට මාරු කරනවා)
mock_data = pd.DataFrame({
    'close': np.random.rand(20) * 100,
    'high': np.random.rand(20) * 105,
    'low': np.random.rand(20) * 95
})

# Logic එක call කිරීම
bias = analyze_market_structure(mock_data)
liq = find_liquidity_zones(mock_data)

col1, col2 = st.columns(2)
col1.metric("Market Bias", bias)
col2.write(f"Liquidity Zones: {liq}")

st.markdown("---")

# =========================
# 🎯 FUTURE SECTIONS
# =========================
st.subheader("🎯 Signal Engine")
st.info("Coming in Part 4")

st.subheader("📊 Accuracy System")
st.info("Coming in Part 6")
