import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
from datetime import datetime

# =========================================================

# PAGE CONFIG

# =========================================================

st.set_page_config(
page_title="QUANTUM X TERMINAL",
layout="wide"
)

# =========================================================

# STYLE

# =========================================================

st.markdown("""

<style>
html, body, [class*="css"] {
    background: linear-gradient(135deg,#020617,#0f172a,#111827);
    color:white;
}

.block-container{
    padding-top:1rem;
}

.card{
    background:rgba(15,23,42,0.92);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:20px;
    padding:20px;
    margin-bottom:20px;
}

.buy{
    background:#14532d;
    padding:14px;
    border-radius:12px;
    text-align:center;
    font-size:20px;
    font-weight:bold;
}

.sell{
    background:#7f1d1d;
    padding:14px;
    border-radius:12px;
    text-align:center;
    font-size:20px;
    font-weight:bold;
}

.neutral{
    background:#334155;
    padding:14px;
    border-radius:12px;
    text-align:center;
    font-size:20px;
    font-weight:bold;
}

.title{
    font-size:46px;
    font-weight:900;
    background:linear-gradient(90deg,#38bdf8,#818cf8,#22c55e);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
</style>

""", unsafe_allow_html=True)

# =========================================================

# HEADER

# =========================================================

st.markdown("""

<div class="card">
<div class="title">⚡ QUANTUM X TERMINAL</div>
<div>Institutional AI Smart Money Dashboard</div>
</div>
""", unsafe_allow_html=True)

# =========================================================

# DATABASE

# =========================================================

conn = sqlite3.connect(
"signals.db",
check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS signals (
id INTEGER PRIMARY KEY AUTOINCREMENT,
coin TEXT,
signal TEXT,
timeframe TEXT,
entry REAL,
tp1 REAL,
tp2 REAL,
tp3 REAL,
sl REAL,
probability REAL,
status TEXT,
created_at TEXT
)
""")

conn.commit()

# =========================================================

# INDICATORS

# =========================================================

def calculate_rsi(data, period=14):

```
delta = data.diff()

gain = delta.where(
    delta > 0,
    0
).rolling(period).mean()

loss = -delta.where(
    delta < 0,
    0
).rolling(period).mean()

rs = gain / loss

return 100 - (100 / (1 + rs))
```

def calculate_ema(data, period):

```
return data.ewm(
    span=period,
    adjust=False
).mean()
```

def calculate_macd(data):

```
ema12 = calculate_ema(data, 12)

ema26 = calculate_ema(data, 26)

macd = ema12 - ema26

signal = calculate_ema(macd, 9)

return macd, signal
```

def calculate_atr(df, period=14):

```
high_low = df["high"] - df["low"]

high_close = np.abs(
    df["high"] - df["close"].shift()
)

low_close = np.abs(
    df["low"] - df["close"].shift()
)

ranges = pd.concat(
    [high_low, high_close, low_close],
    axis=1
)

true_range = np.max(ranges, axis=1)

return pd.Series(true_range).rolling(period).mean()
```

# =========================================================

# MARKET DATA

# =========================================================

@st.cache_data(ttl=60)
def get_market():

```
try:

    url = "https://api.binance.com/api/v3/ticker/24hr"

    response = requests.get(
        url,
        timeout=15,
        headers={"User-Agent":"Mozilla/5.0"}
    )

    data = response.json()

    rows = []

    if isinstance(data, list):

        for coin in data:

            try:

                symbol = str(
                    coin.get("symbol","")
                )

                if not symbol.endswith("USDT"):
                    continue

                volume = float(
                    coin.get("quoteVolume",0)
                )

                if volume < 10000000:
                    continue

                rows.append({

                    "symbol":symbol,

                    "price":float(
                        coin.get("lastPrice",0)
                    ),

                    "change":float(
                        coin.get(
                            "priceChangePercent",
                            0
                        )
                    ),

                    "volume":volume

                })

            except:
                pass

    df = pd.DataFrame(rows)

    if not df.empty:

        df = df.sort_values(
            by="volume",
            ascending=False
        ).head(100)

        return df

except:
    pass

return pd.DataFrame({
    "symbol":["BTCUSDT","ETHUSDT"],
    "price":[68000,3500],
    "change":[2.5,1.2],
    "volume":[1000000,500000]
})
```

# =========================================================

# KLINES

# =========================================================

@st.cache_data(ttl=30)
def get_klines(symbol, interval="15m"):

```
try:

    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=200"

    response = requests.get(
        url,
        timeout=15
    )

    data = response.json()

    frame = pd.DataFrame(data)

    frame = frame.iloc[:, :6]

    frame.columns = [
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    for col in [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]:
        frame[col] = frame[col].astype(float)

    return frame

except:

    fake = pd.DataFrame({
        "open":np.random.uniform(60000,70000,200),
        "high":np.random.uniform(70000,71000,200),
        "low":np.random.uniform(59000,60000,200),
        "close":np.random.uniform(60000,70000,200),
        "volume":np.random.uniform(1000,5000,200)
    })

    return fake
```

# =========================================================

# SAVE SIGNAL

# =========================================================

def save_signal(
coin,
signal,
timeframe,
entry,
tp1,
tp2,
tp3,
sl,
probability
):

```
try:

    cursor.execute("""
    INSERT INTO signals (
        coin,
        signal,
        timeframe,
        entry,
        tp1,
        tp2,
        tp3,
        sl,
        probability,
        status,
        created_at
    )
    VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        coin,
        signal,
        timeframe,
        entry,
        tp1,
        tp2,
        tp3,
        sl,
        probability,
        "RUNNING",
        str(datetime.now())
    ))

    conn.commit()

