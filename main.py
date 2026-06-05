# =========================================================
# QUANTUM X TERMINAL - CORE ENGINE
# =========================================================

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
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
    created_at TEXT,
    reason TEXT
)
""")

conn.commit()

# =========================================================
# MASTER SNIPER ENGINE
# =========================================================

def get_structure_data(df):

    highs = df["high"].values
    lows = df["low"].values
    closes = df["close"].values

    bos_bull = closes[-1] > max(highs[-6:-1])
    bos_bear = closes[-1] < min(lows[-6:-1])

    qm_bull = (
        highs[-3] > highs[-6]
        and lows[-1] < lows[-3]
    )

    qm_bear = (
        lows[-3] < lows[-6]
        and highs[-1] > highs[-3]
    )

    liquidity_bull = (
        lows[-2] < min(lows[-8:-3])
        and closes[-1] > closes[-2]
    )

    liquidity_bear = (
        highs[-2] > max(highs[-8:-3])
        and closes[-1] < closes[-2]
    )

    return {
        "bos_bull": bos_bull,
        "bos_bear": bos_bear,
        "qm_bull": qm_bull,
        "qm_bear": qm_bear,
        "liquidity_bull": liquidity_bull,
        "liquidity_bear": liquidity_bear
    }


def get_validation_data(df):

    volume = df["volume"]

    volume_ma = (
        volume
        .rolling(20)
        .mean()
        .iloc[-1]
    )

    price = df["close"].iloc[-1]

    atr = calculate_atr(df).iloc[-1]

    ema50 = calculate_ema(
        df["close"],
        50
    ).iloc[-1]

    rsi = calculate_rsi(
        df["close"]
    ).iloc[-1]

    return {

        "high_vol":
        volume.iloc[-1] > volume_ma * 1.1,

        "atr_ok":
        (atr / price) > 0.0005,

        "price": price,

        "ema50": ema50,

        "rsi": rsi
    }


def master_sniper_engine(df):

    struct = get_structure_data(df)
    valid = get_validation_data(df)

    bull_score = 0
    bear_score = 0

    reasons = []

    if struct["bos_bull"]:
        bull_score += 20
        reasons.append("BOS")

    if struct["qm_bull"]:
        bull_score += 15
        reasons.append("QM")

    if struct["liquidity_bull"]:
        bull_score += 15
        reasons.append("LIQ")

    if struct["bos_bear"]:
        bear_score += 20

    if struct["qm_bear"]:
        bear_score += 15

    if struct["liquidity_bear"]:
        bear_score += 15

    if valid["high_vol"]:
        bull_score += 10
        bear_score += 10
        reasons.append("VOL")

    if valid["price"] > valid["ema50"]:
        bull_score += 10

    if valid["price"] < valid["ema50"]:
        bear_score += 10

    if valid["rsi"] < 35:
        bull_score += 10

    if valid["rsi"] > 65:
        bear_score += 10

    if not valid["atr_ok"]:
        return None, "LOW_VOL"

    if bull_score >= 20 and bull_score > bear_score:
        return "LONG", " | ".join(reasons)

    if bear_score >= 20 and bear_score > bull_score:
        return "SHORT", "BEARISH_SETUP"

    return None, "NO_CONFLUENCE"

# =========================================================
# SIGNAL SAVE
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
    probability,
    reason=""
):

    try:

        existing = pd.read_sql(
            f"""
            SELECT *
            FROM signals
            WHERE coin='{coin}'
            AND signal='{signal}'
            AND timeframe='{timeframe}'
            AND status='RUNNING'
            """,
            conn
        )

        if existing.empty:

            cursor.execute(
                """
                INSERT INTO signals
                (
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
                    created_at,
                    reason
                )
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
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
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    reason
                )
            )

            conn.commit()

    except:
        pass

# =========================================================
# INDICATORS
# =========================================================

