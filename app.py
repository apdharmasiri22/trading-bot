import streamlit as st
from modules.data_fetcher import get_ohlcv
from modules.indicators import add_indicators # අලුතින් ඉම්පෝට් කළා

st.title("Asaa Trading Dashboard")

symbol = st.selectbox("Select Coin", ["BTC/USDT", "ETH/USDT"])
df = get_ohlcv(symbol)

if not df.empty:
    # Indicators එකතු කරමු
    df = add_indicators(df)
    
    st.write(f"Indicators added for {symbol}")
    st.write(df.tail()) # දැන් බලන්න EMA, RSI, BB තීරු ඇවිල්ලා තියෙනවද කියලා
else:
    st.warning("Data not found.")
