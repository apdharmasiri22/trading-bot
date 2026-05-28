import streamlit as st
import requests
import pandas as pd
import time

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
    padding:8px;
    border-radius:10px;
    text-align:center;
    font-weight:bold;
}

.sell{
    background:#7f1d1d;
    padding:8px;
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
Live Binance Institutional Dashboard
</div>

</div>

""", unsafe_allow_html=True)

# ================= SAFE FETCH =================

@st.cache_data(ttl=15)

def get_market():

```
try:

    url = "https://api.binance.com/api/v3/ticker/24hr"

    response = requests.get(url, timeout=10)

    data = response.json()

    if not isinstance(data, list):
        return pd.DataFrame()

    coins = []

    for coin in data:

        try:

            symbol = coin.get("symbol")

            if not symbol:
                continue

            if not symbol.endswith("USDT"):
                continue

            coins.append({

                "symbol": symbol,
                "price": float(coin.get("lastPrice", 0)),
                "change": float(coin.get("priceChangePercent", 0)),
                "volume": float(coin.get("quoteVolume", 0)),
                "high": float(coin.get("highPrice", 0)),
                "low": float(coin.get("lowPrice", 0))

            })

        except:
            continue

    return pd.DataFrame(coins)

except:
    return pd.DataFrame()
```

# ================= LOAD DATA =================

df = get_market()

if df.empty:

```
st.error("BINANCE API ERROR OR RATE LIMIT")

st.stop()
```

# ================= METRICS =================

btc_rows = df[df["symbol"] == "BTCUSDT"]

if len(btc_rows) > 0:
btc = btc_rows.iloc[0]
else:
btc = {
"price":0
}

green_count = len(df[df["change"] > 0])
red_count = len(df[df["change"] < 0])

total_volume = df["volume"].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:

```
st.markdown(f"""

<div class="metric">

<h3>BTC PRICE</h3>

<div class="blue">
${btc['price']:,.2f}
</div>

</div>

""", unsafe_allow_html=True)
```

with col2:

```
st.markdown(f"""

<div class="metric">

<h3>GREEN COINS</h3>

<div class="green">
{green_count}
</div>

</div>

""", unsafe_allow_html=True)
```

with col3:

```
st.markdown(f"""

<div class="metric">

<h3>RED COINS</h3>

<div class="red">
{red_count}
</div>

</div>

""", unsafe_allow_html=True)
```

with col4:

```
st.markdown(f"""

<div class="metric">

<h3>24H VOLUME</h3>

<div class="yellow">
${total_volume/1000000000:.2f}B
</div>

</div>

""", unsafe_allow_html=True)
```

# ================= PANELS =================

left, center, right = st.columns([1,1,1])

# ================= GAINERS =================

with left:

```
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
```

# ================= AI ENGINE =================

with center:

```
st.markdown("""
<div class="card">
<h2>🧠 AI ANALYSIS ENGINE</h2>
</div>
""", unsafe_allow_html=True)

symbol = st.text_input(
    "Coin Symbol",
    "BTCUSDT"
).upper()

selected = df[df["symbol"] == symbol]

if not selected.empty:

    coin = selected.iloc[0]

    signal = "BUY" if coin["change"] > 0 else "SELL"

    signal_class = "buy" if signal == "BUY" else "sell"

    ai_score = min(
        abs(coin["change"]) * 10,
        100
    )

    volatility = (
        (coin["high"] - coin["low"])
        / max(coin["price"], 1)
    ) * 100

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
    VOLATILITY : {volatility:.2f}%
    </div>

    <div>
    AI SCORE : {ai_score:.0f}/100
    </div>

    </div>

    """, unsafe_allow_html=True)
```

# ================= LOSERS =================

with right:

```
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
```

# ================= TABLE =================

st.markdown("""

<div class="card">
<h2>📋 LIVE MARKET TABLE</h2>
</div>
""", unsafe_allow_html=True)

table = df.sort_values(
by="volume",
ascending=False
)[[
"symbol",
"price",
"change",
"volume"
]]

st.dataframe(
table,
use_container_width=True,
height=500
)

# ================= AUTO REFRESH =================

time.sleep(2)
st.rerun()
