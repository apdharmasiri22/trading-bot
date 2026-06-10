import streamlit as st
import time
from binance_scanner import get_market_data

st.set_page_config(page_title="SMC AI Dashboard", layout="wide")

st.title("📊 SMC AI Trading Dashboard")

# =========================
# LOAD DATA FIRST
# =========================
df = get_market_data()

# =========================
# CHECK AFTER LOADING
# =========================
if df is None or df.empty:
    st.error("Binance data loading failed")
    st.stop()

# =========================
# FILTER UI
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
