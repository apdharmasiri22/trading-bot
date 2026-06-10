from smc_pro import apply_smc_pro
import streamlit as st
import time
from scanner import get_market_data
from smc_engine import apply_smc

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(page_title="SMC Dashboard", layout="wide")

st.title("📊 SMC AI Trading Dashboard")

# ======================
# CACHE SYSTEM
# ======================
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.time = 0

CACHE_TIME = 20

def load_data():

    if st.session_state.df is not None and time.time() - st.session_state.time < CACHE_TIME:
        return st.session_state.df

    df = get_market_data()

    st.session_state.df = df
    st.session_state.time = time.time()

    return df


df = load_data()

# ======================
# CHECK DATA
# ======================
if df.empty:
    st.error("Binance/CoinGecko data loading failed")
    st.stop()

# ======================
# FILTER UI
# ======================
col1, col2, col3 = st.columns(3)

with col1:
    min_volume = st.number_input("Minimum Volume", value=1000000)

with col2:
    change = st.number_input("Min Change %", value=0.0)

with col3:
    limit = st.slider("Show Coins", 5, 50, 20)

# ======================
# FILTER DATA
# ======================
filtered = df[
    (df["Volume"] >= min_volume) &
    (df["Change %"] >= change)
]

filtered = filtered.sort_values("Volume", ascending=False)

# ======================
# 🧠 SMC ENGINE APPLY
# ======================
filtered = apply_smc_pro(filtered)
snipers = filtered[
    (filtered["SMC Score"] >= 70) &
    (filtered["Volume"] > filtered["Volume"].median())
]

# ======================
# TABLE OUTPUT
# ======================
st.dataframe(
    filtered.head(limit),
    use_container_width=True
)

st.divider()

# ======================
# COIN SELECTOR
# ======================
st.subheader("🎯 Coin Select")

coin = None
coin_data = None

if len(filtered) > 0:

    coin = st.selectbox(
        "Choose Coin",
        filtered["Symbol"].tolist()
    )

    st.success(f"Selected: {coin}")

    # 👉 pre-calculate coin data (IMPORTANT FIX)
    coin_data = filtered[filtered["Symbol"] == coin]

else:
    st.warning("No coins found")

st.divider()

# ======================
# 🧠 SMART COIN ANALYSIS
# ======================
st.subheader("🧠 Smart Coin Analysis")

if coin_data is not None and not coin_data.empty:

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("SMC Score", coin_data["SMC Score"].values[0])

    with col2:
        st.metric("Change %", coin_data["Change %"].values[0])

    with col3:
        st.metric("Volume", coin_data["Volume"].values[0])

    st.write(coin_data)

else:
    st.info("Select a coin to view analysis")

# ======================
# 🧠 SMC PRO ANALYSIS
# ======================
st.subheader("🧠 SMC PRO Analysis")

if coin is not None:
    selected = filtered[filtered["Symbol"] == coin]
    st.write(selected)
    
# ======================
# SMC DETAIL VIEW
# ======================
    st.subheader("📊 SMC Signal View")

    selected = filtered[filtered["Symbol"] == coin]

    st.write(selected)

else:
    st.warning("No coins match filters")
