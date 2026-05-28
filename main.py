# =========================================================
# QUANTUM X TERMINAL - ULTIMATE ELITE AI SYSTEM
# =========================================================

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
# STYLE
# =========================================================

st.markdown("""

<style>

html, body, [class*="css"] {

    background:
    linear-gradient(
        135deg,
        #020617 0%,
        #0f172a 40%,
        #111827 100%
    );

    color:white;
    font-family:Arial;
}

.block-container{
    padding-top:1rem;
}

.card{

    background:rgba(15,23,42,0.90);

    border:1px solid rgba(255,255,255,0.08);

    border-radius:22px;

    padding:20px;

    margin-bottom:20px;
}

.metric{

    background:rgba(17,24,39,0.88);

    border:1px solid rgba(255,255,255,0.08);

    border-radius:18px;

    padding:16px;

    margin-bottom:14px;
}

.title{

    font-size:46px;

    font-weight:900;

    background:linear-gradient(
        90deg,
        #38bdf8,
        #818cf8,
        #22c55e
    );

    -webkit-background-clip:text;

    -webkit-text-fill-color:transparent;
}

.buy{
    background:#14532d;
    padding:14px;
    border-radius:12px;
    text-align:center;
    font-weight:bold;
    font-size:20px;
}

.sell{
    background:#7f1d1d;
    padding:14px;
    border-radius:12px;
    text-align:center;
    font-weight:bold;
    font-size:20px;
}

.neutral{
    background:#334155;
    padding:14px;
    border-radius:12px;
    text-align:center;
    font-weight:bold;
    font-size:20px;
}

</style>

""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown("""

<div class="card">

<div class="title">
⚡ QUANTUM X TERMINAL
</div>

<div>
Institutional AI Smart Money Analyzer
</div>

</div>

""", unsafe_allow_html=True)

# =========================================================
# INDICATORS
# =========================================================

def calculate_rsi(data, period=14):

    delta = data.diff()

    gain = (
        delta.where(delta > 0, 0)
    ).rolling(period).mean()

    loss = (
        -delta.where(delta < 0, 0)
    ).rolling(period).mean()

    rs = gain / loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

def calculate_ema(data, period):

    return data.ewm(
        span=period,
        adjust=False
    ).mean()

def calculate_macd(data):

    ema12 = calculate_ema(data, 12)

    ema26 = calculate_ema(data, 26)

    macd = ema12 - ema26

    signal = calculate_ema(macd, 9)

    return macd, signal

def calculate_atr(df, period=14):

    high_low = df["high"] - df["low"]

    high_close = np.abs(
        df["high"] - df["close"].shift()
    )

    low_close = np.abs(
        df["low"] - df["close"].shift()
    )

    ranges = pd.concat(
        [
            high_low,
            high_close,
            low_close
        ],
        axis=1
    )

    true_range = np.max(
        ranges,
        axis=1
    )

    atr = pd.Series(
        true_range
    ).rolling(period).mean()

    return atr

# =========================================================
# MARKET DATA
# =========================================================

@st.cache_data(ttl=60)
def get_market():

    try:

        url = "https://api.binance.com/api/v3/ticker/24hr"

        response = requests.get(
            url,
            timeout=15
        )

        data = response.json()

        rows = []

        for coin in data:

            try:

                symbol = str(
                    coin.get("symbol", "")
                )

                if not symbol.endswith("USDT"):
                    continue

                rows.append({

                    "symbol": symbol,

                    "price": float(
                        coin.get(
                            "lastPrice",
                            0
                        )
                    ),

                    "change": float(
                        coin.get(
                            "priceChangePercent",
                            0
                        )
                    ),

                    "volume": float(
                        coin.get(
                            "quoteVolume",
                            0
                        )
                    )

                })

            except:
                pass

        df = pd.DataFrame(rows)

        df = df.sort_values(
            by="volume",
            ascending=False
        ).head(100)

        return df

    except:

        return pd.DataFrame()

# =========================================================
# KLINES
# =========================================================

@st.cache_data(ttl=30)
def get_klines(symbol, interval="15m"):

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

        return pd.DataFrame()

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

# =========================================================
# LOAD MARKET
# =========================================================

df = get_market()

# =========================================================
# METRICS
# =========================================================

btc_data = df[df["symbol"]=="BTCUSDT"]

if not btc_data.empty:
    btc_price = btc_data.iloc[0]["price"]
else:
    btc_price = 0

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.metric(
        "BTC PRICE",
        f"${btc_price:,.2f}"
    )

with c2:
    st.metric(
        "TOTAL COINS",
        len(df)
    )

with c3:
    st.metric(
        "GREEN COINS",
        len(df[df["change"] > 0])
    )

with c4:
    st.metric(
        "RED COINS",
        len(df[df["change"] < 0])
    )

# =========================================================
# TRADING TYPE
# =========================================================

trading_type = st.selectbox(

    "🎯 SELECT TRADING TYPE",

    [
        "SCALPING",
        "DAY TRADING",
        "SWING TRADING"
    ]

)

if trading_type == "SCALPING":
    timeframe = "5m"

elif trading_type == "DAY TRADING":
    timeframe = "15m"

else:
    timeframe = "1h"

# =========================================================
# AI SIGNAL SCANNER
# =========================================================

st.subheader("🔥 ELITE AI SIGNAL SCANNER")

scan_long = []
scan_short = []

coins = df["symbol"].tolist()[:75]

for coin in coins:

    try:

        kline = get_klines(
            coin,
            timeframe
        )

        if kline.empty:
            continue

        close = kline["close"]

        current_price = close.iloc[-1]

        rsi = calculate_rsi(close).iloc[-1]

        macd, signal_line = calculate_macd(close)

        macd_value = macd.iloc[-1]

        ema20 = calculate_ema(close,20).iloc[-1]

        ema50 = calculate_ema(close,50).iloc[-1]

        ema200 = calculate_ema(close,100).iloc[-1]

        atr = calculate_atr(kline).iloc[-1]

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

        # LONG

        if long_score >= 80:

            entry = current_price

            sl = current_price - (
                atr * 1.5
            )

            tp1 = current_price + (
                atr * 2
            )

            tp2 = current_price + (
                atr * 4
            )

            tp3 = current_price + (
                atr * 6
            )

            scan_long.append({

                "COIN":coin,
                "PRICE":round(current_price,4),
                "LONG %":long_score,
                "ENTRY":round(entry,4),
                "TP1":round(tp1,4),
                "TP2":round(tp2,4),
                "TP3":round(tp3,4),
                "SL":round(sl,4)

            })

            save_signal(
                coin,
                "LONG",
                timeframe,
                entry,
                tp1,
                tp2,
                tp3,
                sl,
                long_score
            )

        # SHORT

        if short_score >= 80:

            entry = current_price

            sl = current_price + (
                atr * 1.5
            )

            tp1 = current_price - (
                atr * 2
            )

            tp2 = current_price - (
                atr * 4
            )

            tp3 = current_price - (
                atr * 6
            )

            scan_short.append({

                "COIN":coin,
                "PRICE":round(current_price,4),
                "SHORT %":short_score,
                "ENTRY":round(entry,4),
                "TP1":round(tp1,4),
                "TP2":round(tp2,4),
                "TP3":round(tp3,4),
                "SL":round(sl,4)

            })

            save_signal(
                coin,
                "SHORT",
                timeframe,
                entry,
                tp1,
                tp2,
                tp3,
                sl,
                short_score
            )

    except:
        pass

# =========================================================
# SIGNAL TABLES
# =========================================================

lcol, scol = st.columns(2)

with lcol:

    st.subheader("🚀 LONG 80%+")

    if len(scan_long) > 0:

        st.dataframe(
            pd.DataFrame(scan_long),
            use_container_width=True,
            height=500
        )

    else:

        st.warning("NO LONG SIGNALS")

with scol:

    st.subheader("🔴 SHORT 80%+")

    if len(scan_short) > 0:

        st.dataframe(
            pd.DataFrame(scan_short),
            use_container_width=True,
            height=500
        )

    else:

        st.warning("NO SHORT SIGNALS")

# =========================================================
# ACCURACY DASHBOARD
# =========================================================

st.subheader("📊 ACCURACY DASHBOARD")

signals_df = pd.read_sql(
    "SELECT * FROM signals",
    conn
)

if not signals_df.empty:

    total_signals = len(signals_df)

    tp1_hits = len(
        signals_df[
            signals_df["status"] == "TP1 HIT"
        ]
    )

    tp2_hits = len(
        signals_df[
            signals_df["status"] == "TP2 HIT"
        ]
    )

    tp3_hits = len(
        signals_df[
            signals_df["status"] == "TP3 HIT"
        ]
    )

    sl_hits = len(
        signals_df[
            signals_df["status"] == "SL HIT"
        ]
    )

    a,b,c,d,e = st.columns(5)

    with a:
        st.metric("TOTAL", total_signals)

    with b:
        st.metric("TP1", tp1_hits)

    with c:
        st.metric("TP2", tp2_hits)

    with d:
        st.metric("TP3", tp3_hits)

    with e:
        st.metric("SL HIT", sl_hits)

# =========================================================
# COIN FILTER
# =========================================================

st.subheader("🔍 AI COIN FILTER")

search_coin = st.text_input(
    "Search Coin",
    ""
)

filtered_df = df[
    df["symbol"].str.contains(
        search_coin.upper(),
        na=False
    )
]

selected_coin = st.selectbox(
    "SELECT COIN",
    filtered_df["symbol"].tolist()
)

# =========================================================
# TRADINGVIEW CHART
# =========================================================

st.subheader("📈 TRADINGVIEW LIVE CHART")

tradingview_html = f"""

<div class="tradingview-widget-container">

<div id="tradingview_chart"></div>

<script type="text/javascript"
src="https://s3.tradingview.com/tv.js"></script>

<script type="text/javascript">

new TradingView.widget({{

    "width": "100%",
    "height": 700,
    "symbol": "BINANCE:{selected_coin}",
    "interval": "{timeframe}",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#0f172a",
    "enable_publishing": false,
    "container_id": "tradingview_chart"

}});

</script>

</div>

"""

st.components.v1.html(
    tradingview_html,
    height=720
)

# =========================================================
# FOOTER
# =========================================================

st.success(
    "SYSTEM ONLINE • AI ACTIVE • SMART MONEY ACTIVE • WHALE DETECTION ENABLED"
)
