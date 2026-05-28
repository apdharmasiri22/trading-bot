import numpy as np
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
import datetime
import time

# වෙබ් පිටුවේ සැකසුම් (Page Configuration)
st.set_page_config(
    page_title="ALPHA TRADING TERMINAL v4.5",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE FOR SIGNAL LOG ---
if 'signals_history' not in st.session_state:
    st.session_state.signals_history = []

# =====================================================================
# 🎨 PREMIUM UI DESIGN
# =====================================================================
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(13, 17, 23, 0.90), rgba(13, 17, 23, 0.97)), 
                          url('https://images.unsplash.com/photo-1642790106117-e829e14a795f?q=80&w=1920');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .main { color: #ffffff; }
    h1, h2, h3, h4 { color: #f0f2f5 !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    div[data-testid="stMetricValue"] { font-size: 30px !important; font-weight: bold !important; font-family: 'monospace'; color: #ffb703 !important; }
    .stAlert { border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
    .dataframe { border: 1px solid #30363d !important; background-color: rgba(22, 27, 34, 0.8) !important; color: #ffffff !important; }
    div[data-testid="stSidebar"] { background-color: rgba(13, 17, 23, 0.96) !important; border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 🛠️ DATA MODULES (FUTURES API)
# =====================================================================
COIN_SYMBOLS = {
    "BTCUSDT": "₿ BTCUSDT", "ETHUSDT": "♦️ ETHUSDT", "SOLUSDT": "☀️ SOLUSDT", "BNBUSDT": "🔶 BNBUSDT",
    "XRPUSDT": "💧 XRPUSDT", "ADAUSDT": "₳ ADAUSDT", "DOGEUSDT": "🐕 DOGEUSDT", "SHIBUSDT": "🦊 SHIBUSDT",
    "AVAXUSDT": "🔺 AVAXUSDT", "DOTUSDT": "● DOTUSDT", "LINKUSDT": "🔗 LINKUSDT", "MATICUSDT": "💜 MATICUSDT"
}
SCAN_COINS = list(COIN_SYMBOLS.keys())

@st.cache_data(ttl=60)
def get_crypto_data(symbol, interval, limit=100):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVol', 'NumTrades', 'TakerBuyBase', 'TakerBuyQuote', 'Ignore'])
            df = df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume']]
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
    except: return None
    return None

# --- MATH FUNCTIONS (Logic) ---
def calculate_rsi(series, period=14):
    if len(series) < period: return pd.Series(50, index=series.index)
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    return 100 - (100 / (1 + (gain / (loss + 1e-10))))

def calculate_ema(series, period): return series.ewm(span=period, adjust=False).mean()

def calculate_macd(series, fast=12, slow=26, signal=9):
    macd_line = calculate_ema(series, fast) - calculate_ema(series, slow)
    return macd_line, calculate_ema(macd_line, signal)

def calculate_atr(df, period=14):
    if len(df) < period: return pd.Series(df["Close"] * 0.003)
    tr = pd.concat([df["High"] - df["Low"], abs(df["High"] - df["Close"].shift()), abs(df["Low"] - df["Close"].shift())], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def calculate_cvd_delta(df):
    if df is None or df.empty or len(df) < 5: return 0
    typical_price_change = df['Close'] - df['Open']
    high_low_spread = df['High'] - df['Low'] + 1e-10
    buyer_volume = df['Volume'] * (0.5 + (typical_price_change / (2 * high_low_spread)))
    seller_volume = df['Volume'] - buyer_volume
    return (buyer_volume - seller_volume).iloc[-5:].sum()

def detect_smc_features(df):
    if df is None or len(df) < 15: return 0, 0, "NONE"
    bos_signal = "NONE"
    if df['Close'].iloc[-1] > df['High'].shift(1).iloc[-6:-1].max(): bos_signal = "BULLISH_BOS"
    elif df['Close'].iloc[-1] < df['Low'].shift(1).iloc[-6:-1].min(): bos_signal = "BEARISH_BOS"
    return 0, 0, bos_signal # упрощенная версия

def send_telegram_alert(token, chat_id, message):
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try: requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        except: pass

def analyze_coin_for_scanner(coin, htf, ltf):
    df_htf = get_crypto_data(coin, htf, 100)
    df_ltf = get_crypto_data(coin, ltf, 100)
    if df_htf is None or df_ltf is None: return None
    
    # Simple logic
    df_htf["EMA_50"] = calculate_ema(df_htf["Close"], 50)
    htf_trend = "BULLISH" if df_htf["Close"].iloc[-1] > df_htf["EMA_50"].iloc[-1] else "BEARISH"
    cvd = calculate_cvd_delta(df_ltf)
    
    if htf_trend == "BULLISH" and cvd > 0:
        return {"Coin": COIN_SYMBOLS.get(coin), "Signal": "🟩 BUY", "Price": df_ltf["Close"].iloc[-1]}
    elif htf_trend == "BEARISH" and cvd < 0:
        return {"Coin": COIN_SYMBOLS.get(coin), "Signal": "🟥 SELL", "Price": df_ltf["Close"].iloc[-1]}
    return None

# =====================================================================
# ⚙️ SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown("### 👑 CONTROL PANEL")
    strategy = st.radio("Profile:", ["⚡ Scalping (1H + 5M)", "📈 Day Trading (4H + 15M)"])
    htf, ltf = ("1h", "5m") if "Scalping" in strategy else ("4h", "15m")
    tg_on = st.checkbox("Enable Alerts")
    tg_token = st.text_input("Bot Token:", type="password")
    tg_id = st.text_input("Chat ID:")

# =====================================================================
# 👑 MAIN DASHBOARD
# =====================================================================
st.title("👑 ALPHA QUANT TERMINAL")

# 📡 SCANNER
active_signals = []
for coin in SCAN_COINS:
    res = analyze_coin_for_scanner(coin, htf, ltf)
    if res:
        active_signals.append(res)
        # Add to session state
        if res not in st.session_state.signals_history:
            st.session_state.signals_history.insert(0, res)
            if tg_on: send_telegram_alert(tg_token, tg_id, f"Signal for {res['Coin']}: {res['Signal']}")

# 📡 SIGNAL LOG TABLE
st.subheader("📡 LIVE SIGNAL LOG")
if st.session_state.signals_history:
    st.dataframe(pd.DataFrame(st.session_state.signals_history).head(10), use_container_width=True)
else:
    st.info("Scanning for signals...")

# 🔄 REFRESH
time.sleep(30)
st.rerun()
