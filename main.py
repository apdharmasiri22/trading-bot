# =========================================================
# 👑 ALPHA TERMINAL v5.1 STABLE (SMOOTH REFRESH FIX)
# =========================================================

import numpy as np
import pandas as pd
import requests
import streamlit as st
import concurrent.futures
import streamlit.components.v1 as components
import datetime
import time

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ALPHA TERMINAL v5.1",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SMOOTH AUTO REFRESH (NO FLASH / NO EXTRA LIB)
# =========================================================

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

REFRESH_SECONDS = 15

if time.time() - st.session_state.last_refresh > REFRESH_SECONDS:
    st.session_state.last_refresh = time.time()
    st.rerun()

# =========================================================
# UI STYLE
# =========================================================

st.markdown("""
<style>

.stApp{
    background:#0d1117;
    color:white;
}

h1,h2,h3,h4{
    color:white !important;
}

[data-testid="stMetricValue"]{
    color:#ffb703;
    font-size:28px;
}

section[data-testid="stSidebar"]{
    background:#111827;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SAFE SESSION
# =========================================================

session = requests.Session()

retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429,500,502,503,504]
)

adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)

# =========================================================
# COINS
# =========================================================

COIN_SYMBOLS = {
    "BTCUSDT":"₿ BTCUSDT",
    "ETHUSDT":"♦️ ETHUSDT",
    "SOLUSDT":"☀️ SOLUSDT",
    "BNBUSDT":"🔶 BNBUSDT",
    "XRPUSDT":"💧 XRPUSDT",
    "ADAUSDT":"₳ ADAUSDT",
    "DOGEUSDT":"🐕 DOGEUSDT",
    "AVAXUSDT":"🔺 AVAXUSDT",
    "DOTUSDT":"● DOTUSDT",
    "LINKUSDT":"🔗 LINKUSDT",
    "MATICUSDT":"💜 MATICUSDT",
    "LTCUSDT":"Ł LTCUSDT",
    "UNIUSDT":"🦄 UNIUSDT",
    "ATOMUSDT":"⚛️ ATOMUSDT",
    "TRXUSDT":"🔴 TRXUSDT"
}

SCAN_COINS = list(COIN_SYMBOLS.keys())[:15]

# =========================================================
# BINANCE DATA
# =========================================================

@st.cache_data(ttl=20)
def get_crypto_data(symbol, interval, limit=100):

    url = "https://data-api.binance.vision/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    try:
        response = session.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        if not isinstance(data, list):
            return None

        df = pd.DataFrame(data)

        df = df.iloc[:, 0:6]
        df.columns = ["Time","Open","High","Low","Close","Volume"]

        for col in ["Open","High","Low","Close","Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df.dropna(inplace=True)
        return df

    except:
        return None

# =========================================================
# INDICATORS
# =========================================================

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / (avg_loss + 1e-10)
    return 100 - (100 / (1 + rs))

# =========================================================
# ANALYSIS
# =========================================================

def analyze_coin(symbol, htf, ltf):

    df = get_crypto_data(symbol, ltf, 120)
    df_htf = get_crypto_data(symbol, htf, 120)

    if df is None or df_htf is None:
        return None

    if len(df) < 50:
        return None

    df["EMA50"] = ema(df["Close"], 50)
    trend = "BULLISH" if df["Close"].iloc[-1] > df["EMA50"].iloc[-1] else "BEARISH"

    df["RSI"] = rsi(df["Close"])
    rsi_val = df["RSI"].iloc[-1]

    price = df["Close"].iloc[-1]

    score = 0
    signal = None

    if trend == "BULLISH":
        score += 30
    else:
        score += 30

    if rsi_val < 45:
        score += 25
        signal = "🟩 BUY"

    if rsi_val > 55:
        score += 25
        signal = "🟥 SELL"

    if score < 40:
        return None

    return {
        "Coin": symbol,
        "Signal": signal or "WAIT",
        "Score": score,
        "Price": price
    }

# =========================================================
# UI
# =========================================================

st.title("👑 ALPHA TERMINAL v5.1")
st.caption("Stable Smooth Refresh Edition")

btc = get_crypto_data("BTCUSDT","5m",5)

if btc is not None:
    st.success("🟢 Live Feed OK")
else:
    st.error("🔴 API Issue")

st.subheader("📡 MARKET SCANNER")

signals = []

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
    results = ex.map(lambda c: analyze_coin(c,"1h","5m"), SCAN_COINS)

    for r in results:
        if r:
            signals.append(r)

if signals:
    st.dataframe(pd.DataFrame(signals), use_container_width=True)
else:
    st.warning("⚠️ No valid setup currently")

st.subheader("🎯 BTC ANALYSIS")

btc_signal = analyze_coin("BTCUSDT","1h","5m")

if btc_signal:
    st.write(btc_signal)
else:
    st.info("No setup")

st.caption(f"Last Update: {datetime.datetime.utcnow()} UTC")
