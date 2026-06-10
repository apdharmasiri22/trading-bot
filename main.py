if df is None or df.empty:
    st.error("Binance API not reachable (try again in few seconds)")
    st.stop()
    
import streamlit as st
import time
from binance_scanner import get_market_data

# =========================
# ⚙️ CONFIG
# =========================
st.set_page_config(page_title="SMC AI Dashboard", layout="wide")

st.title("📊 SMC AI Trading Dashboard")

# =========================
# 💾 CACHE (ANTI-SPAM)
# =========================
if "df_cache" not in st.session_state:
    st.session_state.df_cache = None
    st.session_state.last_fetch = 0

CACHE_TIME = 15  # seconds

def load_data():

    if (
        st.session_state.df_cache is not None
        and time.time() - st.session_state.last_fetch < CACHE_TIME
    ):
        return st.session_state.df_cache

    df = get_market_data()

    st.session_state.df_cache = df
    st.session_state.last_fetch = time.time()

    return df


df = load_data()

# =========================
# 🚨 CHECK DATA
# =========================
if df.empty:
    st.error("Binance data loading failed")
    st.stop()

# =========================
# FILTERS
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    min_volume = st.number_input("Minimum Volume", value=1000000)

with col2:
    change = st.number_input("Min Change %", value=0.0)

with col3:
    limit = st.slider("Show Coins", 5, 50, 20)

# =========================
# FILTER DATA
# =========================
filtered = df[
    (df["Volume"] >= min_volume) &
    (df["Change %"] >= change)
]

filtered = filtered.sort_values("Volume", ascending=False)

st.dataframe(filtered.head(limit), use_container_width=True)

st.divider()

# =========================
# SELECT COIN
# =========================
st.subheader("🎯 Select Coin")

if len(filtered) > 0:

    coin = st.selectbox(
        "Choose Coin",
        filtered["Symbol"].tolist()
    )

    st.success(f"Selected: {coin}")

else:
    st.warning("No coins match filters")
