# =========================================================
# 👑 ALPHA TERMINAL v8.0 ULTRA STABLE EDITION
# No Freeze | No Rate Limit Crash | Fast Scan | Safe Streamlit
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
    page_title="ALPHA TERMINAL v8.0",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# AUTO REFRESH (SAFE - NO EXTRA LIB)
# =========================================================
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 20:
    st.session_state.last_refresh = time.time()
    st.rerun()

# =========================================================
# UI STYLE
# =========================================================
st.markdown("""
<style>
.stApp { background:#0d1117; color:white; }
h1,h2,h3,h4 { color:white !important; }
[data-testid="stMetricValue"] { color:#ffb703; font-size:28px; }
section[data-testid="stSidebar"] { background:#111827; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# SAFE SESSION (ANTI BLOCK)
# =========================================================
session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5,
              status_forcelist=[429,500,502,503,504])
session.mount("https://", HTTPAdapter(max_retries=retry))

# =========================================================
# COINS (UNCHANGED - AS YOU REQUESTED)
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

SCAN_COINS = list(COIN_SYMBOLS.keys())

# =========================================================
# BINANCE DATA (SAFE + FAST + NO BLOCK)
# =========================================================
@st.cache_data(ttl=10)
def get_crypto_data(symbol, interval, limit=100):
    url = "https://api.binance.com/api/v3/klines"

    try:
        r = session.get(url, params={
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }, timeout=10)

        if r.status_code != 200:
            return None

        data = r.json()
        if not isinstance(data, list):
            return None

        df = pd.DataFrame(data, columns=[
            "t","o","h","l","c","v",
            "ct","qv","n","tb","tq","ig"
        ])

        for c in ["o","h","l","c","v"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        return df.dropna()

    except:
        return None

# =========================================================
# INDICATORS (OPTIMIZED)
# =========================================================
def ema(s, p): return s.ewm(span=p, adjust=False).mean()

def rsi(s, p=14):
    d = s.diff()
    g = d.clip(lower=0).rolling(p).mean()
    l = (-d.clip(upper=0)).rolling(p).mean()
    rs = g / (l + 1e-10)
    return 100 - (100 / (1 + rs))

def macd(s):
    m = ema(s,12) - ema(s,26)
    sig = ema(m,9)
    return m, sig

def atr(df, p=14):
    h,l,c = df["h"], df["l"], df["c"].shift()
    tr = pd.concat([(h-l), (h-c).abs(), (l-c).abs()], axis=1).max(axis=1)
    return tr.rolling(p).mean()

# =========================================================
# ANALYSIS ENGINE (FAST + SAFE)
# =========================================================
def analyze(symbol, htf, ltf):

    dfh = get_crypto_data(symbol, htf, 100)
    dfl = get_crypto_data(symbol, ltf, 100)

    if dfh is None or dfl is None or len(dfl) < 50:
        return None

    dfh["ema50"] = ema(dfh["c"], 50)

    trend = "BULL" if dfh["c"].iloc[-1] > dfh["ema50"].iloc[-1] else "BEAR"

    dfl["rsi"] = rsi(dfl["c"])
    dfl["macd"], dfl["sig"] = macd(dfl["c"])
    dfl["atr"] = atr(dfl)

    r = dfl["rsi"].iloc[-1]
    m = dfl["macd"].iloc[-1]
    s = dfl["sig"].iloc[-1]
    price = dfl["c"].iloc[-1]
    a = dfl["atr"].iloc[-1]

    if np.isnan(a):
        a = price * 0.003

    bull = 0
    bear = 0

    if trend == "BULL": bull += 30
    else: bear += 30

    if r < 45: bull += 20
    if r > 55: bear += 20

    if m > s: bull += 30
    else: bear += 30

    if bull >= 55 and trend == "BULL":
        return {
            "Coin": symbol,
            "Signal": "BUY",
            "Price": price,
            "SL": price - a*2,
            "TP": price + a*4,
            "Score": bull
        }

    if bear >= 55 and trend == "BEAR":
        return {
            "Coin": symbol,
            "Signal": "SELL",
            "Price": price,
            "SL": price + a*2,
            "TP": price - a*4,
            "Score": bear
        }

    return None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.title("CONTROL PANEL")

    mode = st.radio("Mode", ["Scalping","Day","Swing"])

    htf, ltf = (
        ("1h","5m") if mode=="Scalping"
        else ("4h","15m") if mode=="Day"
        else ("1d","1h")
    )

    coin = st.selectbox("Coin", SCAN_COINS)

# =========================================================
# HEADER
# =========================================================
st.title("👑 ALPHA TERMINAL v8.0 ULTRA STABLE")

# =========================================================
# SAFE SCANNER (NO FREEZE FIX)
# =========================================================
st.subheader("MARKET SCANNER")

signals = []

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    results = list(ex.map(lambda c: analyze(c, htf, ltf), SCAN_COINS))

for r in results:
    if r:
        signals.append(r)

if signals:
    st.dataframe(pd.DataFrame(signals), use_container_width=True)
else:
    st.warning("No valid setup")

# =========================================================
# SINGLE COIN
# =========================================================
st.subheader(f"{coin} ANALYSIS")

a = analyze(coin, htf, ltf)

if a:
    st.metric("Signal", a["Signal"])
    st.metric("Score", a["Score"])
    st.write(f"Entry: {a['Price']}")
    st.write(f"SL: {a['SL']}")
    st.write(f"TP: {a['TP']}")
else:
    st.info("Waiting for setup...")

# =========================================================
# FOOTER
# =========================================================
st.caption(f"Updated: {datetime.datetime.utcnow()}")