def calculate_rsi(data, period=14):

    delta = data.diff()

    gain = (
        delta.where(delta > 0, 0)
        .rolling(period)
        .mean()
    )

    loss = (
        -delta.where(delta < 0, 0)
        .rolling(period)
        .mean()
    )

    rs = gain / loss

    return 100 - (100 / (1 + rs))


def calculate_ema(data, period):

    return data.ewm(
        span=period,
        adjust=False
    ).mean()


def calculate_atr(df, period=14):

    high_low = df["high"] - df["low"]

    high_close = np.abs(
        df["high"] - df["close"].shift()
    )

    low_close = np.abs(
        df["low"] - df["close"].shift()
    )

    ranges = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    )

    true_range = np.max(
        ranges,
        axis=1
    )

    return pd.Series(
        true_range
    ).rolling(period).mean()


# =========================================================
# LEGACY SMC
# =========================================================

def detect_smc_features(df):

    highs = df["high"].values
    lows = df["low"].values
    closes = df["close"].values

    bos_bullish = False
    bos_bearish = False

    fvg_bullish = False
    fvg_bearish = False

    ob_bullish = False
    ob_bearish = False

    for i in range(-20, -3):

        if (
            closes[-1] > highs[i]
            and closes[-2] > highs[i]
        ):
            bos_bullish = True

        if (
            closes[-1] < lows[i]
            and closes[-2] < lows[i]
        ):
            bos_bearish = True

    if highs[-3] < lows[-1]:
        fvg_bullish = True

    if lows[-3] > highs[-1]:
        fvg_bearish = True

    if (
        closes[-1] > closes[-2]
        and closes[-2] > closes[-3]
        and closes[-4] < closes[-5]
    ):
        ob_bullish = True

    if (
        closes[-1] < closes[-2]
        and closes[-2] < closes[-3]
        and closes[-4] > closes[-5]
    ):
        ob_bearish = True

    return (
        bos_bullish,
        bos_bearish,
        fvg_bullish,
        fvg_bearish,
        ob_bullish,
        ob_bearish
    )


# =========================================================
# MARKET API
# =========================================================

@st.cache_data(ttl=5)
def get_market():

    endpoints = [

        "https://api.binance.com/api/v3/ticker/24hr",

        "https://api4.binance.com/api/v3/ticker/24hr",

        "https://fapi.binance.com/fapi/v1/ticker/24hr"

    ]

    for url in endpoints:

        try:

            response = requests.get(
                url,
                timeout=5
            )

            if response.status_code == 200:

                data = response.json()

                rows = []

                for coin in data:

                    symbol = str(
                        coin.get(
                            "symbol",
                            ""
                        )
                    )

                    if (
                        symbol.endswith("USDT")
                        and "_" not in symbol
                    ):

                        rows.append(
                            {
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
                            }
                        )

                if rows:

                    df = pd.DataFrame(rows)

                    return (
                        df
                        .sort_values(
                            by="volume",
                            ascending=False
                        )
                        .head(15)
                    )

        except:
            pass

    return pd.DataFrame(
        [
            {
                "symbol": "BTCUSDT",
                "price": 65000,
                "change": 1.0,
                "volume": 900000000
            }
        ]
    )


# =========================================================
# KLINE API
# =========================================================

@st.cache_data(ttl=5)
def get_klines(
    symbol,
    interval="15m"
):

    endpoints = [

        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100",

        f"https://api4.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100",

        f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit=100"

    ]

    for url in endpoints:

        try:

            response = requests.get(
                url,
                timeout=5
            )

            if response.status_code == 200:

                data = response.json()

                frame = (
                    pd.DataFrame(data)
                    .iloc[:, :6]
                )

                frame.columns = [
                    "time",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume"
                ]

                frame["time"] = pd.to_datetime(
                    frame["time"],
                    unit="ms"
                )

                for col in [
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume"
                ]:

                    frame[col] = (
                        frame[col]
                        .astype(float)
                    )

                return frame

        except:
            pass

    return pd.DataFrame()


# =========================================================
# LOAD MARKET DATA
# =========================================================

df_market = get_market()

