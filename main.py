👑 ALPHA TERMINAL v8.0 FULL FINAL (GITHUB READY)

import numpy as np
import pandas as pd
import requests
import streamlit as st
import concurrent.futures
import streamlit.components.v1 as components
import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

=========================
CONFIG
=========================

st.set_page_config(
page_title="ALPHA TERMINAL v8",
page_icon="👑",
layout="wide"
)

st.markdown("<meta http-equiv='refresh' content='25'>", unsafe_allow_html=True)

=========================
UI STYLE
=========================

st.markdown("""

<style> .stApp { background:#0d1117; color:white; } h1,h2,h3 { color:white !important; } [data-testid="stMetricValue"] { color:#ffb703; font-size:26px; } section[data-testid="stSidebar"] { background:#111827; } </style>

""", unsafe_allow_html=True)

=========================
SAFE SESSION
=========================

session = requests.Session()

retry = Retry(total=5, backoff_factor=0.5,
status_forcelist=[429,500,502,503,504])

session.mount("https://", HTTPAdapter(max_retries=retry))

=========================
COINS (FULL SAFE LIST)
=========================

COIN_SYMBOLS = {
"BTCUSDT":"BTC",
"ETHUSDT":"ETH",
"SOLUSDT":"SOL",
"BNBUSDT":"BNB",
"XRPUSDT":"XRP",
"ADAUSDT":"ADA",
"DOGEUSDT":"DOGE",
"AVAXUSDT":"AVAX",
"DOTUSDT":"DOT",
"LINKUSDT":"LINK",
"MATICUSDT":"MATIC",
"LTCUSDT":"LTC",
"UNIUSDT":"UNI",
"ATOMUSDT":"ATOM",
"TRXUSDT":"TRX"
}

SCAN_COINS = list(COIN_SYMBOLS.keys())

=========================
BINANCE DATA
=========================

@st.cache_data(ttl=15)
def get_data(symbol, interval, limit=100):
url = "https://data-api.binance.vision/api/v3/klines"

try:
    r = session.get(url, params={
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }, timeout=10)

    data = r.json()
    if not isinstance(data, list):
        return None

    df = pd.DataFrame(data, columns=[
        "t","o","h","l","c","v",
        "ct","q","n","tb","tq","i"
    ])

    df = df[["o","h","l","c","v"]]

    for i in df.columns:
        df[i] = pd.to_numeric(df[i], errors="coerce")

    return df.dropna()

except:
    return None
=========================
INDICATORS
=========================

def ema(x, p):
return x.ewm(span=p).mean()

def rsi(x, p=14):
d = x.diff()
g = d.clip(lower=0).rolling(p).mean()
l = -d.clip(upper=0).rolling(p).mean()
rs = g / (l + 1e-10)
return 100 - (100 / (1 + rs))

def macd(x):
m = ema(x,12) - ema(x,26)
s = ema(m,9)
return m,s

def atr(df):
h,l,c = df["h"], df["l"], df["c"]
tr = pd.concat([
h-l,
abs(h-c.shift()),
abs(l-c.shift())
], axis=1).max(axis=1)

return tr.rolling(14).mean()
=========================
ANALYSIS ENGINE
=========================

def analyze(symbol, htf, ltf):

h = get_data(symbol, htf, 80)
l = get_data(symbol, ltf, 80)

if h is None or l is None or len(h)<40:
    return None

h["ema50"] = ema(h["c"],50)
trend = "BULL" if h["c"].iloc[-1] > h["ema50"].iloc[-1] else "BEAR"

r = rsi(l["c"]).iloc[-1]
m,s = macd(l["c"])
a = atr(l).iloc[-1]
price = l["c"].iloc[-1]

if pd.isna(a):
    a = price * 0.003

bull = 0
bear = 0

if trend=="BULL":
    bull += 30
else:
    bear += 30

if r < 40:
    bull += 20
elif r > 60:
    bear += 20

if m.iloc[-1] > s.iloc[-1]:
    bull += 25
else:
    bear += 25

if l["v"].iloc[-1] > l["v"].rolling(20).mean().iloc[-1]:
    bull += 10
    bear += 10

score = max(bull,bear)

if score < 55:
    return None

if bull > bear:
    return {
        "coin": symbol,
        "signal": "BUY",
        "score": bull,
        "price": price,
        "sl": price - a*2,
        "tp": price + a*4
    }

return {
    "coin": symbol,
    "signal": "SELL",
    "score": bear,
    "price": price,
    "sl": price + a*2,
    "tp": price - a*4
}
=========================
SIDEBAR
=========================

with st.sidebar:

st.title("CONTROL")

mode = st.radio("Mode", ["Scalping","Day","Swing"])

if mode=="Scalping":
    htf,ltf="1h","5m"
elif mode=="Day":
    htf,ltf="4h","15m"
else:
    htf,ltf="1d","1h"

selected = st.selectbox("Coin", SCAN_COINS)
=========================
HEADER
=========================

st.title("👑 ALPHA TERMINAL v8")

test = get_data("BTCUSDT","5m",5)

if test is None:
st.error("Binance down")
st.stop()
else:
st.success("Live Connected")

=========================
SCANNER
=========================

st.subheader("SCAN")

signals = []

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:

res = ex.map(lambda c: analyze(c,htf,ltf), SCAN_COINS)

for r in res:
    if r:
        signals.append(r)

if signals:
st.dataframe(pd.DataFrame(signals))
else:
st.warning("No setup")

=========================
SINGLE
=========================

st.subheader(selected)

r = analyze(selected,htf,ltf)

if r:

st.metric("Signal", r["signal"])
st.metric("Score", r["score"])

st.success(f"""

ENTRY: {r["price"]}
SL: {r["sl"]}
TP: {r["tp"]}
""")

=========================
RISK
=========================

balance = 1000
risk = 1

if r:
risk_cash = balance*(risk/100)
sl = abs(r["price"]-r["sl"])
pos = risk_cash/(sl/r["price"])

st.warning(f"""

Risk: {risk_cash}
Position: {pos}
""")

=========================
DONE
=========================

st.caption(str(datetime.datetime.utcnow()))
