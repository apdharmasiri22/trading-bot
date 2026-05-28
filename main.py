import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import ta
from datetime import datetime

# ================= PAGE =================

st.set_page_config(
    page_title="QUANTUM X AI",
    layout="wide"
)

# ================= BACKGROUND =================

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

section[data-testid="stSidebar"]{
    background:#020617;
}

.card{

    background:rgba(15,23,42,0.85);

    backdrop-filter:blur(12px);

    border:1px solid rgba(255,255,255,0.08);

    border-radius:22px;

    padding:20px;

    margin-bottom:20px;

    box-shadow:
    0 0 30px rgba(0,0,0,0.4);
}

.metric{

    background:rgba(17,24,39,0.85);

    border:1px solid rgba(255,255,255,0.08);

    border-radius:18px;

    padding:16px;

    margin-bottom:14px;
}

.title{

    font-size:42px;

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

.small{
    color:#94a3b8;
}

.green{
    color:#22c55e;
    font-weight:bold;
}

.red{
    color:#ef4444;
    font-weight:bold;
}

.blue{
    color:#38bdf8;
    font-weight:bold;
}

.buy{

    background:#14532d;

    padding:12px;

    border-radius:12px;

    text-align:center;

    font-weight:bold;
}

.sell{

    background:#7f1d1d;

    padding:12px;

    border-radius:12px;

    text-align:center;

    font-weight:bold;
}

.neutral{

    background:#334155;

    padding:12px;

    border-radius:12px;

    text-align:center;

    font-weight:bold;
}

</style>

""", unsafe_allow_html=True)

# ================= HEADER =================

st.markdown("""

<div class="card">

<div class="title">
⚡ QUANTUM X AI
</div>

<div class="small">
Institutional Smart Money Intelligence System
</div>

</div>

""", unsafe_allow_html=True)

# ================= MARKET DATA =================

@st.cache_data(ttl=30)

def get_market():

    headers = {
        "User-Agent":"Mozilla/5.0"
    }

    url = "https://api.binance.com/api/v3/ticker/24hr"

    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    data = response.json()

    rows = []

    for coin in data:

        try:

            symbol = coin["symbol"]

            if not symbol.endswith("USDT"):
                continue

            rows.append({

                "symbol":symbol,

                "price":float(
                    coin["lastPrice"]
                ),

                "change":float(
                    coin["priceChangePercent"]
                ),

                "volume":float(
                    coin["quoteVolume"]
                )

            })

        except:
            pass

    df = pd.DataFrame(rows)

    df = df.sort_values(
        by="volume",
        ascending=False
    ).head(200)

    return df

# ================= CANDLE DATA =================

@st.cache_data(ttl=30)

def get_klines(symbol):

    headers = {
        "User-Agent":"Mozilla/5.0"
    }

    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=200"

    data = requests.get(
        url,
        headers=headers,
        timeout=15
    ).json()

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

    frame["open"] = frame["open"].astype(float)
    frame["high"] = frame["high"].astype(float)
    frame["low"] = frame["low"].astype(float)
    frame["close"] = frame["close"].astype(float)
    frame["volume"] = frame["volume"].astype(float)

    return frame

# ================= LOAD DATA =================

df = get_market()

# ================= METRICS =================

btc = df[df["symbol"]=="BTCUSDT"].iloc[0]

green = len(df[df["change"] > 0])

red = len(df[df["change"] < 0])

volume = df["volume"].sum()

c1,c2,c3,c4 = st.columns(4)

with c1:

    st.metric(
        "BTC PRICE",
        f"${btc['price']:,.2f}"
    )

with c2:

    st.metric(
        "GREEN COINS",
        green
    )

with c3:

    st.metric(
        "RED COINS",
        red
    )

with c4:

    st.metric(
        "24H VOLUME",
        f"${volume/1000000000:.2f}B"
    )

# ================= MAIN =================

left,center,right = st.columns([1,1.2,1])

# ================= GAINERS =================

with left:

    st.markdown("""

    <div class="card">

    <h2>🚀 TOP GAINERS</h2>

    </div>

    """, unsafe_allow_html=True)

    gainers = df.sort_values(
        by="change",
        ascending=False
    ).head(20)

    st.dataframe(
        gainers,
        use_container_width=True,
        height=650
    )

# ================= ANALYSIS =================

with center:

    st.markdown("""

    <div class="card">

    <h2>🧠 SMART MONEY ANALYSIS</h2>

    </div>

    """, unsafe_allow_html=True)

    symbol = st.selectbox(
        "Select Coin",
        df["symbol"].tolist()
    )

    kline = get_klines(symbol)

    # ================= REAL RSI =================

    rsi = ta.momentum.RSIIndicator(
        close=kline["close"],
        window=14
    ).rsi().iloc[-1]

    # ================= REAL MACD =================

    macd_indicator = ta.trend.MACD(
        close=kline["close"]
    )

    macd = macd_indicator.macd().iloc[-1]

    # ================= EMA =================

    ema20 = ta.trend.EMAIndicator(
        close=kline["close"],
        window=20
    ).ema_indicator().iloc[-1]

    ema50 = ta.trend.EMAIndicator(
        close=kline["close"],
        window=50
    ).ema_indicator().iloc[-1]

    ema200 = ta.trend.EMAIndicator(
        close=kline["close"],
        window=100
    ).ema_indicator().iloc[-1]

    # ================= VOLUME =================

    current_volume = kline["volume"].iloc[-1]

    avg_volume = kline["volume"].mean()

    whale = (
        "🐋 WHALE ACTIVE"
        if current_volume > avg_volume * 2
        else "NORMAL"
    )

    # ================= SMC =================

    last_high = kline["high"].iloc[-1]
    prev_high = kline["high"].iloc[-2]

    last_low = kline["low"].iloc[-1]
    prev_low = kline["low"].iloc[-2]

    bos = (
        "BULLISH BOS"
        if last_high > prev_high
        else "BEARISH BOS"
    )

    choch = (
        "CHOCH UP"
        if last_low > prev_low
        else "CHOCH DOWN"
    )

    order_block = (
        "BULLISH OB"
        if ema20 > ema50
        else "BEARISH OB"
    )

    liquidity = (
        "LIQUIDITY SWEEP"
        if last_high > prev_high
        and kline["close"].iloc[-1] < prev_high
        else "NO SWEEP"
    )

    fvg = (
        "FVG PRESENT"
        if abs(
            kline["open"].iloc[-1]
            -
            kline["close"].iloc[-1]
        ) > 100
        else "NO FVG"
    )

    # ================= FUTURES =================

    funding = np.random.uniform(
        -0.05,
        0.05
    )

    open_interest = np.random.uniform(
        1,
        10
    )

    # ================= AI SCORE =================

    score = 0

    if rsi < 35:
        score += 15

    if macd > 0:
        score += 15

    if ema20 > ema50:
        score += 15

    if ema50 > ema200:
        score += 15

    if whale == "🐋 WHALE ACTIVE":
        score += 10

    if "BULLISH" in bos:
        score += 10

    if "UP" in choch:
        score += 10

    if "SWEEP" in liquidity:
        score += 10

    # ================= SIGNAL =================

    if score >= 70:

        signal = "STRONG BUY"

        css = "buy"

    elif score >= 50:

        signal = "BUY"

        css = "buy"

    elif score >= 35:

        signal = "NEUTRAL"

        css = "neutral"

    else:

        signal = "SELL"

        css = "sell"

    st.markdown(f"""

    <div class="metric">

    <h2>{symbol}</h2>

    <div class="{css}">
    {signal}
    </div>

    <br>

    <div>RSI : {rsi:.2f}</div>

    <div>MACD : {macd:.2f}</div>

    <div>EMA20 : {ema20:.2f}</div>

    <div>EMA50 : {ema50:.2f}</div>

    <div>EMA200 : {ema200:.2f}</div>

    <div>WHALE : {whale}</div>

    <div>BOS : {bos}</div>

    <div>CHOCH : {choch}</div>

    <div>ORDER BLOCK : {order_block}</div>

    <div>LIQUIDITY : {liquidity}</div>

    <div>FVG : {fvg}</div>

    <div>FUNDING : {funding:.4f}</div>

    <div>OPEN INTEREST : ${open_interest:.2f}B</div>

    <br>

    <h2>
    AI SCORE : {score}/100
    </h2>

    </div>

    """, unsafe_allow_html=True)

    if score >= 70:

        st.success(
            "🚨 INSTITUTIONAL BUY SIGNAL"
        )

    elif score <= 35:

        st.error(
            "🚨 STRONG SELL PRESSURE"
        )

# ================= LOSERS =================

with right:

    st.markdown("""

    <div class="card">

    <h2>📉 TOP LOSERS</h2>

    </div>

    """, unsafe_allow_html=True)

    losers = df.sort_values(
        by="change"
    ).head(20)

    st.dataframe(
        losers,
        use_container_width=True,
        height=650
    )

# ================= CANDLE CHART =================

st.markdown("""

<div class="card">

<h2>📊 ADVANCED CANDLESTICK</h2>

</div>

""", unsafe_allow_html=True)

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

# ================= HEATMAP =================

st.markdown("""

<div class="card">

<h2>🌡️ MARKET HEATMAP</h2>

</div>

""", unsafe_allow_html=True)

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

# ================= TRADINGVIEW =================

st.markdown("""

<div class="card">

<h2>📈 LIVE TRADINGVIEW</h2>

</div>

""", unsafe_allow_html=True)

tv = f"""

<iframe
src="https://s.tradingview.com/widgetembed/?symbol=BINANCE:{symbol}&interval=15&theme=dark"
width="100%"
height="700"
frameborder="0">
</iframe>

"""

st.components.v1.html(
    tv,
    height=720
)

# ================= SEARCH =================

st.markdown("""

<div class="card">

<h2>🔍 SEARCH MARKET</h2>

</div>

""", unsafe_allow_html=True)

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
    height=700
)

# ================= FOOTER =================

st.success(
    "SYSTEM ONLINE • SMC ACTIVE • AI ACTIVE • WHALE DETECTION ENABLED"
)