# =========================================================
# SIGNAL STATUS ENGINE
# =========================================================

def update_live_signals_status(market_df):

    try:

        running_signals = pd.read_sql(
            """
            SELECT *
            FROM signals
            WHERE status IN
            (
                'RUNNING',
                'TP1 HIT',
                'TP2 HIT'
            )
            """,
            conn
        )

        if running_signals.empty:
            return

        for _, row in running_signals.iterrows():

            match = market_df[
                market_df["symbol"] == row["coin"]
            ]

            if match.empty:
                continue

            current_price = float(
                match.iloc[0]["price"]
            )

            new_status = row["status"]

            if row["signal"] == "LONG":

                if current_price >= row["tp3"]:
                    new_status = "TP3 HIT"

                elif current_price >= row["tp2"]:
                    new_status = "TP2 HIT"

                elif current_price >= row["tp1"]:
                    new_status = "TP1 HIT"

                elif current_price <= row["sl"]:
                    new_status = "SL HIT"

            elif row["signal"] == "SHORT":

                if current_price <= row["tp3"]:
                    new_status = "TP3 HIT"

                elif current_price <= row["tp2"]:
                    new_status = "TP2 HIT"

                elif current_price <= row["tp1"]:
                    new_status = "TP1 HIT"

                elif current_price >= row["sl"]:
                    new_status = "SL HIT"

            if new_status != row["status"]:

                cursor.execute(
                    """
                    UPDATE signals
                    SET status=?
                    WHERE id=?
                    """,
                    (
                        new_status,
                        row["id"]
                    )
                )

                conn.commit()

    except:
        pass


## =========================================================
# ACCURACY DASHBOARD
# =========================================================

def render_accuracy_dashboard(tf):

    try:

        df = pd.read_sql(
            f"""
            SELECT *
            FROM signals
            WHERE timeframe='{tf}'
            """,
            conn
        )

        if df.empty:

            a, b, c, d, e = st.columns(5)

            a.metric("TOTAL TRADES", 0)
            b.metric("LIVE RUNNING", 0)
            c.metric("WINS", 0)
            d.metric("LOSSES", 0)
            e.metric("ACCURACY", "0%")

            return

        total = len(df)

        running = len(
            df[df["status"] == "RUNNING"]
        )

        tp1 = len(
            df[df["status"] == "TP1 HIT"]
        )

        tp2 = len(
            df[df["status"] == "TP2 HIT"]
        )

        tp3 = len(
            df[df["status"] == "TP3 HIT"]
        )

        sl = len(
            df[df["status"] == "SL HIT"]
        )

        # FINAL WINS ONLY
        wins = tp3

        completed = wins + sl

        accuracy = (
            round(
                (wins / completed) * 100,
                1
            )
            if completed > 0
            else 0
        )

        best_status = "TP3 HIT" if wins > 0 else "-"

        net_score = wins - sl

        a, b, c, d, e = st.columns(5)

        a.metric(
            "📊 TOTAL TRADES",
            total
        )

        b.metric(
            "🔥 LIVE RUNNING",
            running
        )

        c.metric(
            "🟢 FINAL WINS",
            wins
        )

        d.metric(
            "🔴 LOSSES",
            sl
        )

        e.metric(
            "🎯 ACCURACY",
            f"{accuracy}%"
        )

        st.markdown("---")

        x1, x2, x3 = st.columns(3)

        x1.metric(
            "TP1 HITS",
            tp1
        )

        x2.metric(
            "TP2 HITS",
            tp2
        )

        x3.metric(
            "TP3 HITS",
            tp3
        )

        st.info(
            f"""
            Net Performance Score : {net_score}
            | Best Result : {best_status}
            """
        )

    except Exception as e:

        st.error(
            f"Dashboard Error : {e}"
        )

# =========================================================
# PREMIUM HEADER UI
# =========================================================

