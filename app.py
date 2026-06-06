import streamlit as st
from modules.data_fetcher import get_ohlcv

st.title("Asaa Trading Dashboard - Part 2")

# කොයින් ලිස්ට් එක (ඔයාට ඕන කොයින් ටික මෙතන දාගන්න)
coins = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
selected_coin = st.selectbox("Select a Coin", coins)

if selected_coin:
    # දත්ත ගන්නා කොටස
    df = get_ohlcv(selected_coin, timeframe='1h', limit=50)
    
    if not df.empty:
        st.write(f"Displaying data for: {selected_coin}")
        st.table(df.head()) # දත්ත ටික table එකක පේනවා
        st.line_chart(df['close']) # නිකමට ප්‍රයිස් චාට් එක
    else:
        st.warning("Data fetch failed!")
