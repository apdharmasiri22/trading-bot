```python
import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(
    page_title="Institutional AI Dashboard",
    layout="wide"
)

# ===================== CSS =====================

st.markdown("""

<style>

html, body, [class*="css"]{
    background:#020617;
    color:white;
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
    text-align:center;
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

# ===================== HEADER =====================

st.markdown("""

<div class="card">

<div class="title">
📡 INSTITUTIONAL AI SCANNER
</div>

<div class="small">
Live Binance Market Intelligence Dashboard
</div>

</div>

""", unsafe_allow_html=True)

# ===================== FETCH DATA =====================

@st.cache_data(ttl=20)

def get_market():

    url = "https://api.binance.com/api/v3/ticker/24hr"

    data = requests.get(url).json()

    usdt = []

    for coin in data:

        if coin["symbol"].endswith("USDT"):

            usdt.append({

                "symbol": coin["symbol"],
                "price": float(coin["lastPrice"]),
                "change": float(coin["priceChangePercent"]),
                "volume": float(coin["quoteVolume"])

            })

    df = pd.DataFrame(usdt)

    return df

df = get_market()

# ===================== TOP AI PICKS =====================

top_gainers = df.sort_values(
    by="change",
    ascending=False
).head(10)

top_losers = df.sort_values(
    by="change"
).head(10)

# ===================== MARKET METRICS =====================

btc = df[df["symbol"] == "BTCUSDT"].iloc[0]

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown(f"""

    <div class="metric">

    <h3>BTC PRICE</h3>

    <div class="blue">
    ${btc['price']:,.2f}
    </div>

    </div>

    """, unsafe_allow_html=True)

with col2:

    green_count = len(df[df["change"] > 0])

    st.markdown(f"""

    <div class="metric">

    <h3>GREEN COINS</h3>

    <div class="green">
    {green_count}
    </div>

    </div>

    """, unsafe_allow_html=True)

with col3:

    red_count = len(df[df["change"] < 0])

    st.markdown(f"""

    <div class="metric">

    <h3>RED COINS</h3>

    <div class="red">
    {red_count}
    </div>

    </div>

    """, unsafe_allow_html=True)

with col4:

    volume = df["volume"].sum()

    st.markdown(f"""

    <div class="metric">

    <h3>24H VOLUME</h3>

    <div class="blue">
    ${volume/1000000000:.2f}B
    </div>

    </div>

    """, unsafe_allow_html=True)

# ===================== MAIN GRID =====================

left, center, right = st.columns([1,1,1])

# ===================== GAINERS =====================

with left:

    st.markdown("""

    <div class="card">

    <h2>🚀 TOP GAINERS</h2>

    </div>

    """, unsafe_allow_html=True)

    for _, row in top_gainers.iterrows():

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

# ===================== AI ANALYSIS =====================

with center:

    st.markdown("""

    <div class="card">

    <h2>🧠 AI ANALYSIS ENGINE</h2>

    </div>

    """, unsafe_allow_html=True)

    symbol = st.text_input(
        "Coin Symbol",
        "BTCUSDT"
    )

    selected = df[df["symbol"] == symbol]

    if not selected.empty:

        coin = selected.iloc[0]

        signal = "LONG" if coin["change"] > 0 else "SHORT"

        signal_color = "green" if signal == "LONG" else "red"

        strength = abs(coin["change"]) * 10

        if strength > 100:
            strength = 100

        st.markdown(f"""

        <div class="metric">

        <h2>{coin['symbol']}</h2>

        <div class="{signal_color}">
        SIGNAL : {signal}
        </div>

        <br>

        <div>
        PRICE : ${coin['price']:,.4f}
        </div>

        <div>
        CHANGE : {coin['change']:.2f}%
        </div>

        <div>
        AI SCORE : {strength:.0f}/100
        </div>

        </div>

        """, unsafe_allow_html=True)

        if signal == "LONG":

            st.success(
                "AI DETECTED BULLISH MOMENTUM"
            )

        else:

            st.error(
                "AI DETECTED BEARISH MOMENTUM"
            )

# ===================== LOSERS =====================

with right:

    st.markdown("""

    <div class="card">

    <h2>📉 TOP LOSERS</h2>

    </div>

    """, unsafe_allow_html=True)

    for _, row in top_losers.iterrows():

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

# ===================== LIVE TABLE =====================

st.markdown("""

<div class="card">

<h2>📊 LIVE MARKET TABLE</h2>

</div>

""", unsafe_allow_html=True)

table = df.sort_values(
    by="volume",
    ascending=False
)[["symbol","price","change","volume"]]

st.dataframe(
    table,
    use_container_width=True,
    height=500
)

# ===================== AUTO REFRESH =====================

time.sleep(1)
st.rerun()
```
