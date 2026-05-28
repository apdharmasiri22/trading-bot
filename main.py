# ================================
# 👑 ALPHA TERMINAL v4.6
# MORE SIGNALS + LIVE DATA
# ================================

import numpy as np
import pandas as pd
import requests
import streamlit as st
import concurrent.futures
import streamlit.components.v1 as components
import datetime
import time

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ALPHA TERMINAL v4.6",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# UI
# =========================================================

st.markdown("""
<style>

.stApp{
    background-color:#0d1117;
    color:white;
}

h1,h2,h3,h4{
    color:white !important;
}

[data-testid="stMetricValue"]{
    color:#ffb703;
    font-size:28px;
}

section[data-testid="stSidebar"]{
    background-color:#111827;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SAFE SESSION
# =========================================================

session = requests.Session()

retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429,500,502,503,504]
)

session.mount(
    "https://",
    HTTPAdapter(max_retries=retries)
)

# =========================================================
# COINS
# =========================================================

COIN_SYMBOLS = {

    "BTCUSDT":"₿ BTCUSDT",
    "ETHUSDT":"♦️ ETHUSDT",
    "SOLUSDT":"☀️ SOLUSDT",
    "BNBUSDT":"🔶 BNBUSDT",
    "XRPUSDT":"💧 XRPUSDT",
    "ADAUSDT":"₳ ADAUSDT",
    "DOGEUSDT":"🐕 DOGEUSDT",
    "AVAXUSDT":"🔺 AVAXUSDT",
    "DOTUSDT":"● DOTUSDT",
    "LINKUSDT":"🔗 LINKUSDT",
    "MATICUSDT":"💜 MATICUSDT",
    "LTCUSDT":"Ł LTCUSDT",
    "UNIUSDT":"🦄 UNIUSDT",
    "ATOMUSDT":"⚛️ ATOMUSDT",
    "TRXUSDT":"🔴 TRXUSDT",
    "APTUSDT":"🌀 APTUSDT",
    "ARBUSDT":"🔵 ARBUSDT",
    "OPUSDT":"🔴 OPUSDT",
    "SUIUSDT":"💧 SUIUSDT",
    "INJUSDT":"💉 INJUSDT"

}

SCAN_COINS = list(COIN_SYMBOLS.keys())

# =========================================================
# API
# =========================================================

@st.cache_data(ttl=300)
def get_crypto_data(symbol, interval, limit=100):

    url = "https://data-api.binance.vision/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    try:

        response = session.get(
            url,
            params=params,
            timeout=20,
            headers={
                "User-Agent":"Mozilla/5.0"
            }
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if not isinstance(data, list):
            return None

        columns = [
            "Time",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "CloseTime",
            "QuoteAssetVol",
            "NumTrades",
            "TakerBuyBase",
            "TakerBuyQuote",
            "Ignore"
        ]

        df = pd.DataFrame(data, columns=columns)

        for col in ["Open","High","Low","Close","Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df.dropna(inplace=True)

        return df

    except:
        return None

# =========================================================
# INDICATORS
# =========================================================

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / (avg_loss + 1e-10)

    return 100 - (100 / (1 + rs))

def calculate_macd(series):

    ema12 = calculate_ema(series, 12)
    ema26 = calculate_ema(series, 26)

    macd = ema12 - ema26
    signal = calculate_ema(macd, 9)

    return macd, signal

def calculate_atr(df, period=14):

    high_low = df["High"] - df["Low"]

    high_close = abs(df["High"] - df["Close"].shift())

    low_close = abs(df["Low"] - df["Close"].shift())

    ranges = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    )

    true_range = ranges.max(axis=1)

    atr = true_range.rolling(period).mean()

    return atr

def calculate_adx(df, period=14):

    plus_dm = df["High"].diff()
    minus_dm = df["Low"].diff()

    plus_dm = plus_dm.where(
        (plus_dm > minus_dm) & (plus_dm > 0),
        0
    )

    minus_dm = minus_dm.where(
        (minus_dm > plus_dm) & (minus_dm > 0),
        0
    )

    tr1 = df["High"] - df["Low"]
    tr2 = abs(df["High"] - df["Close"].shift())
    tr3 = abs(df["Low"] - df["Close"].shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()

    plus_di = 100 * (
        plus_dm.rolling(period).mean() / atr
    )

    minus_di = 100 * (
        minus_dm.rolling(period).mean() / atr
    )

    dx = (
        abs(plus_di - minus_di) /
        (plus_di + minus_di + 1e-10)
    ) * 100

    adx = dx.rolling(period).mean()

    return adx

# =========================================================
# ANALYSIS ENGINE
# =========================================================

def analyze_coin(symbol, htf, ltf):

    df_htf = get_crypto_data(symbol, htf, 120)
    df_ltf = get_crypto_data(symbol, ltf, 120)

    if (
        df_htf is None or
        df_ltf is None or
        df_htf.empty or
        df_ltf.empty
    ):
        return None

    if len(df_htf) < 50 or len(df_ltf) < 50:
        return None

    # EMA TREND
    df_htf["EMA50"] = calculate_ema(
        df_htf["Close"],
        50
    )

    trend = (
        "BULLISH"
        if df_htf["Close"].iloc[-1] >
        df_htf["EMA50"].iloc[-1]
        else "BEARISH"
    )

    # RSI
    df_ltf["RSI"] = calculate_rsi(
        df_ltf["Close"]
    )

    rsi = df_ltf["RSI"].iloc[-1]

    # MACD
    macd, signal = calculate_macd(
        df_ltf["Close"]
    )

    # ATR
    df_ltf["ATR"] = calculate_atr(df_ltf)

    atr = df_ltf["ATR"].iloc[-1]

    # ADX
    df_ltf["ADX"] = calculate_adx(df_ltf)

    adx = df_ltf["ADX"].iloc[-1]

    if np.isnan(adx):
        adx = 0

    # VOLUME
    avg_volume = df_ltf["Volume"].rolling(20).mean()

    volume_ok = (
        df_ltf["Volume"].iloc[-1] >
        avg_volume.iloc[-1]
    )

    bullish = 0
    bearish = 0

    # =====================================================
    # NEW MORE ACTIVE SIGNAL SYSTEM
    # =====================================================

    # TREND
    if trend == "BULLISH":
        bullish += 30
    else:
        bearish += 30

    # RSI
    if rsi < 45:
        bullish += 20

    if rsi > 55:
        bearish += 20

    # MACD
    if macd.iloc[-1] > signal.iloc[-1]:
        bullish += 30
    else:
        bearish += 30

    # ADX
    if adx > 15:
        bullish += 10
        bearish += 10

    # VOLUME
    if volume_ok:
        bullish += 10
        bearish += 10

    current_price = df_ltf["Close"].iloc[-1]

    if np.isnan(atr):
        atr = current_price * 0.003

    # BUY
    if bullish >= 45 and trend == "BULLISH":

        return {
            "Coin": symbol,
            "Signal": "🟩 BUY",
            "Score": bullish,
            "Price": current_price,
            "SL": current_price - (atr * 2),
            "TP": current_price + (atr * 4),
            "ADX": adx,
            "RSI": rsi
        }

    # SELL
    if bearish >= 45 and trend == "BEARISH":

        return {
            "Coin": symbol,
            "Signal": "🟥 SELL",
            "Score": bearish,
            "Price": current_price,
            "SL": current_price + (atr * 2),
            "TP": current_price - (atr * 4),
            "ADX": adx,
            "RSI": rsi
        }

    return None

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("⚙️ CONTROL PANEL")

    strategy = st.radio(
        "Trading Mode",
        [
            "Scalping",
            "Day Trading",
            "Swing"
        ]
    )

    if strategy == "Scalping":
        htf = "1h"
        ltf = "5m"

    elif strategy == "Day Trading":
        htf = "4h"
        ltf = "15m"

    else:
        htf = "1d"
        ltf = "1h"

    selected_coin = st.selectbox(
        "Select Coin",
        SCAN_COINS
    )

    balance = st.number_input(
        "Balance",
        value=1000.0
    )

    risk_percent = st.slider(
        "Risk %",
        1,
        5,
        1
    )

    leverage = st.slider(
        "Leverage",
        1,
        50,
        10
    )

# =========================================================
# HEADER
# =========================================================

st.title("👑 ALPHA TERMINAL v4.6")

st.caption(
    f"Mode: {strategy} | Binance Live Feed Active"
)

# =========================================================
# LIVE DATA CHECK
# =========================================================

btc_test = get_crypto_data("BTCUSDT", "5m", 5)

if btc_test is not None:
    st.success("🟢 Binance Live Data Connected Successfully")
else:
    st.error("🔴 Binance Connection Failed")

# =========================================================
# MARKET SCANNER
# =========================================================

st.subheader("📡 LIVE MARKET SCANNER")

signals = []

with concurrent.futures.ThreadPoolExecutor(
    max_workers=5
) as executor:

    results = executor.map(
        lambda coin: analyze_coin(
            coin,
            htf,
            ltf
        ),
        SCAN_COINS
    )

    for result in results:

        if result:
            signals.append(result)

        time.sleep(0.25)

if signals:

    df = pd.DataFrame(signals)

    st.dataframe(
        df,
        use_container_width=True
    )

else:

    st.warning(
        "⚠️ No active setups currently."
    )

# =========================================================
# SINGLE COIN ANALYSIS
# =========================================================

st.subheader(
    f"🎯 {selected_coin} ANALYSIS"
)

analysis = analyze_coin(
    selected_coin,
    htf,
    ltf
)

if analysis:

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "SIGNAL",
            analysis["Signal"]
        )

    with col2:
        st.metric(
            "SCORE",
            f'{analysis["Score"]}%'
        )

    with col3:
        st.metric(
            "ADX",
            f'{analysis["ADX"]:.2f}'
        )

    with col4:
        st.metric(
            "RSI",
            f'{analysis["RSI"]:.2f}'
        )

    st.success(
        f"""
ENTRY: {analysis["Price"]:.4f}

STOP LOSS: {analysis["SL"]:.4f}

TAKE PROFIT: {analysis["TP"]:.4f}
"""
    )

    # RISK
    risk_cash = balance * (
        risk_percent / 100
    )

    sl_distance = abs(
        analysis["Price"] -
        analysis["SL"]
    )

    if sl_distance > 0:

        position_size = risk_cash / (
            sl_distance /
            analysis["Price"]
        )

        margin = (
            position_size /
            leverage
        )

        st.warning(
            f"""
RISK AMOUNT: ${risk_cash:.2f}

POSITION SIZE: ${position_size:.2f}

MARGIN NEEDED: ${margin:.2f}
"""
        )

else:

    st.info(
        "⚪ No valid setup currently."
    )

# =========================================================
# TRADINGVIEW CHART
# =========================================================

st.subheader("📈 LIVE CHART")

tv_interval = (
    "5"
    if ltf == "5m"
    else "15"
    if ltf == "15m"
    else "60"
)

tv_html = f"""

<div id="tv_chart"></div>

<script
type="text/javascript"
src="https://s3.tradingview.com/tv.js">
</script>

<script type="text/javascript">

new TradingView.widget({{

    "width":"100%",
    "height":500,
    "symbol":"BINANCE:{selected_coin}",
    "interval":"{tv_interval}",
    "timezone":"Etc/UTC",
    "theme":"dark",
    "style":"1",
    "locale":"en",
    "toolbar_bg":"#111827",
    "enable_publishing":false,
    "allow_symbol_change":true,
    "container_id":"tv_chart"

}});

</script>
"""

components.html(tv_html, height=520)

# =========================================================
# FOOTER
# =========================================================

st.caption(
    f"Last Update: {datetime.datetime.utcnow()} UTC"
)

if __name__ == "__main__":
    pass
