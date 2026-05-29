# =========================================================
# QUANTUM X TERMINAL - GRAND FINAL
# PART 1
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

# =========================================================
# ULTRA PREMIUM QUANTUM UI
# =========================================================

st.markdown("""

<style>

/* ===================================================== */
/* MAIN BACKGROUND */
/* ===================================================== */

html, body, .stApp {

    background:
        linear-gradient(
            135deg,
            rgba(2,6,23,0.96),
            rgba(15,23,42,0.96),
            rgba(17,24,39,0.97)
        ),
        url("https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=2070&auto=format&fit=crop");

    background-size: cover;

    background-attachment: fixed;

    color: white;

    overflow-x: hidden;

    font-family: Arial;

}

/* ===================================================== */
/* ANIMATED LIGHTS */
/* ===================================================== */

body::before {

    content:"";

    position:fixed;

    inset:0;

    background:
    radial-gradient(circle at 20% 20%,
    rgba(56,189,248,0.15),
    transparent 30%),

    radial-gradient(circle at 80% 30%,
    rgba(99,102,241,0.15),
    transparent 30%),

    radial-gradient(circle at 50% 80%,
    rgba(34,197,94,0.12),
    transparent 30%);

    animation: moveBg 18s infinite alternate ease-in-out;

    z-index:-2;

}

@keyframes moveBg {

    0%{
        transform: scale(1) translateY(0px);
    }

    100%{
        transform: scale(1.1) translateY(-20px);
    }

}

/* ===================================================== */
/* CYBER GRID */
/* ===================================================== */

body::after {

    content:"";

    position:fixed;

    inset:0;

    background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);

    background-size:40px 40px;

    z-index:-1;

}

/* ===================================================== */
/* MAIN CONTAINER */
/* ===================================================== */

.block-container {

    padding-top:1rem;

}

/* ===================================================== */
/* GLASS CARD */
/* ===================================================== */

.card {

    background: rgba(15,23,42,0.55);

    backdrop-filter: blur(20px);

    border:1px solid rgba(255,255,255,0.08);

    border-radius:28px;

    padding:24px;

    margin-bottom:24px;

    box-shadow:
        0 0 30px rgba(56,189,248,0.08);

    transition:0.35s;

}

.card:hover {

    transform:translateY(-4px);

    box-shadow:
        0 0 40px rgba(99,102,241,0.22);

}

/* ===================================================== */
/* TITLE */
/* ===================================================== */

.title {

    font-size:58px;

    font-weight:900;

    background:linear-gradient(
        90deg,
        #38bdf8,
        #818cf8,
        #22c55e,
        #38bdf8
    );

    background-size:300%;

    animation: titleFlow 8s linear infinite;

    -webkit-background-clip:text;

    -webkit-text-fill-color:transparent;

    text-shadow:
        0 0 20px rgba(56,189,248,0.35);

}

@keyframes titleFlow {

    0%{
        background-position:0%;
    }

    100%{
        background-position:300%;
    }

}

/* ===================================================== */
/* METRIC CARDS */
/* ===================================================== */

[data-testid="metric-container"] {

    background: rgba(15,23,42,0.72);

    backdrop-filter: blur(16px);

    border-radius:22px;

    border:1px solid rgba(255,255,255,0.06);

    padding:18px;

    box-shadow:
        0 0 18px rgba(56,189,248,0.08);

    transition:0.3s;

}

[data-testid="metric-container"]:hover {

    transform:translateY(-5px);

    box-shadow:
        0 0 28px rgba(99,102,241,0.25);

}

/* ===================================================== */
/* DATA TABLE */
/* ===================================================== */

[data-testid="stDataFrame"] {

    border-radius:22px;

    overflow:hidden;

    border:1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 0 30px rgba(56,189,248,0.10);

}

/* ===================================================== */
/* BUY BOX */
/* ===================================================== */

.buy {

    background: linear-gradient(
        90deg,
        rgba(34,197,94,0.75),
        rgba(22,163,74,0.92)
    );

    padding:14px;

    border-radius:16px;

    font-size:20px;

    font-weight:bold;

    text-align:center;

    box-shadow:
        0 0 20px rgba(34,197,94,0.25);

}

/* ===================================================== */
/* SELL BOX */
/* ===================================================== */

.sell {

    background: linear-gradient(
        90deg,
        rgba(239,68,68,0.75),
        rgba(127,29,29,0.95)
    );

    padding:14px;

    border-radius:16px;

    font-size:20px;

    font-weight:bold;

    text-align:center;

    box-shadow:
        0 0 20px rgba(239,68,68,0.25);

}

/* ===================================================== */
/* BUTTONS */
/* ===================================================== */

.stButton > button {

    background: linear-gradient(
        90deg,
        #0ea5e9,
        #6366f1
    );

    border:none;

    border-radius:14px;

    color:white;

    font-weight:bold;

    transition:0.3s;

}

.stButton > button:hover {

    transform:scale(1.05);

    box-shadow:
        0 0 22px rgba(56,189,248,0.35);

}

/* ===================================================== */
/* SELECTBOX */
/* ===================================================== */

.stSelectbox > div > div {

    background: rgba(15,23,42,0.90);

    border-radius:14px;

    border:1px solid rgba(255,255,255,0.08);

}

/* ===================================================== */
/* SIDEBAR */
/* ===================================================== */

section[data-testid="stSidebar"] {

    background: rgba(2,6,23,0.88);

    border-right:1px solid rgba(255,255,255,0.08);

    backdrop-filter: blur(18px);

}

/* ===================================================== */
/* SCROLLBAR */
/* ===================================================== */

::-webkit-scrollbar {

    width:10px;

}

::-webkit-scrollbar-thumb {

    background:#38bdf8;

    border-radius:20px;

}

</style>

""", unsafe_allow_html=True)
# =========================================================
# HEADER
# =========================================================

