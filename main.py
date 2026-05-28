import numpy as np
import pandas as pd
import requests
import streamlit as st
import concurrent.futures
import streamlit.components.v1 as components
import datetime
import time

# වෙබ් පිටුවේ සැකසුම් (Page Configuration)
st.set_page_config(
    page_title="ALPHA TRADING TERMINAL v4.1",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# 🎨 PREMIUM UI DESIGN (ULTIMATE CRYPTO TERMINAL VIBE)
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
# 🛠️ DATA MODULES & COIN SYMBOLS (BYBIT COMPATIBLE)
# =====================================================================
COIN_SYMBOLS = {
    "BTCUSDT": "₿ BTCUSDT", "ETHUSDT": "♦️ ETHUSDT", "SOLUSDT": "☀️ SOLUSDT", "BNBUSDT": "🔶 BNBUSDT",
    "XRPUSDT": "💧 XRPUSDT", "ADAUSDT": "₳ ADAUSDT", "DOGEUSDT": "🐕 DOGEUSDT", "SHIBUSDT": "🦊 SHIBUSDT",
    "PEPEUSDT": "🐸 PEPEUSDT", "DOTUSDT": "● DOTUSDT", "LTCUSDT": "Ł LTCUSDT", "AVAXUSDT": "🔺 AVAXUSDT",
    "LINKUSDT": "🔗 LINKUSDT", "TRXUSDT": "🔴 TRXUSDT", "ATOMUSDT": "⚛️ ATOMUSDT", "UNIUSDT": "🦄 UNIUSDT",
    "NEARUSDT": "Ⓝ NEARUSDT", "SUIUSDT": "💧 SUIUSDT", "FETUSDT": "🤖 FETUSDT", "APTUSDT": "🌀 APTUSDT"
}
SCAN_COINS = list(COIN_SYMBOLS.keys())

def get_all_binance_symbols_with_symbols():
    return COIN_SYMBOLS

def get_crypto_data(symbol, interval, limit=100):
    bybit_intervals = {"1m": "1", "5m": "5", "15m": "15", "1h": "60", "4h": "240", "1d": "D"}
    bybit_inv = bybit_intervals.get(interval, "15")
    
    # Bybit V5 Linear/Inverse Market Endpoint
    url = "https://api.bybit.com/v5/market/kline"
    params = {"category": "linear", "symbol": symbol, "interval": bybit_inv, "limit": limit}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            raw_list = data.get("result", {}).get("list", [])
            if not raw_list or len(raw_list) < 5:
                return None
            
            # Format: [startTime, openPrice, highPrice, lowPrice, closePrice, volume, turnover]
            df = pd.DataFrame(raw_list, columns=["Time", "Open", "High", "Low", "Close", "Volume", "Turnover"])
            
            # Convert strings to floats safely
            for col in ["Open", "High", "Low", "Close", "Volume"]:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
            # Chronological Order Flip (Oldest -> Newest)
            df = df.iloc[::-1].reset_index(drop=True)
            return df
    except:
        return None
    return None

# =====================================================================
# 🧠 ADVANCED QUANT MATH & HIGH ACCURACY SMC ENGINE
# =====================================================================
def calculate_rsi(series, period=14):
    if len(series) < period: return pd.Series(50, index=series.index)
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    return 100 - (100 / (1 + (gain / (loss + 1e-10))))

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

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
    cvd = (buyer_volume - seller_volume).iloc[-5:].sum()
    return cvd

def is_news_block_active():
    now = datetime.datetime.utcnow()
    if now.weekday() in [2, 3] and now.hour in [13, 14]: 
        return True
    return False

def detect_smc_features(df):
    if df is None or len(df) < 15: return 0, 0, "NONE"
    
    bos_signal = "NONE"
    if df['Close'].iloc[-1] > df['High'].shift(1).iloc[-6:-1].max():
        bos_signal = "BULLISH_BOS"
    elif df['Close'].iloc[-1] < df['Low'].shift(1).iloc[-6:-1].min():
        bos_signal = "BEARISH_BOS"
        
    bullish_ob = 1 if (df['Close'].iloc[-2] < df['Open'].iloc[-2]) and (df['Close'].iloc[-1] > df['High'].iloc[-2]) and (df['Volume'].iloc[-1] > df['Volume'].rolling(20).mean().fillna(0).iloc[-1] * 1.3) else 0
    bearish_ob = 1 if (df['Close'].iloc[-2] > df['Open'].iloc[-2]) and (df['Close'].iloc[-1] < df['Low'].iloc[-2]) and (df['Volume'].iloc[-1] > df['Volume'].rolling(20).mean().fillna(0).iloc[-1] * 1.3) else 0
    
    fvg_bullish = 1 if (df['Low'].iloc[-1] > df['High'].iloc[-3]) and (df['Close'].iloc[-2] > df['Open'].iloc[-2]) else 0
    fvg_bearish = 1 if (df['High'].iloc[-1] < df['Low'].iloc[-3]) and (df['Close'].iloc[-2] < df['Open'].iloc[-2]) else 0
    
    liq_sweep_bullish = 1 if (df['Low'].iloc[-1] < df['Low'].shift(1).rolling(10).min().fillna(0).iloc[-2]) and (df['Close'].iloc[-1] > df['Open'].iloc[-1]) else 0
    liq_sweep_bearish = 1 if (df['High'].iloc[-1] > df['High'].shift(1).rolling(10).max().fillna(0).iloc[-2]) and (df['Close'].iloc[-1] < df['Open'].iloc[-1]) else 0

    bull_points = (bullish_ob * 15) + (fvg_bullish * 15) + (liq_sweep_bullish * 10) + (15 if bos_signal == "BULLISH_BOS" else 0)
    bear_points = (bearish_ob * 15) + (fvg_bearish * 15) + (liq_sweep_bearish * 10) + (15 if bos_signal == "BEARISH_BOS" else 0)
    
    return bull_points, bear_points, bos_signal

def send_telegram_alert(token, chat_id, message):
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try: requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        except: pass

def analyze_coin_for_scanner(coin, htf, ltf):
    df_htf = get_crypto_data(coin, htf, 100)
    df_ltf = get_crypto_data(coin, ltf, 100)
    
    if df_htf is None or df_ltf is None or len(df_htf) < 50 or len(df_ltf) < 50: 
        return None
    
    if is_news_block_active(): return None

    bullish_points, bearish_points, total_checks = 0, 0, 0
    df_htf["EMA_50"] = calculate_ema(df_htf["Close"], 50)
    
    htf_trend = "BULLISH" if df_htf["Close"].iloc[-1] > df_htf["EMA_50"].iloc[-1] else "BEARISH"
    bullish_points += 15 if htf_trend == "BULLISH" else 0
    bearish_points += 15 if htf_trend == "BEARISH" else 0
    total_checks += 15
    
    df_ltf["RSI"] = calculate_rsi(df_ltf["Close"], 14)
    c_rsi = df_ltf["RSI"].iloc[-1]
    if c_rsi < 35: bullish_points += 15
    elif c_rsi > 65: bearish_points += 15
    total_checks += 15
    
    df_ltf["MACD"], df_ltf["Signal"] = calculate_macd(df_ltf["Close"])
    if df_ltf["MACD"].iloc[-1] > df_ltf["Signal"].iloc[-1]: bullish_points += 10
    else: bearish_points += 10
    total_checks += 10
    
    smc_bull, smc_bear, bos_sig = detect_smc_features(df_ltf)
    if htf_trend == "BULLISH" and bos_sig == "BULLISH_BOS": bullish_points += 20
    if htf_trend == "BEARISH" and bos_sig == "BEARISH_BOS": bearish_points += 20
    
    bullish_points += smc_bull
    bearish_points += smc_bear
    total_checks += 75 
    
    cvd_flow = calculate_cvd_delta(df_ltf)
    if cvd_flow > 0: bullish_points += 15
    elif cvd_flow < 0: bearish_points += 15
    total_checks += 15

    bull_per = (bullish_points / total_checks) * 100
    bear_per = (bearish_points / total_checks) * 100
    c_price = df_ltf["Close"].iloc[-1]
    df_ltf["ATR"] = calculate_atr(df_ltf)
    c_atr = df_ltf["ATR"].iloc[-1] if not pd.isna(df_ltf["ATR"].iloc[-1]) else (c_price * 0.003)
    dec = 6 if c_price < 0.1 else 4
    
    coin_display = COIN_SYMBOLS.get(coin, f"🪙 {coin}")
    
    if bull_per >= 60 and htf_trend == "BULLISH" and cvd_flow > 0:
        return {"Coin": coin_display, "Signal": "🟩 BUY / LONG", "Strength": f"{bull_per:.1f}%", "Structure": bos_sig, "Entry": f"{c_price:.{dec}f}", "SL": f"{c_price - (c_atr*2):.{dec}f}", "TP": f"{c_price + (c_atr*4):.{dec}f}"}
    elif bear_per >= 60 and htf_trend == "BEARISH" and cvd_flow < 0:
        return {"Coin": coin_display, "Signal": "🟥 SELL / SHORT", "Strength": f"{bear_per:.1f}%", "Structure": bos_sig, "Entry": f"{c_price:.{dec}f}", "SL": f"{c_price + (c_atr*2):.{dec}f}", "TP": f"{c_price - (c_atr*4):.{dec}f}"}
    return None

# =====================================================================
# ⚙️ SIDEBAR MANAGEMENT CONTROL PANEL
# =====================================================================
all_symbols_dict = get_all_binance_symbols_with_symbols()

with st.sidebar:
    st.markdown("### 👑 TERMINAL CONTROL PANEL")
    
    st.markdown("#### ⏱️ STRATEGY TIMEFRAME")
    strategy = st.radio("Select Trading Profile:", ["⚡ Scalping (1H + 5M)", "📈 Day Trading (4H + 15M)", "🐋 Swing Trading (1D + 1H)"], index=1)
    htf, ltf = ("1h", "5m") if "Scalping" in strategy else ("4h", "15m") if "Day Trading" in strategy else ("1d", "1h")
    
    st.markdown("---")
    
    selected_coin_display = st.selectbox("🎯 DEEP ANALYSIS COIN:", options=list(all_symbols_dict.values()), index=list(all_symbols_dict.keys()).index("BTCUSDT") if "BTCUSDT" in all_symbols_dict else 0)
    selected_coin = [k for k, v in all_symbols_dict.items() if v == selected_coin_display][0]
    
    st.markdown("---")
    
    st.markdown("#### 💰 RISK CALCULATOR")
    balance = st.number_input("Account Balance ($):", min_value=10.0, value=1000.0, step=50.0)
    risk_pct = st.slider("Risk Per Trade (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
    leverage = st.slider("Target Leverage (x):", min_value=1, max_value=50, value=10)
    
    st.markdown("---")
    
    st.markdown("####)