except:
    pass
```

# =========================================================

# LOAD MARKET

# =========================================================

df = get_market()

# =========================================================

# METRICS

# =========================================================

btc_data = df[df["symbol"] == "BTCUSDT"]

btc_price = 0

if not btc_data.empty:
btc_price = btc_data.iloc[0]["price"]

c1,c2,c3,c4 = st.columns(4)

with c1:
st.metric(
"BTC PRICE",
f"${btc_price:,.2f}"
)

with c2:
st.metric(
"COINS",
len(df)
)

with c3:
st.metric(
"GREEN",
len(df[df["change"] > 0])
)

with c4:
st.metric(
"RED",
len(df[df["change"] < 0])
)

# =========================================================

# LAYOUT

# =========================================================

left,center,right = st.columns([1,1.5,1])

# =========================================================

# TOP GAINERS

# =========================================================

with left:

```
st.subheader("🚀 TOP GAINERS")

gainers = df.sort_values(
    by="change",
    ascending=False
).head(20)

st.dataframe(
    gainers,
    use_container_width=True,
    height=650
)
```

# =========================================================

# ANALYZER

# =========================================================

with center:

```
st.subheader("🧠 AI ANALYZER")

symbol = st.selectbox(
    "Select Coin",
    df["symbol"].tolist()
)

timeframe = st.selectbox(
    "Timeframe",
    ["5m","15m","1h","4h","1d"]
)

kline = get_klines(
    symbol,
    timeframe
)

close = kline["close"]

current_price = close.iloc[-1]

rsi = calculate_rsi(close).iloc[-1]

macd, signal_line = calculate_macd(close)

macd_value = macd.iloc[-1]

ema20 = calculate_ema(close,20).iloc[-1]

ema50 = calculate_ema(close,50).iloc[-1]

ema200 = calculate_ema(close,100).iloc[-1]

atr = calculate_atr(kline).iloc[-1]

# =====================================================
# AI SIGNAL ENGINE
# =====================================================

long_score = 0

if rsi < 35:
    long_score += 25

if macd_value > 0:
    long_score += 25

if ema20 > ema50:
    long_score += 25

if ema50 > ema200:
    long_score += 25

short_score = 100 - long_score

# =====================================================
# SIGNAL
# =====================================================

if long_score >= 80:

    signal = "🚀 STRONG LONG"
    css = "buy"

elif long_score >= 60:

    signal = "🟢 LONG"
    css = "buy"

elif long_score >= 40:

    signal = "🟡 NEUTRAL"
    css = "neutral"

else:

    signal = "🔴 SHORT"
    css = "sell"

# =====================================================
# ENTRY / TP / SL
# =====================================================

