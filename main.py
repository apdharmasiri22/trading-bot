import streamlit as st
from streamlit_autorefresh import st_autorefresh

from data.binance_feed import get_top_coins, get_price, get_candles
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
st_autorefresh(
    interval=30000,
    key="refresh"
)


# =========================
# HEADER
# =========================
st.title("📊 SMC Quantum Dashboard")
st.caption("Smart Money Concepts + Binance Live Data")


st.markdown("---")


# =========================
# GET LIVE BINANCE COINS
# =========================

coins = get_top_coins(200)


if not coins:
    st.error(
        "❌ Market data not loaded."
    )
    st.stop()


# =========================
# COIN SELECTOR
# =========================

coin = st.selectbox(
    "🔍 Select Coin (Live Binance)",
    coins
)


st.markdown(
    f"### 🪙 Selected Coin : {coin}"
)


# =========================
# PRICE
# =========================

price = get_price(coin)


if price:

    st.success(
        f"💰 Live Price : {price}"
    )

else:

    st.error(
        "Price loading failed"
    )


st.markdown("---")

# =========================
# GET CANDLES
# =========================
candles = get_candles(coin)

# =========================
# ENGINE 1 - SMC STRUCTURE
# =========================
smc_result = smc.update(candles)

# =========================
# ENGINE 2 - BUILD ANALYSIS DICT
# =========================
analysis = {
    "structure_score": smc_result["structure_score"],
    "liquidity_score": 15,   # placeholder (next step)
    "entry_score": 15,       # placeholder
    "pattern_score": 10,     # placeholder
    "wave_score": 5,         # placeholder
    "timing_score": 5        # placeholder
}

# =========================
# SCORE ENGINE
# =========================
final_result = score_engine.update_scores(analysis)

# =========================
# UI DISPLAY
# =========================
st.markdown("### 🧠 SMC ANALYSIS")

st.write("📊 Structure:", smc_result["structure"])

st.markdown("### 🎯 FINAL DECISION")
st.success(f"""
Score: {final_result['total_score']}

{final_result['decision']}
""")


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


st.components.v1.html(
    html_code,
    height=650
)


st.markdown("---")


# =========================
# FUTURE ENGINES
# =========================


col1,col2,col3 = st.columns(3)


with col1:

    st.subheader("🧠 SMC Engine")
    st.info(
        "Coming Part 3\n\nBOS / MSS / Liquidity"
    )


with col2:

    st.subheader("🎯 Signal Engine")
    st.info(
        "Coming Part 4\n\nEntry TP SL"
    )


with col3:

    st.subheader("📊 Accuracy")
    st.info(
        "Coming Part 6\n\nWin Rate + Learning"
    )


st.markdown("---")

st.caption(
    "SMC Quantum Dashboard v1.2"
)
