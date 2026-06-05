import streamlit as st
from streamlit_autorefresh import st_autorefresh

from binance_feed import get_top_coins, get_price, get_candles
from smc_engine import SMCEngine
from score_engine import ScoreEngine

# =========================
# INIT
# =========================
smc = SMCEngine()
score_engine = ScoreEngine()

st.set_page_config(page_title="SMC Quantum Dashboard", layout="wide")
st_autorefresh(interval=30000, key="refresh")

st.title("📊 SMC Quantum Dashboard")
st.caption("Smart Money Concepts + Binance Live Data")

st.markdown("---")

# =========================
# COINS
# =========================
coins = get_top_coins(100)

if not coins:
    st.error("❌ Market data not loaded.")
    st.stop()

coin = st.selectbox("🔍 Select Coin", coins)

st.markdown(f"### 🪙 {coin}")

# =========================
# PRICE
# =========================
price = get_price(coin)

if price:
    st.success(f"💰 Price: {price}")
else:
    st.error("Price loading failed")

# =========================
# CANDLES
# =========================
candles = get_candles(coin)

if candles:

    smc_result = smc.update(candles)

    analysis = {
        "structure_score": smc_result.get("structure_score", 0),
        "liquidity_score": 10,
        "entry_score": 10,
        "pattern_score": 10,
        "wave_score": 5,
        "timing_score": 5
    }

    final_result = score_engine.update_scores(analysis)

    st.subheader("🧠 SMC Analysis")
    st.write("Structure:", smc_result.get("structure"))

    st.success(f"""
Score: {final_result['total_score']}

{final_result['decision']}
""")

else:
    st.warning("No candle data available")

# =========================
# CHART
# =========================
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
"theme":"dark",
"container_id":"tradingview_chart"
}});
</script>
"""

st.components.v1.html(html_code, height=650)
