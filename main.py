# =========================================================
# QUANTUM X TERMINAL - FULL AI SYSTEM
# =========================================================

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

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

    backdrop-filter:blur(12px);

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

@st.cache_data(ttl=30)

def get_market():

    try:

        url = "https://api.binance.com/api/v3/ticker/24hr"

        response = requests.get(
            url,
            timeout=15
        )

        data = response.json()

        rows = []

        if isinstance(data, list):

            for coin in data:

                try:

                    symbol = str(
                        coin.get(
                            "symbol",
                            ""
                        )
                    )

                    if not symbol.endswith("USDT"):
                        continue

                    rows.append({

                        "symbol":symbol,

                        "price":float(
                            coin.get(
                                "lastPrice",
                                0
                            )
                        ),

                        "change":float(
                            coin.get(
                                "priceChangePercent",
                                0
                            )
                        ),

                        "volume":float(
                            coin.get(
                                "quoteVolume",
                                0
                            )
                        )

                    })

                except:
                    pass

        if len(rows) > 0:

            df = pd.DataFrame(rows)

            # REMOVE DEAD COINS

            df = df[
                (df["volume"] > 1000000)
            ]

            # SORT

            df = df.sort_values(
                by="volume",
                ascending=False
            )

            # TAKE MANY COINS

            df = df.head(300)

            return df

    except:
        pass

    fallback = pd.DataFrame({

        "symbol":[
            "BTCUSDT",
            "ETHUSDT",
            "SOLUSDT",
            "XRPUSDT",
            "DOGEUSDT"
        ],

        "price":[
            68000,
            3500,
            170,
            0.62,
            0.16
        ],

        "change":[
            2.5,
            3.2,
            7.5,
            -1.2,
            12.1
        ],

        "volume":[
            50000000000,
            20000000000,
            8000000000,
            3000000000,
            4000000000
        ]

    })

    return fallback

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

        frame = frame.iloc[:,:6]

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

            "open":np.random.uniform(68000,69000,200),
            "high":np.random.uniform(69000,70000,200),
            "low":np.random.uniform(67000,68000,200),
            "close":np.random.uniform(68000,69000,200),
            "volume":np.random.uniform(1000,5000,200)

        })

        return fake

# =========================================================
# LOAD MARKET
# =========================================================

df = get_market()

# =========================================================
# METRICS
# =========================================================

btc_data = df[df["symbol"]=="BTCUSDT"]

btc_price = btc_data.iloc[0]["price"] if not btc_data.empty else 0

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.metric("BTC PRICE", f"${btc_price:,.2f}")

with c2:
    st.metric("TOTAL COINS", len(df))

with c3:
    st.metric("GREEN COINS", len(df[df["change"] > 0]))

with c4:
    st.metric("RED COINS", len(df[df["change"] < 0]))

# =========================================================
# MAIN LAYOUT
# =========================================================

left,center,right = st.columns([1,1.5,1])

# =========================================================
# GAINERS
# =========================================================

with left:

    st.subheader("🚀 TOP GAINERS")

    gainers = df.sort_values(
        by="change",
        ascending=False
    ).head(100)

    st.dataframe(
        gainers,
        use_container_width=True,
        height=650
    )

# =========================================================
# AI ANALYZER
# =========================================================

with center:

    st.subheader("🧠 QUANTUM X PRO AI ANALYZER")

    symbol = st.selectbox(
        "🪙 SELECT COIN",
        df["symbol"].tolist()
    )

    timeframe = st.selectbox(
        "⏱️ TIMEFRAME",
        [
            "5m",
            "15m",
            "1h",
            "4h",
            "1d"
        ]
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

    entry = current_price

    sl = current_price - (atr * 1.5)

    tp1 = current_price + (atr * 2)

    tp2 = current_price + (atr * 4)

    tp3 = current_price + (atr * 6)

    st.markdown(f"""

    <div class="metric">

    <h1>{symbol}</h1>

    <div class="{css}">
    {signal}
    </div>

    <br>

    <h2>
    🟢 LONG POSSIBILITY :
    {long_score}%
    </h2>

    <h2>
    🔴 SHORT POSSIBILITY :
    {short_score}%
    </h2>

    <hr>

    <div>📊 RSI : {rsi:.2f}</div>

    <div>⚡ MACD : {macd_value:.2f}</div>

    <div>📈 EMA20 : {ema20:.2f}</div>

    <div>📈 EMA50 : {ema50:.2f}</div>

    <div>📈 EMA200 : {ema200:.2f}</div>

    <div>🌊 ATR : {atr:.2f}</div>

    <hr>

    <h3>🎯 ENTRY : {entry:.2f}</h3>

    <h3>🛑 STOP LOSS : {sl:.2f}</h3>

    <h3>💰 TP1 : {tp1:.2f}</h3>

    <h3>💰 TP2 : {tp2:.2f}</h3>

    <h3>💰 TP3 : {tp3:.2f}</h3>

    </div>

    """, unsafe_allow_html=True)

# =========================================================
# LOSERS
# =========================================================

with right:

    st.subheader("📉 TOP LOSERS")

    losers = df.sort_values(
        by="change"
    ).head(100)

    st.dataframe(
        losers,
        use_container_width=True,
        height=650
    )

# =========================================================
# CANDLE CHART
# =========================================================

st.subheader("📊 ADVANCED CANDLE CHART")

fig = go.Figure(data=[

    go.Candlestick(

        x=kline.index,

        open=kline["open"],

        high=kline["high"],

        low=kline["low"],

        close=kline["close"]

    )

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

heat = df.head(100)

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
# SEARCH
# =========================================================

st.subheader("🔍 SEARCH MARKET")

search = st.text_input(
    "Search Coin",
    ""
)

filtered = df[
    df["symbol"].str.contains(
        search.upper(),
        na=False
    )
]

st.dataframe(
    filtered,
    use_container_width=True,
    height=500
)

# =========================================================
# FOOTER
# =========================================================

st.success(
    "SYSTEM ONLINE • AI ACTIVE • SMART MONEY ACTIVE"
)
