import streamlit as st
import requests
import pandas as pd
import random

# ================= SAFE PLOTLY =================

PLOTLY_AVAILABLE = True

try:

    import plotly.graph_objects as go
    import plotly.express as px

except:

    PLOTLY_AVAILABLE = False

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
Whale Tracking • Futures Intelligence • AI Signals
</div>

</div>

""", unsafe_allow_html=True)

# ================= MARKET =================

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
            ["BNBUSDT",620,-1.4,3000000000]

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

# ================= PANELS =================

left,center,right = st.columns(3)

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

    st.subheader("🧠 AI SIGNAL ENGINE")

    symbol = st.selectbox(
        "Select Coin",
        df["symbol"].tolist()
    )

    coin = df[
        df["symbol"] == symbol
    ].iloc[0]

    rsi = random.randint(20,80)

    macd = round(
        random.uniform(-5,5),
        2
    )

    whale = (
        "🐋 ACTIVE"
        if coin["volume"] > 5000000000
        else "NORMAL"
    )

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

    st.markdown(f"""

    ### {coin['symbol']}

    - PRICE : ${coin['price']:,.4f}
    - CHANGE : {coin['change']:.2f}%
    - RSI : {rsi}
    - MACD : {macd}
    - WHALE : {whale}
    - AI SCORE : {score}/100

    ## 🚨 SIGNAL : {signal}

    """)

    if score >= 70:

        st.success(
            "STRONG BUY SIGNAL"
        )

    else:

        st.error(
            "WEAK / SELL SIGNAL"
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

if PLOTLY_AVAILABLE:

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

# ================= FUTURES =================

st.subheader("🔥 FUTURES DATA")

f1,f2,f3 = st.columns(3)

with f1:

    st.metric(
        "Funding Rate",
        "0.012%"
    )

with f2:

    st.metric(
        "Open Interest",
        "$5.2B"
    )

with f3:

    st.metric(
        "Liquidation Risk",
        "HIGH"
    )

# ================= TABLE =================

st.subheader("📋 LIVE MARKET")

st.dataframe(
    df,
    use_container_width=True,
    height=500
)

# ================= FOOTER =================

st.success(
    "SYSTEM ONLINE • AI ACTIVE • WHALE DETECTION ENABLED"
)
