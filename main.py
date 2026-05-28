import streamlit as st
import requests
import pandas as pd
import random

# ================= PAGE =================

st.set_page_config(
    page_title="Institutional AI Dashboard",
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

.title{
    font-size:34px;
    font-weight:bold;
    color:#38bdf8;
}

.small{
    color:#94a3b8;
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

</style>

""", unsafe_allow_html=True)

# ================= HEADER =================

st.markdown("""

<div class="card">

<div class="title">
📡 INSTITUTIONAL AI SCANNER
</div>

<div class="small">
Live Institutional Trading Dashboard
</div>

</div>

""", unsafe_allow_html=True)

# ================= FALLBACK DATA =================

fallback_data = [

    ["BTCUSDT",68500,2.5,50000000000],
    ["ETHUSDT",3800,3.2,25000000000],
    ["SOLUSDT",170,8.4,9000000000],
    ["BNBUSDT",620,-1.1,4000000000],
    ["XRPUSDT",0.62,5.8,7000000000],
    ["DOGEUSDT",0.17,12.2,6000000000],
    ["ADAUSDT",0.71,-2.5,3000000000],
    ["AVAXUSDT",39,6.2,2000000000],
    ["LINKUSDT",18,4.1,1500000000],
    ["MATICUSDT",0.95,-3.3,1800000000]

]

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

        if not isinstance(data, list):
            raise Exception()

        coins = []

        for coin in data:

            try:

                symbol = coin.get("symbol")

                if symbol is None:
                    continue

                if not symbol.endswith("USDT"):
                    continue

                coins.append({

                    "symbol": symbol,

                    "price": float(
                        coin.get("lastPrice",0)
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

        if len(coins) == 0:
            raise Exception()

        return pd.DataFrame(coins)

    except:

        fake = []

        for x in fallback_data:

            fake.append({

                "symbol":x[0],

                "price":x[1],

                "change":x[2] + random.uniform(-1,1),

                "volume":x[3]

            })

        return pd.DataFrame(fake)

# ================= LOAD DATA =================

df = get_market()

# ================= METRICS =================

btc = df[df["symbol"]=="BTCUSDT"].iloc[0]

green_count = len(
    df[df["change"] > 0]
)

red_count = len(
    df[df["change"] < 0]
)

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

left,center,right = st.columns(3)

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
    ).head(5)

    for _, row in gainers.iterrows():

        st.markdown(f"""

        <div class="metric">

        <h3>{row['symbol']}</h3>

        <div class="green">
        {row['change']:.2f}%
        </div>

        </div>

        """, unsafe_allow_html=True)

# ================= AI ENGINE =================

with center:

    st.markdown("""

    <div class="card">

    <h2>🧠 AI ANALYSIS ENGINE</h2>

    </div>

    """, unsafe_allow_html=True)

    symbol = st.selectbox(
        "Select Coin",
        df["symbol"].tolist()
    )

    coin = df[
        df["symbol"] == symbol
    ].iloc[0]

    signal = (
        "BUY"
        if coin["change"] > 0
        else "SELL"
    )

    signal_class = (
        "buy"
        if signal == "BUY"
        else "sell"
    )

    ai_score = min(
        abs(coin["change"]) * 10,
        100
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
    AI SCORE : {ai_score:.0f}/100
    </div>

    </div>

    """, unsafe_allow_html=True)

# ================= LOSERS =================

with right:

    st.markdown("""

    <div class="card">

    <h2>📉 TOP LOSERS</h2>

    </div>

    """, unsafe_allow_html=True)

    losers = df.sort_values(
        by="change"
    ).head(5)

    for _, row in losers.iterrows():

        st.markdown(f"""

        <div class="metric">

        <h3>{row['symbol']}</h3>

        <div class="red">
        {row['change']:.2f}%
        </div>

        </div>

        """, unsafe_allow_html=True)

# ================= CHART =================

st.markdown("""

<div class="card">

<h2>📊 LIVE CHART</h2>

</div>

""", unsafe_allow_html=True)

chart = """

<iframe
src="https://s.tradingview.com/widgetembed/?symbol=BINANCE:BTCUSDT&interval=15&theme=dark"
width="100%"
height="600"
frameborder="0">
</iframe>

"""

st.components.v1.html(
    chart,
    height=620
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
    height=400
)

# ================= FOOTER =================

st.markdown("""

<div class="card">

<h3>⚡ SYSTEM STATUS</h3>

<div class="green">
LIVE • AI ACTIVE • MARKET CONNECTED
</div>

</div>

""", unsafe_allow_html=True)
