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

st.set_page_config(page_title="SMC Dashboard", layout="wide")
st_autorefresh(interval=30000, key="refresh")

st.title("📊 SMC Quantum Dashboard")
st.caption("Smart Money Concepts System")

st.markdown("---")


# =========================
# COINS (200)
# =========================
coins = get_top_coins(200)

if not coins:
    st.error("Market data not loaded.")
    st.stop()


# =========================
# SELECT 10 COINS
# =========================
selected_coins = st.multiselect(
    "🔍 Select coins (max 10)",
    coins,
    max_selections=10
)

st.markdown("---")


# =========================
# ANALYSIS
# =========================
for coin in selected_coins:

    price = get_price(coin)
    candles = get_candles(coin)

    if not candles:
        continue

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

    st.subheader(f"🪙 {coin}")

    if price:
        st.write("💰 Price:", price)

    st.write("📊 Structure:", smc_result.get("structure"))

    st.success(f"""
Score: {final_result['total_score']}
Decision: {final_result['decision']}
""")

    st.markdown("---")