st.markdown("""
<style>

.main-title{
    text-align:center;
    font-size:54px;
    font-weight:900;
    color:#00F5FF;
    letter-spacing:2px;
}

.sub-title{
    text-align:center;
    font-size:18px;
    color:#B8B8B8;
    margin-bottom:10px;
}

.status-box{
    background:#111827;
    padding:15px;
    border-radius:15px;
    border:1px solid #1F2937;
    text-align:center;
    margin-bottom:15px;
}

.status-green{
    color:#22C55E;
    font-weight:bold;
}

hr{
    border:none;
    border-top:1px solid #1F2937;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-title">
🚀 QUANTUM X INSTITUTIONAL TERMINAL
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sub-title">
AI Smart Money Concepts • Liquidity Hunter • Sniper Engine
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="status-box">
<span class="status-green">
🟢 MARKET NODES ONLINE
</span>
&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
⚡ REAL-TIME BINANCE FEED
&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
🎯 AUTO SIGNAL TRACKING ACTIVE
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📈 MARKET PAIRS",
        len(df_market)
    )

with col2:
    st.metric(
        "🟢 ACTIVE FEED",
        "ONLINE"
    )

with col3:
    st.metric(
        "⚡ SCANNER",
        "RUNNING"
    )

with col4:
    st.metric(
        "🧠 ENGINE",
        "SNIPER V2"
    )

st.markdown("---")

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🎯 SCALPING 5m",
        "⚡ DAY TRADING 15m",
        "🔮 SWING 1h",
        "📜 HISTORY"
    ]
)

# =========================================================
# UNIVERSAL SCANNER
# =========================================================

def run_scanner(timeframe):

    longs = []
    shorts = []

    for coin in df_market["symbol"].tolist()[:15]:

        try:

            kline = get_klines(
                coin,
                timeframe
            )

            if len(kline) < 30:
                continue

            signal, reason = master_sniper_engine(kline)

            if not signal:
                continue

            price = kline["close"].iloc[-1]

            atr = calculate_atr(
                kline
            ).iloc[-1]

            if np.isnan(atr):
                continue

            if signal == "LONG":

                sl = price - (atr * 1.8)

                longs.append(
                    {
                        "COIN": coin,
                        "ENTRY": round(price, 4),
                        "TP1": round(price + atr * 2, 4),
                        "REASON": reason
                    }
                )

                save_signal(
                    coin,
                    "LONG",
                    timeframe,
                    price,
                    price + atr * 2,
                    price + atr * 4.5,
                    price + atr * 7,
                    sl,
                    90,
                    reason
                )

            if signal == "SHORT":

                sl = price + (atr * 1.8)

                shorts.append(
                    {
                        "COIN": coin,
                        "ENTRY": round(price, 4),
                        "TP1": round(price - atr * 2, 4),
                        "REASON": reason
                    }
                )

                save_signal(
                    coin,
                    "SHORT",
                    timeframe,
                    price,
                    price - atr * 2,
                    price - atr * 4.5,
                    price - atr * 7,
                    sl,
                    90,
                    reason
                )

        except:
            pass

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🟢 LONG SIGNALS")
        st.dataframe(
            pd.DataFrame(longs),
            use_container_width=True
        )

    with col2:
        st.subheader("🔴 SHORT SIGNALS")
        st.dataframe(
            pd.DataFrame(shorts),
            use_container_width=True
        )


# =========================================================
# 5M
# =========================================================

with tab1:

    render_accuracy_dashboard("5m")
    run_scanner("5m")

# =========================================================
# 15M
# =========================================================

with tab2:

    render_accuracy_dashboard("15m")
    run_scanner("15m")

# =========================================================
# 1H
# =========================================================

with tab3:

    render_accuracy_dashboard("1h")
    run_scanner("1h")

# =========================================================
# HISTORY
# =========================================================

with tab4:

    st.subheader("📜 SIGNAL HISTORY")

    try:

        history = pd.read_sql(
            """
            SELECT *
            FROM signals
            ORDER BY id DESC
            """,
            conn
        )

        st.dataframe(
            history,
            use_container_width=True
        )

    except:

        st.info(
            "No history available."
        )
