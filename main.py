import streamlit as st
from streamlit_autorefresh import st_autorefresh

from binance_feed import get_top_coins, get_price, get_candles

# dummy engines (ඔයාගේ ඒවා use කරන්න පුළුවන්)
class SMCEngine:
    def update(self, candles):
        return {
            "structure": "Bullish",
            "structure_score": 20
        }

class ScoreEngine:
    def update_scores(self, a):
        total = sum(a.values())
        return {
            "total_score": total,
            "decision": "BUY" if total > 40 else "WAIT"
        }


smc = SMCEngine()
score_engine = ScoreEngine()

st.set_page_config(page_title="SMC Dashboard", layout="wide")
st_autorefresh(interval=30000, key="refresh")

st.title("📊 SMC Quantum Dashboard")

# ================= COINS =================
coins = get_top_coins(200)

if not coins:
    st.error("No market data")
    st.stop()

selected = st.multiselect(
    "Select coins (max 10)",
    coins,
    max_selections=10
)

if not selected:
    st.info("Select coins")
    st.stop()

# ================= ANALYSIS =================
for coin in selected:

    price = get_price(coin)
    candles = get_candles(coin)

    if not candles:
        continue

    smc_result = smc.update(candles)

    analysis = {
        "structure_score": smc_result["structure_score"],
        "liquidity_score": 10,
        "entry_score": 10,
        "pattern_score": 10,
        "wave_score": 5,
        "timing_score": 5
    }

    final = score_engine.update_scores(analysis)

    st.subheader(coin)

    if price:
        st.write("Price:", price)

    st.write("Structure:", smc_result["structure"])

    st.success(f"""
Score: {final['total_score']}
Decision: {final['decision']}
""")

    st.markdown("---")
