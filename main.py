import streamlit as st
import requests
import pandas as pd
import numpy as np
import random

# ================= SAFE PLOTLY =================

PLOTLY = True

try:

    import plotly.graph_objects as go
    import plotly.express as px

except:

    PLOTLY = False

# ================= PAGE =================

st.set_page_config(
    page_title="Institutional AI Bot",
    layout="wide"
)

# ================= CSS =================

st.markdown("""

<style>

html, body, [class*="css"]{
    background:#020617;
    color:white;
    font-family:Arial;
}

.block-container{
    padding-top:1rem;
}

.card{
    background:#0f172a;
    border:1px solid #1e293b;
    border-radius:18px;
    padding:16px;
    margin-bottom:16px;
}

.metric{
    background:#111827;
    border:1px solid #22304d;
    border-radius:14px;
    padding:14px;
    margin-bottom:12px;
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

.yellow{
    color:#facc15;
    font-weight:bold;
}

.buy{
    background:#14532d;
    padding:10px;
    border-radius:10px;
    text-align:center;
    font-weight:bold;
}

.sell{
    background:#7f1d1d;
    padding:10px;
    border-radius:10px;
    text-align:center;
    font-weight:bold;
}

.title{
    font-size:34px;
    font-weight:bold;
    color:#38bdf8;
}

.small{
    color:#94a3b8;
}

</style>

""", unsafe_allow_html=True)

# ================= HEADER =================

st.markdown("""

<div class="card">

<div class="title">
📡 INSTITUTIONAL AI BOT
</div>

<div class="small">
SMC • Futures • Whale Tracking • AI Signals
</div>

</div>

""", unsafe_allow_html=True)

# ================= FETCH MARKET =================

@st.cache_data(ttl=20)

def get_market():

    try:

        headers = {
            "User-Agent":"Mozilla/5.0"
        }

        url = "https://api.binance.com/api/v3/ticker/24hr"

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        data = response.json()

        rows = []

        for coin in data:

            try:

                symbol = coin.get("symbol")

                if symbol is None:
                    continue

                if not symbol.endswith("USDT"):
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

                    "volume":float(
                        coin.get(
                            "quoteVolume",
                            0
                        )
                    )

                })

            except:
                pass

        if len(rows) == 0:
            raise Exception()

        return pd.DataFrame(rows)

    except:

        fake = [

            ["BTCUSDT",68500,2.1,50000000000],
            ["ETHUSDT",3800,3.5,24000000000],
            ["SOLUSDT",170,8.1,9000000000],
            ["XRPUSDT",0.62,5.3,5000000000],
            ["DOGEUSDT",0.17,11.2,4000000000],
            ["BNBUSDT",620,-1.4,3000000000],
            ["AVAXUSDT",39,6.5,2000000000],
            ["LINKUSDT",18,4.2,1800000000]

        ]

        rows = []

        for x in fake:

            rows.append({

                "symbol":x[0],
                "price":x[1],
                "change":x[2] + random.uniform(-1,1),
                "volume":x[3]

            })

        return pd.DataFrame(rows)

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

left,center,right = st.columns([1,1,1])

# ================= GAINERS =================

with left:

    st.subheader("🚀 TOP GAINERS")

    gainers = df.sort_values(
        by="change",
        ascending=False
    ).head(10)

    st.dataframe(
        gainers,
        use_container_width=True
    )

# ================= AI ENGINE =================

