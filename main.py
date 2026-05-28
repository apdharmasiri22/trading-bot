import streamlit as st
import pandas as pd
import requests
import streamlit.components.v1 as components

# --- PAGE CONFIG ---
st.set_page_config(page_title="ALPHA MASTER TERMINAL", layout="wide")
st.markdown("""<style>.stApp {background-color: #0d1117; color: white;}</style>""", unsafe_allow_html=True)

# --- DATA ENGINE ---
@st.cache_data(ttl=60)
def get_binance_data(symbol, interval="15m"):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
    try:
        res = requests.get(url).json()
        df = pd.DataFrame(res, columns=["Time", "Open", "High", "Low", "Close", "Volume", "CloseTime", "QA", "Trades", "TBA", "TAQ", "Ignore"])
        for col in ["Open", "High", "Low", "Close", "Volume"]: df[col] = df[col].astype(float)
        return df
    except: return None

# --- SIDEBAR & CONTROL ---
st.sidebar.title("👑 TERMINAL CONTROL")
symbol = st.sidebar.text_input("Search Coin (e.g. BTCUSDT):", "BTCUSDT").upper()
timeframe = st.sidebar.selectbox("Timeframe:", ["5m", "15m", "1h", "4h"])

# --- MAIN DASHBOARD ---
st.title(f"📊 {symbol} | Institutional Terminal")
df = get_binance_data(symbol, timeframe)

if df is not None and not df.empty:
    # Calculations
    last_price = df['Close'].iloc[-1]
    rsi = 100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff() > 0, 0).rolling(14).mean() / (-df['Close'].diff().where(df['Close'].diff() < 0, 0)).rolling(14).mean())))
    
    # 1. Metrics Area
    col1, col2, col3 = st.columns(3)
    col1.metric("Price", f"${last_price:,.2f}")
    col2.metric("RSI (14)", f"{rsi.iloc[-1]:.2f}")
    col3.metric("Volume (24h)", f"{df['Volume'].sum():,.0f}")

    # 2. TradingView Chart
    tv_html = f"""<div id="tv"></div><script src="https://s3.tradingview.com/tv.js"></script>
    <script>new TradingView.widget({{"symbol": "BINANCE:{symbol}", "width": "100%", "height": 500, "theme": "dark", "container_id": "tv"}});</script>"""
    components.html(tv_html, height=510)

    # 3. Risk Calculator
    st.markdown("---")
    st.write("### 🛡️ Risk & Position Calculator")
    c1, c2, c3 = st.columns(3)
    balance = c1.number_input("Balance ($):", 100, 100000, 1000)
    risk_pct = c2.slider("Risk Per Trade (%):", 0.1, 5.0, 1.0)
    leverage = c3.slider("Leverage (x):", 1, 50, 10)
    
    st.success(f"Position Size: ${(balance * (risk_pct/100)) * leverage:,.2f} | Stop Loss Distance suggested: ${last_price * 0.02:,.2f}")

else:
    st.error("දත්ත ලැබී නැත. කරුණාකර නිවැරදි Symbol එක (උදා: BTCUSDT) ඇතුලත් කරන්න.")
