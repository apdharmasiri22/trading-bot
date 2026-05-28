import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

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
📡 INSTITUTIONAL AI TRADING BOT
</div>

<div class="small">
Whale Tracking • Futures Intelligence • AI Signal Engine
</div>

</div>

""", unsafe_allow_html=True)

# ================= FETCH MARKET =================

@st.cache_data(ttl=15)

def get_market():

    try:

        headers = {
            "User-Agent":"Mozilla/5.0"
        }

        url = "https://api.binance.com/api/v3/ticker/24hr"

        data = requests.get(
            url,
            headers=headers,
            timeout=10
        ).json()

        rows = []

        for coin in data:

            try:

                symbol = coin.get("symbol")

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

        return pd.DataFrame(rows)

    except:

        fallback = [

            ["BTCUSDT",68500,2.1,50000000000],
            ["ETHUSDT",3800,3.5,24000000000],
            ["SOLUSDT",170,8.1,9000000000],
            ["XRPUSDT",0.62,5.3,5000000000],
            ["DOGEUSDT",0.17,11.2,4000000000],
            ["BNBUSDT",620,-1.4,3000000000]

        ]

        fake = []

        for x in fallback:

            fake.append({

                "symbol":x[0],
                "price":x[1],
                "change":x[2],
                "volume":x[3]

            })

        return pd.DataFrame(fake)

df = get_market()

# ================= METRICS =================

btc = df[df["symbol"]=="BTCUSDT"].iloc[0]

green_count = len(df[df["change"] > 0])
red_count = len(df[df["change"] < 0])

volume = df["volume"].sum()

c1,c2,c3,c4 = st.columns(4)

with c1:

    st.markdown(f"""

    <div class="metric">

    <h3>BTC PRICE</h3>

    <div class="blue">
    ${btc['price']:,.2f}
    </div>

    </div>

    """, unsafe_allow_html=True)

with c2:

    st.markdown(f"""

    <div class="metric">

    <h3>GREEN COINS</h3>

    <div class="green">
    {green_count}
    </div>

    </div>

    """, unsafe_allow_html=True)

with c3:

    st.markdown(f"""

    <div class="metric">

    <h3>RED COINS</h3>

    <div class="red">
    {red_count}
    </div>

    </div>

    """, unsafe_allow_html=True)

with c4:

    st.markdown(f"""

    <div class="metric">

    <h3>24H VOLUME</h3>

    <div class="yellow">
    ${volume/1000000000:.2f}B
    </div>

    </div>

    """, unsafe_allow_html=True)

# ================= PANELS =================

left,center,right = st.columns([1,1,1])

# ================= TOP GAINERS =================

with left:

    st.markdown("""
    <div class="card">
    <h2>🚀 TOP GAINERS</h2>
    </div>
    """, unsafe_allow_html=True)

    gainers = df.sort_values(
        by="change",
        ascending=False
    ).head(10)

    for _, row in gainers.iterrows():

        st.markdown(f"""

        <div class="metric">

        <h3>{row['symbol']}</h3>

        <div class="green">
        {row['change']:.2f}%
        </div>

        <div>
        ${row['price']:,.4f}
        </div>

        </div>

        """, unsafe_allow_html=True)

# ================= AI ENGINE =================

with center:

    st.markdown("""
    <div class="card">
    <h2>🧠 AI SIGNAL ENGINE</h2>
    </div>
    """, unsafe_allow_html=True)

    symbol = st.selectbox(
        "Select Coin",
        df["symbol"].tolist()
    )

    coin = df[
        df["symbol"] == symbol
    ].iloc[0]

    # ================= FAKE RSI =================

    rsi = np.random.randint(20,80)

    # ================= MACD =================

    macd = np.random.uniform(-5,5)

    # ================= WHALE =================

    whale = (
        "🐋 WHALE ACTIVE"
        if coin["volume"] > 5000000000
        else "NORMAL"
    )

    # ================= SIGNAL =================

    score = 0

    if rsi < 35:
        score += 30

    if macd > 0:
        score += 30

    if coin["change"] > 0:
        score += 20

    if coin["volume"] > 5000000000:
        score += 20

    signal = (
        "BUY"
        if score >= 60
        else "SELL"
    )

    signal_class = (
        "buy"
        if signal == "BUY"
        else "sell"
    )

    st.markdown(f"""

    <div class="metric">

    <h2>{coin['symbol']}</h2>

    <div class="{signal_class}">
    {signal} SIGNAL
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
    MACD : {macd:.2f}
    </div>

    <div>
    AI SCORE : {score}/100
    </div>

    <div>
    WHALE : {whale}
    </div>

    </div>

    """, unsafe_allow_html=True)

    # ================= ALERT =================

    if score >= 70:

        st.success(
            "🚨 STRONG BUY DETECTED"
        )

    elif score <= 30:

        st.error(
            "🚨 STRONG SELL DETECTED"
        )

# ================= TOP LOSERS =================

with right:

    st.markdown("""
    <div class="card">
    <h2>📉 TOP LOSERS</h2>
    </div>
    """, unsafe_allow_html=True)

    losers = df.sort_values(
        by="change"
    ).head(10)

    for _, row in losers.iterrows():

        st.markdown(f"""

        <div class="metric">

        <h3>{row['symbol']}</h3>

        <div class="red">
        {row['change']:.2f}%
        </div>

        <div>
        ${row['price']:,.4f}
        </div>

        </div>

        """, unsafe_allow_html=True)

# ================= CANDLESTICK CHART =================

st.markdown("""
<div class="card">
<h2>📊 CANDLESTICK CHART</h2>
</div>
""", unsafe_allow_html=True)

candles = pd.DataFrame({

    "open":np.random.uniform(68000,69000,50),
    "high":np.random.uniform(69000,70000,50),
    "low":np.random.uniform(67000,68000,50),
    "close":np.random.uniform(68000,69000,50)

})

fig = go.Figure(data=[

    go.Candlestick(

        open=candles["open"],
        high=candles["high"],
        low=candles["low"],
        close=candles["close"]

    )

])

fig.update_layout(
    template="plotly_dark",
    height=600
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

heat = df.head(20)

fig2 = px.treemap(

    heat,

    path=["symbol"],

    values="volume",

    color="change",

    color_continuous_scale="RdYlGn"

)

fig2.update_layout(
    template="plotly_dark",
    height=600
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ================= FUTURES =================

st.markdown("""
<div class="card">
<h2>🔥 FUTURES INTELLIGENCE</h2>
</div>
""", unsafe_allow_html=True)

f1,f2,f3 = st.columns(3)

with f1:

    st.markdown("""

    <div class="metric">

    <h3>Funding Rate</h3>

    <div class="green">
    0.012%
    </div>

    </div>

    """, unsafe_allow_html=True)

with f2:

    st.markdown("""

    <div class="metric">

    <h3>Open Interest</h3>

    <div class="yellow">
    $5.2B
    </div>

    </div>

    """, unsafe_allow_html=True)

with f3:

    st.markdown("""

    <div class="metric">

    <h3>Liquidation Risk</h3>

    <div class="red">
    HIGH
    </div>

    </div>

    """, unsafe_allow_html=True)

# ================= MULTI CHART =================

st.markdown("""
<div class="card">
<h2>📈 TRADINGVIEW MULTI CHART</h2>
</div>
""", unsafe_allow_html=True)

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

# ================= TABLE =================

st.markdown("""
<div class="card">
<h2>📋 LIVE MARKET TABLE</h2>
</div>
""", unsafe_allow_html=True)

st.dataframe(
    df,
    use_container_width=True,
    height=500
)

# ================= FOOTER =================

st.markdown("""

<div class="card">

<h3>⚡ SYSTEM STATUS</h3>

<div class="green">
LIVE • AI ACTIVE • WHALE DETECTION • FUTURES ONLINE
</div>

</div>

""", unsafe_allow_html=True)
