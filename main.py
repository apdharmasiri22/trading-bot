import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ================= PAGE =================

st.set_page_config(
    page_title="QUANTUM X AI",
    layout="wide"
)

# ================= STYLE =================

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

    background:rgba(15,23,42,0.85);

    backdrop-filter:blur(12px);

    border:1px solid rgba(255,255,255,0.08);

    border-radius:22px;

    padding:20px;

    margin-bottom:20px;
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

<div>
Institutional Smart Money Intelligence
</div>

</div>

""", unsafe_allow_html=True)

# ================= RSI =================

def calculate_rsi(data, period=14):

    delta = data.diff()

    gain = (delta.where(delta > 0, 0)).rolling(period).mean()

    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

# ================= EMA =================

def calculate_ema(data, period):

    return data.ewm(span=period, adjust=False).mean()

# ================= MACD =================

def calculate_macd(data):

    ema12 = calculate_ema(data, 12)

    ema26 = calculate_ema(data, 26)

    macd = ema12 - ema26

    signal = calculate_ema(macd, 9)

    return macd, signal

# ================= MARKET =================

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

# ================= KLINES =================

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

    for col in [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]:

        frame[col] = frame[col].astype(float)

    return frame

# ================= LOAD =================

df = get_market()

# ================= METRICS =================

btc = df[df["symbol"]=="BTCUSDT"].iloc[0]

c1,c2,c3,c4 = st.columns(4)

with c1:

    st.metric(
        "BTC PRICE",
        f"${btc['price']:,.2f}"
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

# ================= MAIN =================

left,center,right = st.columns([1,1.2,1])

# ================= GAINERS =================

with left:

    st.subheader("🚀 TOP GAINERS")

    gainers = df.sort_values(
        by="change",
        ascending=False
    ).head(20)

    st.dataframe(
        gainers,
        use_container_width=True,
        height=600
    )

# ================= ANALYSIS =================

with center:

    st.subheader("🧠 AI ANALYSIS")

    symbol = st.selectbox(
        "Select Coin",
        df["symbol"].tolist()
    )

    kline = get_klines(symbol)

    close = kline["close"]

    # ================= REAL INDICATORS =================

    rsi = calculate_rsi(close).iloc[-1]

    macd, signal_line = calculate_macd(close)

    macd_value = macd.iloc[-1]

    ema20 = calculate_ema(close,20).iloc[-1]

    ema50 = calculate_ema(close,50).iloc[-1]

    ema200 = calculate_ema(close,100).iloc[-1]

    # ================= WHALE =================

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

    liquidity = (
        "LIQUIDITY SWEEP"
        if last_high > prev_high
        and close.iloc[-1] < prev_high
        else "NO SWEEP"
    )

    # ================= SCORE =================

    score = 0

    if rsi < 35:
        score += 20

    if macd_value > 0:
        score += 20

    if ema20 > ema50:
        score += 20

    if ema50 > ema200:
        score += 20

    if whale == "🐋 WHALE ACTIVE":
        score += 10

    if "BULLISH" in bos:
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

    <div>MACD : {macd_value:.2f}</div>

    <div>EMA20 : {ema20:.2f}</div>

    <div>EMA50 : {ema50:.2f}</div>

    <div>EMA200 : {ema200:.2f}</div>

    <div>WHALE : {whale}</div>

    <div>BOS : {bos}</div>

    <div>CHOCH : {choch}</div>

    <div>LIQUIDITY : {liquidity}</div>

    <br>

    <h2>
    AI SCORE : {score}/100
    </h2>

    </div>

    """, unsafe_allow_html=True)

# ================= LOSERS =================

with right:

    st.subheader("📉 TOP LOSERS")

    losers = df.sort_values(
        by="change"
    ).head(20)

    st.dataframe(
        losers,
        use_container_width=True,
        height=600
    )

# ================= CHART =================

st.subheader("📊 CANDLESTICK")

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

st.subheader("🌡️ HEATMAP")

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

# ================= SEARCH =================

st.subheader("🔍 SEARCH")

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

# ================= FOOTER =================

st.success(
    "SYSTEM ONLINE • AI ACTIVE • SMART MONEY ACTIVE"
)