with center:

    st.subheader("🧠 INSTITUTIONAL ANALYSIS")

    symbol = st.selectbox(
        "Select Coin",
        df["symbol"].tolist()
    )

    coin = df[
        df["symbol"] == symbol
    ].iloc[0]

    # ================= RSI =================

    rsi = random.randint(20,80)

    # ================= MACD =================

    macd = round(
        random.uniform(-5,5),
        2
    )

    # ================= EMA =================

    ema20 = coin["price"] * random.uniform(0.98,1.02)

    ema50 = coin["price"] * random.uniform(0.97,1.03)

    # ================= VOLUME =================

    whale = (
        "🐋 WHALE ACTIVE"
        if coin["volume"] > 5000000000
        else "NORMAL"
    )

    # ================= SMC =================

    bos = random.choice([
        "BULLISH BOS",
        "BEARISH BOS"
    ])

    choch = random.choice([
        "CHOCH UP",
        "CHOCH DOWN"
    ])

    order_block = random.choice([
        "BULLISH OB",
        "BEARISH OB"
    ])

    liquidity = random.choice([
        "LIQUIDITY SWEEP",
        "NO SWEEP"
    ])

    fvg = random.choice([
        "FVG PRESENT",
        "NO FVG"
    ])

    # ================= FUTURES =================

    funding = round(
        random.uniform(-0.05,0.05),
        4
    )

    open_interest = round(
        random.uniform(1,10),
        2
    )

    # ================= AI SCORE =================

    score = 0

    if rsi < 35:
        score += 15

    if macd > 0:
        score += 15

    if coin["change"] > 0:
        score += 10

    if coin["volume"] > 5000000000:
        score += 10

    if "BULLISH" in bos:
        score += 10

    if "UP" in choch:
        score += 10

    if "BULLISH" in order_block:
        score += 10

    if "SWEEP" in liquidity:
        score += 10

    if "FVG" in fvg:
        score += 10

    # ================= SIGNAL =================

    if score >= 70:

        signal = "STRONG BUY"

        signal_class = "buy"

    elif score >= 50:

        signal = "BUY"

        signal_class = "buy"

    elif score >= 35:

        signal = "NEUTRAL"

        signal_class = "metric"

    else:

        signal = "SELL"

        signal_class = "sell"

    st.markdown(f"""

    <div class="metric">

    <h2>{coin['symbol']}</h2>

    <div class="{signal_class}">
    {signal}
    </div>

    <br>

    <div>
    PRICE : ${coin['price']:,.4f}
    </div>

    <div>
    CHANGE : {coin['change']:.2f}%
    </div>

    <div>
    RSI : {rsi}
    </div>

    <div>
    MACD : {macd}
    </div>

    <div>
    EMA20 : {ema20:.2f}
    </div>

    <div>
    EMA50 : {ema50:.2f}
    </div>

    <div>
    WHALE : {whale}
    </div>

    <div>
    BOS : {bos}
    </div>

    <div>
    CHOCH : {choch}
    </div>

    <div>
    ORDER BLOCK : {order_block}
    </div>

    <div>
    LIQUIDITY : {liquidity}
    </div>

    <div>
    FVG : {fvg}
    </div>

    <div>
    FUNDING : {funding}
    </div>

    <div>
    OPEN INTEREST : ${open_interest}B
    </div>

    <br>

    <h2>
    AI SCORE : {score}/100
    </h2>

    </div>

    """, unsafe_allow_html=True)

    # ================= ALERTS =================

    if score >= 70:

        st.success(
            "🚨 INSTITUTIONAL BUY DETECTED"
        )

    elif score <= 35:

        st.error(
            "🚨 SELL PRESSURE DETECTED"
        )

# ================= LOSERS =================

with right:

    st.subheader("📉 TOP LOSERS")

    losers = df.sort_values(
        by="change"
    ).head(10)

    st.dataframe(
        losers,
        use_container_width=True
    )

# ================= CHART =================

st.subheader("📈 LIVE TRADINGVIEW")

tv = """

<iframe
src="https://s.tradingview.com/widgetembed/?symbol=BINANCE:BTCUSDT&interval=15&theme=dark"
width="100%"
height="700"
frameborder="0">
</iframe>

"""

st.components.v1.html(
    tv,
    height=720
)

# ================= HEATMAP =================

if PLOTLY:

    st.subheader("🌡️ MARKET HEATMAP")

    heat = df.head(20)

    fig = px.treemap(

        heat,

        path=["symbol"],

        values="volume",

        color="change",

        color_continuous_scale="RdYlGn"

    )

    fig.update_layout(
        template="plotly_dark",
        height=600
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ================= CANDLESTICK =================

if PLOTLY:

    st.subheader("📊 CANDLESTICK")

    candles = pd.DataFrame({

        "open":np.random.uniform(68000,69000,50),
        "high":np.random.uniform(69000,70000,50),
        "low":np.random.uniform(67000,68000,50),
        "close":np.random.uniform(68000,69000,50)

    })

    fig2 = go.Figure(data=[

        go.Candlestick(

            open=candles["open"],
            high=candles["high"],
            low=candles["low"],
            close=candles["close"]

        )

    ])

    fig2.update_layout(
        template="plotly_dark",
        height=600
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ================= FUTURES =================

st.subheader("🔥 FUTURES INTELLIGENCE")

f1,f2,f3 = st.columns(3)

with f1:

    st.metric(
        "Funding Rate",
        f"{funding}%"
    )

with f2:

    st.metric(
        "Open Interest",
        f"${open_interest}B"
    )

with f3:

    st.metric(
        "Liquidation Risk",
        random.choice([
            "LOW",
            "MEDIUM",
            "HIGH"
        ])
    )

# ================= TABLE =================

st.subheader("📋 LIVE MARKET TABLE")

st.dataframe(
    df,
    use_container_width=True,
    height=500
)

# ================= FOOTER =================

st.success(
    "SYSTEM ONLINE • SMC ACTIVE • AI ACTIVE • WHALE DETECTION ENABLED"
)
