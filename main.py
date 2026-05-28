# app.py

```python
import streamlit as st
import pandas as pd
import numpy as np
import requests

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="ALPHA TERMINAL",
    page_icon="🚀",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }

    h1,h2,h3 {
        color: #f0f2f6;
    }

    div[data-testid="stMetricValue"] {
        color: #00ff88;
        font-size: 28px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# SYMBOLS
# =========================
SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "DOGEUSDT"
]

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Settings")

selected_coin = st.sidebar.selectbox(
    "Select Coin",
    SYMBOLS
)

selected_tf = st.sidebar.selectbox(
    "Select Timeframe",
    ["5m", "15m", "1h", "4h"]
)

balance = st.sidebar.number_input(
    "Balance ($)",
    value=1000.0
)

risk_percent = st.sidebar.slider(
    "Risk %",
    1,
    10,
    2
)

# =========================
# FETCH DATA
# =========================
def get_data(symbol, interval, limit=200):
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    response = requests.get(url, params=params)
    data = response.json()

    columns = [
        "Time",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "CloseTime",
        "Q1",
        "Trades",
        "TB",
        "TQ",
        "Ignore"
    ]

    df = pd.DataFrame(data, columns=columns)

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = df[col].astype(float)

    return df

# =========================
# INDICATORS
# =========================
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def rsi(series, period=14):
    delta = series.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


def atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)

    true_range = ranges.max(axis=1)

    return true_range.rolling(period).mean()


def macd(series):
    ema12 = ema(series, 12)
    ema26 = ema(series, 26)

    macd_line = ema12 - ema26
    signal_line = ema(macd_line, 9)

    return macd_line, signal_line

# =========================
# SMC LOGIC
# =========================
def detect_bos(df):
    recent_high = df['High'].iloc[-6:-1].max()
    recent_low = df['Low'].iloc[-6:-1].min()

    if df['Close'].iloc[-1] > recent_high:
        return "Bullish BOS"

    if df['Close'].iloc[-1] < recent_low:
        return "Bearish BOS"

    return "No BOS"

# =========================
# ANALYZE MARKET
# =========================
def analyze(df):
    df['EMA50'] = ema(df['Close'], 50)
    df['RSI'] = rsi(df['Close'])

    macd_line, signal_line = macd(df['Close'])

    trend = "Bullish" if df['Close'].iloc[-1] > df['EMA50'].iloc[-1] else "Bearish"

    rsi_value = df['RSI'].iloc[-1]

    bos = detect_bos(df)

    score = 0

    if trend == "Bullish":
        score += 30

    if rsi_value > 50:
        score += 20

    if macd_line.iloc[-1] > signal_line.iloc[-1]:
        score += 20

    if bos == "Bullish BOS":
        score += 30

    signal = "NEUTRAL"

    if score >= 70:
        signal = "BUY"

    elif score <= 30:
        signal = "SELL"

    return {
        "trend": trend,
        "rsi": round(rsi_value, 2),
        "score": score,
        "signal": signal,
        "bos": bos
    }

# =========================
# MAIN TITLE
# =========================
st.title("👑 ALPHA CRYPTO TERMINAL")

st.write("Advanced Crypto Dashboard")

# =========================
# LOAD DATA
# =========================
df = get_data(selected_coin, selected_tf)

analysis = analyze(df)

# =========================
# METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Trend", analysis['trend'])

with col2:
    st.metric("RSI", analysis['rsi'])

with col3:
    st.metric("AI Score", f"{analysis['score']}%")

with col4:
    st.metric("Signal", analysis['signal'])

# =========================
# BOS INFO
# =========================
st.subheader("📈 Market Structure")

st.info(analysis['bos'])

# =========================
# PRICE CHART
# =========================
st.subheader("📊 Price Data")

chart_df = df[['Close']]

st.line_chart(chart_df)

# =========================
# RISK MANAGEMENT
# =========================
last_price = df['Close'].iloc[-1]

atr_value = atr(df).iloc[-1]

if pd.isna(atr_value):
    atr_value = last_price * 0.01

stop_loss = last_price - (atr_value * 2)

take_profit = last_price + (atr_value * 4)

risk_amount = balance * (risk_percent / 100)

position_size = risk_amount / abs(last_price - stop_loss)

st.subheader("💰 Risk Management")

risk_col1, risk_col2, risk_col3 = st.columns(3)

with risk_col1:
    st.metric("Entry", round(last_price, 2))

with risk_col2:
    st.metric("Stop Loss", round(stop_loss, 2))

with risk_col3:
    st.metric("Take Profit", round(take_profit, 2))

st.success(f"Recommended Position Size: ${round(position_size, 2)}")

# =========================
# RAW DATA
# =========================
st.subheader("📋 Live Market Data")

st.dataframe(df.tail(20), use_container_width=True)
```

---

# requirements.txt

```txt
streamlit
pandas
numpy
requests
```

---

# RUN COMMAND

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

# IMPORTANT

Only copy the code inside:

* app.py
* requirements.txt

Do NOT copy markdown headings or explanations into Python files.
