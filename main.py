import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ALPHA TERMINAL",
    page_icon="👑",
    layout="wide"
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

h1,h2,h3{
    color:white !important;
}

[data-testid="stMetricValue"]{
    color:#ffb703;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# COINS
# =========================================================

COIN_SYMBOLS = {
    "BTCUSDT": "₿ BTCUSDT",
    "ETHUSDT": "♦️ ETHUSDT",
    "SOLUSDT": "☀️ SOLUSDT",
    "BNBUSDT": "🔶 BNBUSDT",
    "XRPUSDT": "💧 XRPUSDT"
}

SCAN_COINS = list(COIN_SYMBOLS.keys())

# =========================================================
# API
# =========================================================

@st.cache_data(ttl=30)
def get_crypto_data(symbol, interval, limit=100):

    url = "https://data-api.binance.vision/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
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

        for col in ["Open", "High", "Low", "Close", "Volume"]:
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

    rsi = 100 - (100 / (1 + rs))

    return rsi

def calculate_macd(series):

    ema12 = calculate_ema(series, 12)
    ema26 = calculate_ema(series, 26)

    macd = ema12 - ema26
    signal = calculate_ema(macd, 9)

    return macd, signal

def calculate_atr(df, period=14):

    high_low = df["High"] - df["Low"]

    high_close = np.abs(df["High"] - df["Close"].shift())

    low_close = np.abs(df["Low"] - df["Close"].shift())

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

    if df_htf is None or df_ltf is None:
        return None

    if len(df_htf) < 50 or len(df_ltf) < 50:
        return None

    # EMA
    df_htf["EMA50"] = calculate_ema(df_htf["Close"], 50)

    trend = (
        "BULLISH"
        if df_htf["Close"].iloc[-1] >
        df_htf["EMA50"].iloc[-1]
        else "BEARISH"
    )

    # RSI
    df_ltf["RSI"] = calculate_rsi(df_ltf["Close"])

    rsi = df_ltf["RSI"].iloc[-1]

    # MACD
    macd, signal = calculate_macd(df_ltf["Close"])

    df_ltf["MACD"] = macd
    df_ltf["SIGNAL"] = signal

    # ATR
    df_ltf["ATR"] = calculate_atr(df_ltf)

    atr = df_ltf["ATR"].iloc[-1]

    # ADX
    df_ltf["ADX"] = calculate_adx(df_ltf)

    adx = df_ltf["ADX"].iloc[-1]

    # Volume
    avg_volume = df_ltf["Volume"].rolling(20).mean()

    volume_ok = (
        df_ltf["Volume"].iloc[-1] >
        avg_volume.iloc[-1]
    )

    bullish = 0
    bearish = 0

    # Trend
    if trend == "BULLISH":
        bullish += 20
    else:
        bearish += 20

    # RSI
    if rsi < 35:
        bullish += 15

    if rsi > 65:
        bearish += 15

    # MACD
    if macd.iloc[-1] > signal.iloc[-1]:
        bullish += 20
    else:
        bearish += 20

    # ADX
    if adx > 20:
        bullish += 10
        bearish += 10

    # Volume
    if volume_ok:
        bullish += 10
        bearish += 10

    bull_score = bullish
    bear_score = bearish

    current_price = df_ltf["Close"].iloc[-1]

    if np.isnan(atr):
        atr = current_price * 0.003

    # BUY
    if bull_score >= 60 and trend == "BULLISH":

        return {
            "Coin": symbol,
            "Signal": "BUY",
            "Score": bull_score,
            "Price": current_price,
            "SL": current_price - (atr * 2),
            "TP": current_price + (atr * 4),
            "ADX": adx
        }

    # SELL
    if bear_score >= 60 and trend == "BEARISH":

        return {
            "Coin": symbol,
            "Signal": "SELL",
            "Score": bear_score,
            "Price": current_price,
            "SL": current_price + (atr * 2),
            "TP": current_price - (atr * 4),
            "ADX": adx
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

st.title("👑 ALPHA QUANT TERMINAL")

st.caption(
    f"Mode: {strategy} | Binance Live Data"
)

# =========================================================
# SCANNER
# =========================================================

st.subheader("📡 LIVE MARKET SCANNER")

signals = []

for coin in SCAN_COINS:

    result = analyze_coin(
        coin,
        htf,
        ltf
    )

    if result:
        signals.append(result)

if signals:

    signals_df = pd.DataFrame(signals)

    st.dataframe(
        signals_df,
        use_container_width=True
    )

else:

    st.warning(
        "No high probability setups detected."
    )

# =========================================================
# SINGLE COIN ANALYSIS
# =========================================================

st.subheader(f"🎯 {selected_coin} ANALYSIS")

analysis = analyze_coin(
    selected_coin,
    htf,
    ltf
)

if analysis:

    col1, col2, col3 = st.columns(3)

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

    st.success(
        f"""
Entry: {analysis["Price"]:.4f}

Stop Loss: {analysis["SL"]:.4f}

Take Profit: {analysis["TP"]:.4f}
"""
    )

    # Risk Calculation
    risk_cash = balance * (
        risk_percent / 100
    )

    sl_distance = abs(
        analysis["Price"] - analysis["SL"]
    )

    if sl_distance > 0:

        position_size = risk_cash / (
            sl_distance / analysis["Price"]
        )

        margin = position_size / leverage

        st.warning(
            f"""
Risk Amount: ${risk_cash:.2f}

Position Size: ${position_size:.2f}

Margin Needed: ${margin:.2f}
"""
        )

else:

    st.info(
        "No valid setup currently."
    )

# =========================================================
# FOOTER
# =========================================================

st.caption(
    f"Last Update: {datetime.datetime.utcnow()} UTC"
)

if __name__ == "__main__":
    pass
