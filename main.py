import streamlit as st
import os

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
coins = get_top_coins(100)

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
@st.cache_data(ttl=15)
def get_price(symbol):

    try:
        # 🧠 FIX: remove USDT properly
        coin = symbol.replace("USDT", "")

        url = "https://min-api.cryptocompare.com/data/price"

        params = {
            "fsym": coin,
            "tsyms": "USD"
        }

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        return data.get("USD")

    except Exception as e:
        return None

# =========================
# CANDLES + SMC ENGINE
# =========================
def get_candles(symbol, limit=50):

    try:
        coin = symbol.replace("USDT", "")

        url = "https://min-api.cryptocompare.com/data/v2/histominute"

        params = {
            "fsym": coin,
            "tsym": "USD",
            "limit": limit
        }

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        # 🧠 SAFE CHECK
        if "Data" not in data:
            return []

        inner = data["Data"]

        if "Data" not in inner:
            return []

        raw = inner["Data"]

        candles = []

        for c in raw:
            if isinstance(c, dict):
                candles.append({
                    "open": float(c.get("open", 0)),
                    "high": float(c.get("high", 0)),
                    "low": float(c.get("low", 0)),
                    "close": float(c.get("close", 0))
                })

        return candles

    except Exception as e:
        return []

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
