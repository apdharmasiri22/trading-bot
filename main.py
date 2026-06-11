import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import market_scanner as ms
from smc_engine import apply_smc
from smc_pro import apply_smc_pro
# ======================
# SAFE CACHE INIT
# ======================
if "df" not in st.session_state:
    st.session_state.df = None
    st.session_state.time = 0


# ======================
# LOAD DATA (BINANCE ONLY)
# ======================
def load_data(symbol):

    if (
        st.session_state.df is not None
        and time.time() - st.session_state.time < CACHE_TIME
    ):
        return st.session_state.df

    df = get_market_data(symbol)

    if df is None or df.empty:
        return pd.DataFrame()

    st.session_state.df = df
    st.session_state.time = time.time()

    return df


# ======================
# COIN LIST
# ======================
coins = get_top_coins()
coin = st.selectbox(
    "Select Coin",
    [c if c.endswith("USDT") else c + "USDT" for c in coins]
)

# ======================
# LOAD DATA
# ======================
df = load_data(coin)

st.write("DEBUG ROWS:", len(df))

if df.empty:
    st.error("No Binance data")
    st.stop()

# ======================
# FILTER UI
# ======================
col1, col2, col3 = st.columns(3)

with col1:
    min_volume = st.number_input("Minimum Volume", value=0.0)

with col2:
    change = st.number_input("Min Change %", value=-100.0)

with col3:
    limit = st.slider("Show Rows", 5, 50, 20)


# ======================
# FILTER (SAFE)
# ======================
filtered = df.copy()


# ======================
# APPLY SMC ENGINE (ONLY ONCE)
# ======================
filtered = apply_smc(filtered)

# ======================
# APPLY PRO SIGNALS
# ======================
filtered = apply_smc_pro(filtered)

filtered = filtered.sort_values("Volume", ascending=False)

# ======================
# TABLE
# ======================
st.dataframe(filtered.head(limit), use_container_width=True)

st.divider()

# ======================
# ANALYSIS
# ======================
st.subheader("🧠 Latest Signal")

if not filtered.empty:
    st.write(filtered.tail(1))