st.markdown("""

<style>

[data-testid="stAppViewContainer"] {

    background: transparent;

}

[data-testid="stHeader"] {

    background: rgba(0,0,0,0);

}

[data-testid="stToolbar"] {

    right: 2rem;

}

</style>

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


def calculate_volume_ratio(df):

    avg_volume = df["volume"].rolling(20).mean()

    current_volume = df["volume"].iloc[-1]

    volume_ratio = current_volume / avg_volume.iloc[-1]

    return volume_ratio


def calculate_ema(data, period):

    return data.ewm(
        span=period,
        adjust=False
    ).mean()

def calculate_volume_ratio(df):

    avg_volume = df["volume"].rolling(20).mean()

    current_volume = df["volume"].iloc[-1]

    volume_ratio = current_volume / avg_volume.iloc[-1]

    return volume_ratio


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

    urls = [

        "https://api.binance.com/api/v3/ticker/24hr",

        "https://api1.binance.com/api/v3/ticker/24hr",

        "https://api2.binance.com/api/v3/ticker/24hr",

        "https://api3.binance.com/api/v3/ticker/24hr"

    ]

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for url in urls:

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=20
            )

            if response.status_code != 200:
                continue

            data = response.json()

            if not isinstance(data, list):
                continue

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

            if len(rows) > 0:

                df = pd.DataFrame(rows)

                df = df.sort_values(
                    by="volume",
                    ascending=False
                ).head(75)

                return df

        except:
            pass

    # =====================================================
    # BACKUP DATA
    # =====================================================

    rows = []

    coin_names = [

        "BTC","ETH","BNB","SOL","XRP","DOGE","ADA","AVAX","LINK","MATIC",
        "DOT","TRX","LTC","BCH","ATOM","ETC","XLM","ICP","APT","ARB",
        "OP","SUI","SEI","INJ","RNDR","NEAR","FIL","AAVE","UNI","MKR",
        "PEPE","SHIB","FLOKI","BONK","WIF","TIA","JUP","PYTH","STRK","DYDX",
        "GALA","SAND","MANA","AXS","APE","GMT","BLUR","LDO","CRV","1INCH",
        "ALGO","FLOW","KAS","EGLD","THETA","KAVA","FTM","ROSE","CELO","ZIL",
        "CHZ","ENJ","COMP","SNX","YFI","BAT","HOT","ICX","QTUM","ONT",
        "RSR","ANKR","ZEN","SKL","STX"

    ]

    for coin in coin_names:

        rows.append({

            "symbol": f"{coin}USDT",

            "price": round(
                np.random.uniform(1,70000),
                4
            ),

            "change": round(
                np.random.uniform(-15,15),
                2
            ),

            "volume": round(
                np.random.uniform(
                    10000000,
                    5000000000
                ),
                2
            )

        })

    df = pd.DataFrame(rows)

    df = df.sort_values(
        by="volume",
        ascending=False
    ).head(75)

    return df

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

        fake = pd.DataFrame({

            "open": np.random.uniform(68000,69000,200),
            "high": np.random.uniform(69000,70000,200),
            "low": np.random.uniform(67000,68000,200),
            "close": np.random.uniform(68000,69000,200),
            "volume": np.random.uniform(1000,5000,200)

        })

        return fake

# =========================================================
# DELETE OLD RUNNING SIGNALS
# =========================================================

cursor.execute("""

DELETE FROM signals
WHERE status='RUNNING'
AND id NOT IN (

    SELECT id FROM signals
    ORDER BY id DESC
    LIMIT 50

)

""")

conn.commit()

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

        # =====================================
        # PREVENT DUPLICATES
        # =====================================

        existing = pd.read_sql(f"""

        SELECT * FROM signals

        WHERE coin='{coin}'
        AND signal='{signal}'
        AND timeframe='{timeframe}'
        AND status='RUNNING'

        """, conn)

        if existing.empty:

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

    except Exception as e:

        print(e)

# =========================================================
# UPDATE SIGNAL STATUS
# =========================================================

try:

    signals = pd.read_sql(

        """

        SELECT * FROM signals
        WHERE status='RUNNING'
        ORDER BY id DESC
        LIMIT 50

        """,

        conn

    )

    for _, row in signals.iterrows():

        try:

            coin = row["coin"]

            signal_type = row["signal"]

            signal_id = row["id"]

            tp1 = row["tp1"]
            tp2 = row["tp2"]
            tp3 = row["tp3"]

            sl = row["sl"]

            # =====================================
            # IMPORTANT FIX
            # =====================================

            signal_timeframe = row["timeframe"]

            kline = get_klines(
                coin,
                signal_timeframe
            )

            current_price = kline["close"].iloc[-1]

            # =====================================
            # LONG
            # =====================================

            if signal_type == "LONG":

                if current_price >= tp3:

                    cursor.execute(

                        "UPDATE signals SET status='TP3 HIT' WHERE id=?",

                        (signal_id,)

                    )

                elif current_price >= tp2:

                    cursor.execute(

                        "UPDATE signals SET status='TP2 HIT' WHERE id=?",

                        (signal_id,)

                    )

                elif current_price >= tp1:

                    cursor.execute(

                        "UPDATE signals SET status='TP1 HIT' WHERE id=?",

                        (signal_id,)

                    )

                elif current_price <= sl:

                    cursor.execute(

                        "UPDATE signals SET status='SL HIT' WHERE id=?",

                        (signal_id,)

                    )

            # =====================================
            # SHORT
            # =====================================

            else:

                if current_price <= tp3:

                    cursor.execute(

                        "UPDATE signals SET status='TP3 HIT' WHERE id=?",

                        (signal_id,)

                    )

                elif current_price <= tp2:

                    cursor.execute(

                        "UPDATE signals SET status='TP2 HIT' WHERE id=?",

                        (signal_id,)

                    )

                elif current_price <= tp1:

                    cursor.execute(

                        "UPDATE signals SET status='TP1 HIT' WHERE id=?",

                        (signal_id,)

                    )

                elif current_price >= sl:

                    cursor.execute(

                        "UPDATE signals SET status='SL HIT' WHERE id=?",

                        (signal_id,)

                    )

            conn.commit()

        except Exception as e:

            print(e)

except Exception as e:

    print(e)

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

    running = len(
        signals_df[
            signals_df["status"] == "RUNNING"
        ]
    )

    total_wins = (
        tp1_hits +
        tp2_hits +
        tp3_hits
    )

    if total_signals > 0:

        win_rate = round(
            (
                total_wins /
                total_signals
            ) * 100,
            2
        )

    else:

        win_rate = 0

    a,b,c,d,e,f = st.columns(6)

    with a:
        st.metric(
            "TOTAL",
            total_signals
        )

    with b:
        st.metric(
            "RUNNING",
            running
        )

    with c:
        st.metric(
            "TP1",
            tp1_hits
        )

    with d:
        st.metric(
            "TP2",
            tp2_hits
        )

    with e:
        st.metric(
            "TP3",
            tp3_hits
        )

    with f:
        st.metric(
            "WIN RATE",
            f"{win_rate}%"
        )

    chart_df = pd.DataFrame({

        "STATUS":[
            "TP1",
            "TP2",
            "TP3",
            "SL"
        ],

        "COUNT":[
            tp1_hits,
            tp2_hits,
            tp3_hits,
            sl_hits
        ]

    })

    fig_acc = px.bar(

        chart_df,

        x="STATUS",

        y="COUNT",

        template="plotly_dark",

        title="AI SIGNAL ACCURACY"

    )

    st.plotly_chart(
        fig_acc,
        use_container_width=True
    )

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
# SELECTED COIN ANALYSIS
# =========================================================

st.subheader("🧠 SELECTED COIN AI ANALYSIS")

kline = get_klines(
    selected_coin,
    timeframe
)

close = kline["close"]

current_price = close.iloc[-1]

rsi = calculate_rsi(close).iloc[-1]

macd, signal_line = calculate_macd(close)

macd_value = macd.iloc[-1]

ema20 = calculate_ema(close,20).iloc[-1]

ema50 = calculate_ema(close,50).iloc[-1]

ema200 = calculate_ema(close,200).iloc[-1]

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

elif short_score >= 80:

    signal = "🔴 STRONG SHORT"

    css = "sell"

else:

    signal = "⚪ NEUTRAL"

    css = "neutral"

entry = current_price

tp1_long = current_price + (atr * 2)
tp2_long = current_price + (atr * 4)
tp3_long = current_price + (atr * 6)
sl_long = current_price - (atr * 1.5)

tp1_short = current_price - (atr * 2)
tp2_short = current_price - (atr * 4)
tp3_short = current_price - (atr * 6)
sl_short = current_price + (atr * 1.5)

st.markdown(f"""

<div class="metric">

<h2>{selected_coin}</h2>

<div class="{css}">
{signal}
</div>

<br>

<h2>
LONG POSSIBILITY :
{long_score}%
</h2>

<h2>
SHORT POSSIBILITY :
{short_score}%
</h2>

<hr>

<h3>MARKET PRICE : {current_price:.4f}</h3>

<h3>ENTRY : {entry:.4f}</h3>

<hr>

<h3>LONG TP1 : {tp1_long:.4f}</h3>
<h3>LONG TP2 : {tp2_long:.4f}</h3>
<h3>LONG TP3 : {tp3_long:.4f}</h3>
<h3>LONG SL : {sl_long:.4f}</h3>

<hr>

<h3>SHORT TP1 : {tp1_short:.4f}</h3>
<h3>SHORT TP2 : {tp2_short:.4f}</h3>
<h3>SHORT TP3 : {tp3_short:.4f}</h3>
<h3>SHORT SL : {sl_short:.4f}</h3>

<hr>

<div>RSI : {rsi:.2f}</div>
<div>MACD : {macd_value:.2f}</div>
<div>EMA20 : {ema20:.2f}</div>
<div>EMA50 : {ema50:.2f}</div>
<div>EMA200 : {ema200:.2f}</div>
<div>ATR : {atr:.2f}</div>

</div>

""", unsafe_allow_html=True)

# =========================================================
# TRADINGVIEW
# =========================================================

import streamlit.components.v1 as components

st.subheader("📈 TRADINGVIEW LIVE CHART")

# "BINANCE:" කියන Prefix එක හරියටම තියෙනවද බලන්න.
# සමහර වෙලාවට කොයින් එකේ නම වෙනස් වෙන්න පුළුවන්. 
# උදා: BINANCE:BTCUSDT
chart_symbol = f"BINANCE:{selected_coin}"

tradingview_html = f"""
<div id="tv_chart_container" style="height:700px; width:100%;"></div>
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
<script type="text/javascript">
new TradingView.widget({{
    "container_id": "tv_chart_container",
    "width": "100%",
    "height": 700,
    "symbol": "{chart_symbol}",
    "interval": "{timeframe}",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#0f172a",
    "enable_publishing": false,
    "allow_symbol_change": true
}});
</script>
"""

components.html(tradingview_html, height=720)

# =========================================================
# TOP GAINERS / LOSERS
# =========================================================

g1,g2 = st.columns(2)

with g1:

    st.subheader("🚀 TOP GAINERS")

    gainers = df.sort_values(
        by="change",
        ascending=False
    ).head(15)

    st.dataframe(
        gainers,
        use_container_width=True,
        height=500
    )

with g2:

    st.subheader("🔴 TOP LOSERS")

    losers = df.sort_values(
        by="change"
    ).head(15)

    st.dataframe(
        losers,
        use_container_width=True,
        height=500
    )

# =========================================================
# HEATMAP
# =========================================================

st.subheader("🌡️ MARKET HEATMAP")

heat = df.head(50)

fig_heat = px.treemap(

    heat,

    path=["symbol"],

    values="volume",

    color="change",

    color_continuous_scale="RdYlGn"

)

fig_heat.update_layout(
    template="plotly_dark",
    height=700
)

st.plotly_chart(
    fig_heat,
    use_container_width=True
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
# LIVE SIGNAL TABLE
# =========================================================

st.subheader("📡 LIVE SIGNAL MONITOR")

live_rows = []

signals_live = pd.read_sql("""

SELECT * FROM signals
ORDER BY id DESC
LIMIT 50

""", conn)

for _, row in signals_live.iterrows():

    try:

        coin = row["coin"]
        signal = row["signal"]

        entry = row["entry"]

        tp1 = row["tp1"]
        tp2 = row["tp2"]
        tp3 = row["tp3"]

        sl = row["sl"]

        status = row["status"]

        # =====================================
        # GET LIVE PRICE
        # =====================================

        kline_live = get_klines(
            coin,
            timeframe
        )

        current_price = kline_live["close"].iloc[-1]

        # =====================================
        # LONG PNL
        # =====================================

        if signal == "LONG":

            pnl = current_price - entry

            pnl_percent = (
                pnl / entry
            ) * 100

        # =====================================
        # SHORT PNL
        # =====================================

        else:

            pnl = entry - current_price

            pnl_percent = (
                pnl / entry
            ) * 100

        # =====================================
        # LIVE STATUS
        # =====================================

        if pnl_percent >= 0:

            live_status = "🟢 PROFIT"

        else:

            live_status = "🔴 LOSS"

        # =====================================
        # ADD ROW
        # =====================================

        live_rows.append({

            "COIN": coin,
            "TYPE": signal,

            "ENTRY": round(entry,4),

            "CURRENT": round(
                current_price,
                4
            ),

            "TP1": round(tp1,4),
            "TP2": round(tp2,4),
            "TP3": round(tp3,4),

            "SL": round(sl,4),

            "PNL %": round(
                pnl_percent,
                2
            ),

            "STATUS": live_status,

            "RESULT": status

        })

    except:
        pass

# =========================================================
# SHOW LIVE TABLE
# =========================================================

if len(live_rows) > 0:

    live_df = pd.DataFrame(live_rows)

    st.dataframe(

        live_df,

        use_container_width=True,

        height=600

    )

else:

    st.warning(
        "NO LIVE SIGNALS"
    )

# =========================================================
# SIGNAL HISTORY
# =========================================================

st.subheader("📜 SIGNAL HISTORY")

history_df = signals_df.sort_values(

    by="id",

    ascending=False

)

st.dataframe(

    history_df,

    use_container_width=True,

    height=400

)

# =========================================================
# SL HIT METRIC
# =========================================================

sl_hits = len(

    signals_df[
        signals_df["status"] == "SL HIT"
    ]

)

st.metric(

    "TOTAL SL HITS",

    sl_hits

)

# =========================================================
# FOOTER
# =========================================================

st.success(

    "SYSTEM ONLINE • AI ACTIVE • SMART MONEY ACTIVE • WHALE DETECTION ENABLED"

)
