import streamlit as st
import os

st.write("FILES:", os.listdir())
import streamlit as st
from streamlit_autorefresh import st_autorefresh

import binance_feed

get_top_coins = binance_feed.get_top_coins
get_price = binance_feed.get_price
get_candles = binance_feed.get_candles
from smc_engine import SMCEngine
from score_engine import ScoreEngine

# =========================
# APP CONFIG
# =========================
st.set_page_config(
    page_title="SMC Quantum Dashboard",
    layout="wide"
)

# =========================
# AUTO REFRESH
# =========================
st_autorefresh(interval=30000, key="refresh")

# =========================
# INIT ENGINES
# =========================
smc = SMCEngine()
score_engine = ScoreEngine()

# =========================
# HEADER
# =========================
st.title("📊 SMC Quantum Dashboard")
st.caption("Smart Money Concepts + Binance Live Data")

st.markdown("---")

# =========================
# LOAD COINS
# =========================
coins = get_top_coins(200)

if not coins:
    st.error("❌ Market data not loaded.")
    st.stop()

# =========================
# COIN SELECTOR
# =========================
coin = st.selectbox("🔍 Select Coin (Live Binance)", coins)

st.markdown(f"### 🪙 Selected Coin : {coin}")

# =========================
# PRICE
# =========================
price = get_price(coin)

if price:
    st.success(f"💰 Live Price : {price}")
else:
    st.error("Price loading failed")

st.markdown("---")

# =========================
# CANDLES + SMC ENGINE
# =========================
candles = get_candles(coin)

if candles:
    smc_result = smc.update(candles)

    analysis = {
        "structure_score": smc_result.get("structure_score", 0),
        "liquidity_score": 15,
        "entry_score": 15,
        "pattern_score": 10,
        "wave_score": 5,
        "timing_score": 5
    }

    final_result = score_engine.update_scores(analysis)

    # =========================
    # SMC OUTPUT
    # =========================
    st.subheader("🧠 SMC Analysis")

    st.write("📊 Structure:", smc_result.get("structure", "N/A"))

    st.markdown("### 🎯 Final Decision")

    st.success(f"""
Score: {final_result['total_score']}

{final_result['decision']}
""")
else:
    st.warning("No candle data available")

st.markdown("---")

# =========================
# TRADINGVIEW CHART
# =========================
st.subheader("📈 TradingView Chart")

symbol = f"BINANCE:{coin}"

html_code = f"""
<div id="tradingview_chart"></div>

<script src="https://s3.tradingview.com/tv.js"></script>

<script>
new TradingView.widget({{
"width":1000,
"height":600,
"symbol":"{symbol}",
"interval":"15",
"timezone":"Etc/UTC",
"theme":"dark",
"style":"1",
"locale":"en",
"container_id":"tradingview_chart"
}});
</script>
"""

st.components.v1.html(html_code, height=650)

st.markdown("---")

# =========================
# FUTURE MODULES
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🧠 SMC Engine")
    st.info("Active - Structure Analysis")

with col2:
    st.subheader("🎯 Signal Engine")
    st.info("Coming Next (BOS / MSS / Entry)")

with col3:
    st.subheader("📊 Accuracy")
    st.info("Coming Soon")

st.markdown("---")
st.caption("SMC Quantum Dashboard v1.3 (Fixed Build)")
