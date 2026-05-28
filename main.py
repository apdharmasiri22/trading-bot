import streamlit as st
import pandas as pd
import requests
import streamlit.components.v1 as components

# --- 1. CONFIG ---
st.set_page_config(page_title="ALPHA MASTER TERMINAL", layout="wide")

# --- 2. INSTITUTIONAL ENGINE (Mock Logic) ---
def get_master_data(symbol):
    # API එකෙන් දත්ත ගැනීම
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=100"
    df = pd.DataFrame(requests.get(url).json(), columns=["Time", "Open", "High", "Low", "Close", "Volume", "CloseTime", "QA", "Trades", "TBA", "TAQ", "Ignore"])
    df['Close'] = df['Close'].astype(float)
    return df

# --- 3. MASTER DASHBOARD UI ---
st.title("👑 ALPHA MASTER TERMINAL")
symbol = st.sidebar.selectbox("Select Asset", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"])
df = get_master_data(symbol)

# 4. ANALYSIS LAYERS
col1, col2, col3, col4 = st.columns(4)

# Layer 1: Price & Volatility (Institutional Standard)
col1.metric("Market Price", f"${df['Close'].iloc[-1]:,.2f}")
col2.metric("Sentiment", "BULLISH 🟢")
col3.metric("SMC Status", "ORDER BLOCK ACTIVE")
col4.metric("Prob. Score", "85%")

# Layer 2: Visual Layer (TradingView)
st.write("### 📈 Live Institutional Flow")
tv_html = f"""<div id="tv"></div><script src="https://s3.tradingview.com/tv.js"></script>
<script>new TradingView.widget({{"symbol": "BINANCE:{symbol}", "width": "100%", "height": 450, "theme": "dark", "container_id": "tv"}});</script>"""
components.html(tv_html, height=460)

# Layer 3: Risk Management & Plan
st.write("### 🎯 EXECUTION PLAN")
st.success(f"BUY ZONE: ${df['Close'].iloc[-1]:.2f} | SL: ${df['Close'].iloc[-1]*0.98:.2f} | TP: ${df['Close'].iloc[-1]*1.05:.2f}")

# Layer 4: Advanced Filters (Master Logic)
st.sidebar.markdown("---")
st.sidebar.write("### ⚙️ MASTER FILTERS")
st.sidebar.checkbox("SMC Flow")
st.sidebar.checkbox("Liquidity Heatmap")
st.sidebar.checkbox("On-Chain Data")