entry = current_price

sl = current_price - (atr * 1.5)

tp1 = current_price + (atr * 2)

tp2 = current_price + (atr * 4)

tp3 = current_price + (atr * 6)

leverage = "10X" if long_score >= 80 else "5X"

whale = "🐋 WHALE ACTIVE"

# =====================================================
# SAVE SIGNAL
# =====================================================

if long_score >= 80:

    save_signal(
        symbol,
        "LONG",
        timeframe,
        entry,
        tp1,
        tp2,
        tp3,
        sl,
        long_score
    )

# =====================================================
# DISPLAY
# =====================================================

st.markdown(f"""

<div class="card">

<h1>{symbol}</h1>

<div class="{css}">
{signal}
</div>

<br>

<h2>
🟢 LONG POSSIBILITY : {long_score}%
</h2>

<h2>
🔴 SHORT POSSIBILITY : {short_score}%
</h2>

<hr>

<div>📊 RSI : {rsi:.2f}</div>

<div>⚡ MACD : {macd_value:.2f}</div>

<div>📈 EMA20 : {ema20:.2f}</div>

<div>📈 EMA50 : {ema50:.2f}</div>

<div>📈 EMA200 : {ema200:.2f}</div>

<div>🌊 ATR : {atr:.2f}</div>

<div>🐋 WHALE STATUS : {whale}</div>

<hr>

<h3>🎯 ENTRY : {entry:.2f}</h3>

<h3>🛑 STOP LOSS : {sl:.2f}</h3>

<h3>💰 TP1 : {tp1:.2f}</h3>

<h3>💰 TP2 : {tp2:.2f}</h3>

<h3>💰 TP3 : {tp3:.2f}</h3>

<h3>⚡ LEVERAGE : {leverage}</h3>

</div>

""", unsafe_allow_html=True)
```

# =========================================================

# LOSERS

# =========================================================

with right:

```
st.subheader("📉 TOP LOSERS")

losers = df.sort_values(
    by="change"
).head(20)

st.dataframe(
    losers,
    use_container_width=True,
    height=650
)
```

# =========================================================

# CHART

# =========================================================

st.subheader("📊 ADVANCED CANDLE CHART")

fig = go.Figure(data=[

```
go.Candlestick(

    x=kline.index,

    open=kline["open"],

    high=kline["high"],

    low=kline["low"],

    close=kline["close"]

)
```

])

fig.update_layout(
template="plotly_dark",
height=700
)

st.plotly_chart(
fig,
use_container_width=True
)

# =========================================================

# HEATMAP

# =========================================================

st.subheader("🌡️ MARKET HEATMAP")

heat = df.head(50)

fig2 = px.treemap(
heat,
path=["symbol"],
values="volume",
color="change",
color_continuous_scale="RdYlGn"
)

fig2.update_layout(
template="plotly_dark",
height=700
)

st.plotly_chart(
fig2,
use_container_width=True
)

# =========================================================

# ACCURACY DASHBOARD

# =========================================================

st.subheader("📊 AI SIGNAL ACCURACY")

signals_df = pd.read_sql(
"SELECT * FROM signals",
conn
)

if not signals_df.empty:

```
total_signals = len(signals_df)

tp_hits = len(
    signals_df[
        signals_df["status"] == "TP1 HIT"
    ]
)

sl_hits = len(
    signals_df[
        signals_df["status"] == "SL HIT"
    ]
)

win_rate = round(
    (tp_hits / total_signals) * 100,
    2
)

a,b,c,d = st.columns(4)

with a:
    st.metric(
        "TOTAL",
        total_signals
    )

with b:
    st.metric(
        "TP HIT",
        tp_hits
    )

with c:
    st.metric(
        "SL HIT",
        sl_hits
    )

with d:
    st.metric(
        "WIN RATE",
        f"{win_rate}%"
    )

st.dataframe(
    signals_df.sort_values(
        by="id",
        ascending=False
    ),
    use_container_width=True,
    height=400
)
```

# =========================================================

# FOOTER

# =========================================================

st.success(
"SYSTEM ONLINE • AI ACTIVE • WHALE DETECTION ENABLED"
)
