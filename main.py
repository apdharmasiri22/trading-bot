# =========================================================
# 👑 ALPHA TERMINAL v5.0 STABLE EDITION (SMOOTH REFRESH FIX)
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
from streamlit_autorefresh import st_autorefresh   # ✅ ADDED

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ALPHA TERMINAL v5.0",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SMOOTH AUTO REFRESH (FIXED)
# =========================================================

st_autorefresh(interval=15000, key="data_refresh")  # ✅ ONLY FIX HERE

# =========================================================
# UI
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
# SAFE REQUEST SESSION
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
# DATA FETCH
# =========================================================

@st.cache_data(ttl=20)
def get_crypto_data(symbol, interval, limit=100):

    url = "https://data-api.binance.vision/api/v3/klines"

    try:
        response = session.get(
            url,
            params={"symbol": symbol, "interval": interval, "limit": limit},
            timeout=15
        )

        if response.status_code != 200:
            return None

        data = response.json()
        if not isinstance(data, list):
            return None

        df = pd.DataFrame(data)
        df = df.iloc[:, :6]
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

def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()

def rsi(s, n=14):
    d = s.diff()
    gain = d.clip(lower=0).rolling(n).mean()
    loss = (-d.clip(upper=0)).rolling(n).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

def macd(s):
    m = ema(s, 12) - ema(s, 26)
    sig = ema(m, 9)
    return m, sig

def atr(df, n=14):
    h,l,c = df["High"],df["Low"],df["Close"]
    tr = pd.concat([
        h-l,
        abs(h-c.shift()),
        abs(l-c.shift())
    ], axis=1).max(axis=1)
    return tr.rolling(n).mean()

# =========================================================
# ANALYSIS
# =========================================================

def analyze(symbol):

    df = get_crypto_data(symbol, "5m", 120)
    if df is None or len(df) < 60:
        return None

    price = df["Close"].iloc[-1]

    trend = "BULLISH" if price > ema(df["Close"], 50).iloc[-1] else "BEARISH"

    r = rsi(df["Close"]).iloc[-1]
    m,s = macd(df["Close"])

    a = atr(df).iloc[-1]
    if np.isnan(a):
        a = price * 0.003

    vol_ok = df["Volume"].iloc[-1] > df["Volume"].rolling(20).mean().iloc[-1]

    bull = 0
    bear = 0

    bull += 25 if trend == "BULLISH" else 0
    bear += 25 if trend == "BEARISH" else 0

    bull += 20 if r < 48 else 0
    bear += 20 if r > 52 else 0

    bull += 25 if m.iloc[-1] > s.iloc[-1] else 0
    bear += 25 if m.iloc[-1] <= s.iloc[-1] else 0

    bull += 10 if vol_ok else 0
    bear += 10 if vol_ok else 0

    if bull >= 40 and trend == "BULLISH":
        return {
            "Coin": symbol,
            "Signal": "BUY",
            "Price": price,
            "SL": price - a*2,
            "TP": price + a*3,
            "Score": bull
        }

    if bear >= 40 and trend == "BEARISH":
        return {
            "Coin": symbol,
            "Signal": "SELL",
            "Price": price,
            "SL": price + a*2,
            "TP": price - a*3,
            "Score": bear
        }

    return None

# =========================================================
# UI HEADER
# =========================================================

st.title("👑 ALPHA TERMINAL v5.0 (SMOOTH MODE)")

# =========================================================
# SCANNER
# =========================================================

st.subheader("MARKET SCANNER")

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    results = list(ex.map(analyze, SCAN_COINS))

signals = [r for r in results if r]

if signals:
    st.dataframe(pd.DataFrame(signals), use_container_width=True)
else:
    st.warning("No valid setup currently")

# =========================================================
# STATUS
# =========================================================

test = get_crypto_data("BTCUSDT","5m",10)

if test is not None:
    st.success("LIVE CONNECTED")
else:
    st.error("API ERROR")

# =========================================================
# FOOTER
# =========================================================

st.caption(str(datetime.datetime.utcnow()))
