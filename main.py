import streamlit as st
import time
from scanner import get_market_data

st.set_page_config(page_title="SMC Dashboard", layout="wide")

st.title("📊 SMC AI Trading Dashboard")

# ======================
# CACHE (slow API avoid)
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
    st.error("Data load වෙන්නේ නෑ (API issue)")
    st.stop()

# ======================
# FILTERS
# ======================
col1, col2, col3 = st.columns(3)

with col1:
    min_volume = st.number_input("Minimum Volume", value=1000000)

with col2:
    change = st.number_input("Min Change %", value=0.0)

with col3:
    limit = st.slider("Show Coins", 5, 50, 20)

filtered = df[
    (df["Volume"] >= min_volume) &
    (df["Change %"] >= change)
]

filtered = filtered.sort_values("Volume", ascending=False)

st.dataframe(filtered.head(limit), use_container_width=True)

# ======================
# COIN SELECT
# ======================
st.subheader("🎯 Coin Select")

coin = st.selectbox("Coin එක තෝරන්න", filtered["Symbol"].tolist())

st.success("Selected: " + coin)
