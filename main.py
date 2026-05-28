# =========================================================
# 👑 ALPHA TERMINAL v9.0 PRO ENGINE
# No Freeze | Always Active | Smart Signal System
# =========================================================

import numpy as np
import pandas as pd
import requests
import streamlit as st
import concurrent.futures
import datetime
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="ALPHA TERMINAL V9",
    page_icon="👑",
    layout="wide"
)

# AUTO REFRESH SAFE
if "t" not in st.session_state:
    st.session_state.t = time.time()

if time.time() - st.session_state.t > 15:
    st.session_state.t = time.time()
    st.rerun()

# =========================================================
# SESSION (SAFE)
# =========================================================
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=3))

# =========================================================
# COINS
# =========================================================
COINS = [
    "BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT",
    "ADAUSDT","DOGEUSDT","AVAXUSDT","DOTUSDT","LINKUSDT"
]

# =========================================================
# DATA
# =========================================================
@st.cache_data(ttl=10)
def get_data(symbol):
    url = "https://api.binance.com/api/v3/klines"
    try:
        r = session.get(url, params={
            "symbol": symbol,
            "interval": "5m",
            "limit": 100
        }, timeout=10)

        data = r.json()
        df = pd.DataFrame(data)

        df = df.iloc[:, [1,2,3,4,5]]
        df.columns = ["o","h","l","c","v"]

        df = df.astype(float)
        return df

    except:
        return None

# =========================================================
# INDICATORS
# =========================================================
def ema(s,p): return s.ewm(span=p).mean()

def rsi(s):
    d = s.diff()
    g = d.clip(lower=0).rolling(14).mean()
    l = (-d.clip(upper=0)).rolling(14).mean()
    rs = g/(l+1e-10)
    return 100 - (100/(1+rs))

# =========================================================
# ENGINE (SMART SCORING)
# =========================================================
def analyze(symbol):

    df = get_data(symbol)
    if df is None or len(df) < 50:
        return None

    price = df["c"].iloc[-1]

    trend = "BULL" if price > ema(df["c"],50).iloc[-1] else "BEAR"

    r = rsi(df["c"]).iloc[-1]

    bull = 50 if trend=="BULL" else 50
    bear = 50 if trend=="BEAR" else 50

    # RSI soft scoring (IMPORTANT FIX)
    if r < 50:
        bull += (50 - r)
    else:
        bear += (r - 50)

    score = max(bull, bear)

    direction = "BUY" if bull > bear else "SELL"

    return {
        "Coin": symbol,
        "Direction": direction,
        "Score": round(score,2),
        "Price": price
    }

# =========================================================
# UI
# =========================================================
st.title("👑 ALPHA TERMINAL V9 PRO")

# =========================================================
# SCANNER (FAST + NO FREEZE)
# =========================================================
results = []

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    out = list(ex.map(analyze, COINS))

for r in out:
    if r:
        results.append(r)

df = pd.DataFrame(results)

# =========================================================
# ALWAYS SHOW DATA (NO EMPTY SCREEN FIX)
# =========================================================
if len(df) == 0:
    st.warning("Market scanning... retrying")
else:
    st.dataframe(df.sort_values("Score", ascending=False))

    st.subheader("🔥 TOP 3 COINS")
    st.dataframe(df.sort_values("Score", ascending=False).head(3))

# =========================================================
# MARKET BIAS (IMPORTANT FIX)
# =========================================================
if len(df) > 0:
    bull_avg = (df["Direction"] == "BUY").mean() * 100
    bear_avg = 100 - bull_avg

    st.metric("Market Bias BUY %", f"{bull_avg:.1f}")
    st.metric("Market Bias SELL %", f"{bear_avg:.1f}")

st.caption(f"Updated {datetime.datetime.utcnow()}")
