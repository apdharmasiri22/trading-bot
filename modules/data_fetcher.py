import ccxt
import pandas as pd
import streamlit as st

# Binance Public API Setup (අපි Public දත්ත විතරක් ගන්න නිසා Keys ඕන නෑ)
exchange = ccxt.binance({
    'enableRateLimit': True,
})

@st.cache_data(ttl=60) # මිනිත්තුවකට සැරයක් විතරක් data refresh වෙන්න (Speed එකට)
def get_ohlcv(symbol, timeframe='1h', limit=100):
    """
    symbol: 'BTC/USDT' වගේ කොයින් එකක්
    timeframe: '15m', '1h', '4h' වගේ
    """
    try:
        # දත්ත ලබාගැනීම
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        
        # DataFrame එකක් විදියට හැඩගැන්වීම
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Timestamp එක ලස්සන දින වකවානුවකට හරවමු
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df
    
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()
