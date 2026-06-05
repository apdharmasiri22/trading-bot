import streamlit as st
from streamlit_autorefresh import st_autorefresh
from data.binance_feed import get_top_coins, get_price

# =========================
# 🏆 APP CONFIG
# =========================
APP_NAME = "SMC Quantum Trading Dashboard"
st.set_page_config(page_title=APP_NAME, layout="wide")

# 🔁 Auto refresh (30 sec)
st_autorefresh(interval=30000, key="refresh")

# =========================
# HEADER
# =========================
st.title(f"📊 {APP_NAME}")
st.markdown("Smart Money Concepts + Liquidity Based Trading System")
st.markdown("---")

# =========================
# 🪙 LIVE BINANCE COIN SELECTOR
# =========================
coins = get_top_coins(20)
coin = st.selectbox("🔍 Select Coin (Live from Binance)", coins)

st.markdown(f"### 📌 Selected Coin: `{coin}`")

# =========================
# 💰 LIVE PRICE
# =========================
price = get_price(coin)
if price:
    st.success(f"💰 Live Price: {price}")
else:
    st.error("Price loading failed")

st.markdown("---")

# =========================
# 📈 TRADINGVIEW CHART
# =========================
st.subheader("📈 TradingView Chart")

symbol = f"BINANCE:{coin}"

html_code = f"""
<div class="tradingview-widget-container">
  <div id="tradingview_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "width": "100%",
    "height": 500,
    "symbol": "{symbol}",
    "interval": "15",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "allow_symbol_change": true,
    "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""
st.components.v1.html(html_code, height=550)

st.markdown("---")

# =========================
# 🧠 ANALYSIS PANEL (Engine ready)
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 Market Bias")
    st.info("⏳ Waiting for SMC Engine (Part 3)")

with col2:
    st.subheader("🎯 Entry Zone")
    st.warning("FVG / Order Block will appear here")

with col3:
    st.subheader("⚠️ Risk (SL / TP)")
    st.error("TP1 / TP2 / SL pending engine")

st.markdown("---")

# =========================
# 📌 FOOTER
# =========================
st.caption("SMC Quantum Trading Dashboard v1.0 - Integrated Version")
