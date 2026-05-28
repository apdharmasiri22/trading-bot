import numpy as np
import pandas as pd
import requests
import streamlit as st
import time

# Page Configuration
st.set_page_config(
    page_title="ALPHA TRADING TERMINAL v4.5",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE ---
if 'signals_history' not in st.session_state:
    st.session_state.signals_history = []

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    div[data-testid="stMetricValue"] { color: #ffb703 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIG ---
COIN_SYMBOLS = {
    "BTCUSDT": "₿ BTCUSDT", "ETHUSDT": "♦️ ETHUSDT", "SOLUSDT": "☀️ SOLUSDT", 
    "BNBUSDT": "🔶 BNBUSDT", "XRPUSDT": "💧 XRPUSDT", "ADAUSDT": "₳ ADAUSDT"
}
SCAN_COINS = list(COIN_SYMBOLS.keys())

# --- FUNCTIONS ---
@st.cache_data(ttl=60)
def get_crypto_data(symbol, interval, limit=50):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVol', 'NumTrades', 'TakerBuyBase', 'TakerBuyQuote', 'Ignore'])
            df[['Close', 'Open', 'High', 'Low', 'Volume']] = df[['Close', 'Open', 'High', 'Low', 'Volume']].astype(float)
            return df
        return None
    except: return None

def calculate_ema(series, period): return series.ewm(span=period, adjust=False).mean()

def calculate_cvd_delta(df):
    if df is None or len(df) < 5: return 0
    return (df['Volume'] * ((df['Close'] - df['Open']) / (df['High'] - df['Low'] + 1e-10))).iloc[-5:].sum()

def send_telegram_alert(token, chat_id, message):
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try: requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        except: pass

def analyze_coin(coin, htf, ltf):
    df_htf = get_crypto_data(coin, htf)
    df_ltf = get_crypto_data(coin, ltf)
    if df_htf is None or df_ltf is None: return None
    
    ema_50 = calculate_ema(df_htf["Close"], 50).iloc[-1]
    htf_trend = "BULLISH" if df_htf["Close"].iloc[-1] > ema_50 else "BEARISH"
    cvd = calculate_cvd_delta(df_ltf)
    
    if htf_trend == "BULLISH" and cvd > 0:
        return {"Coin": COIN_SYMBOLS[coin], "Signal": "🟩 BUY", "Price": df_ltf["Close"].iloc[-1]}
    elif htf_trend == "BEARISH" and cvd < 0:
        return {"Coin": COIN_SYMBOLS[coin], "Signal": "🟥 SELL", "Price": df_ltf["Close"].iloc[-1]}
    return None

# --- UI ---
st.title("👑 ALPHA QUANT TERMINAL")
with st.sidebar:
    st.header("CONTROL PANEL")
    strategy = st.radio("Profile:", ["⚡ Scalping (1H + 5M)", "📈 Day Trading (4H + 15M)"])
    htf, ltf = ("1h", "5m") if "Scalping" in strategy else ("4h", "15m")
    tg_on = st.checkbox("Enable Telegram Alerts")
    tg_token = st.text_input("Bot Token:", type="password")
    tg_id = st.text_input("Chat ID:")

# --- SCANNER LOOP ---
st.write("📡 Scanning market...")
for coin in SCAN_COINS:
    res = analyze_coin(coin, htf, ltf)
    if res:
        if res not in st.session_state.signals_history:
            st.session_state.signals_history.insert(0, res)
            if tg_on: send_telegram_alert(tg_token, tg_id, f"{res['Coin']} - {res['Signal']}")
    time.sleep(0.5) # API බ්ලොක් නොවෙන්න

# --- DISPLAY ---
st.subheader("📡 LIVE SIGNAL LOG")
if st.session_state.signals_history:
    st.dataframe(pd.DataFrame(st.session_state.signals_history), use_container_width=True)
else:
    st.info("No signals yet. Scanning in background...")

time.sleep(20)
st.rerun()
