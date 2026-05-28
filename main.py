import numpy as np
import pandas as pd
import requests
import streamlit as st
import concurrent.futures
import streamlit.components.v1 as components

# වෙබ් පිටුවේ සැකසුම් (Page Configuration)
st.set_page_config(
    page_title="ALPHA TRADING TERMINAL v2.0",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# 🎨 PREMIUM UI DESIGN (ULTIMATE CRYPTO TERMINAL VIBE)
# =====================================================================
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(13, 17, 23, 0.90), rgba(13, 17, 23, 0.97)), 
                          url('https://images.unsplash.com/photo-1642790106117-e829e14a795f?q=80&w=1920');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .main { color: #ffffff; }
    h1, h2, h3, h4 { color: #f0f2f5 !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    div[data-testid="stMetricValue"] { font-size: 30px !important; font-weight: bold !important; font-family: 'monospace'; color: #ffb703 !important; }
    .stAlert { border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
    .dataframe { border: 1px solid #30363d !important; background-color: rgba(22, 27, 34, 0.8) !important; color: #ffffff !important; }
    div[data-testid="stSidebar"] { background-color: rgba(13, 17, 23, 0.96) !important; border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================================
# 🛠️ DATA MODULES & COIN SYMBOLS
# =====================================================================
COIN_SYMBOLS = {
    "BTCUSDT": "₿ BTCUSDT", "ETHUSDT": "♦️ ETHUSDT", "SOLUSDT": "☀️ SOLUSDT", "BNBUSDT": "🔶 BNBUSDT",
    "XRPUSDT": "💧 XRPUSDT", "ADAUSDT": "₳ ADAUSDT", "DOGEUSDT": "🐕 DOGEUSDT", "SHIBUSDT": "🦊 SHIBUSDT",
    "PEPEUSDT": "🐸 PEPEUSDT", "DOTUSDT": "● DOTUSDT", "LTCUSDT": "Ł LTCUSDT", "AVAXUSDT": "🔺 AVAXUSDT",
    "LINKUSDT": "🔗 LINKUSDT", "TRXUSDT": "🔴 TRXUSDT", "ATOMUSDT": "⚛️ ATOMUSDT", "UNIUSDT": "🦄 UNIUSDT",
    "NEARUSDT": "Ⓝ NEARUSDT", "SUIUSDT": "💧 SUIUSDT", "FETUSDT": "🤖 FETUSDT", "APTUSDT": "🌀 APTUSDT"
}
SCAN_COINS = list(COIN_SYMBOLS.keys())

def get_all_binance_symbols_with_symbols():
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        response = requests.get(url)
        data = response.json()
        all_pairs = [s["symbol"] for s in data["symbols"] if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"]
        display_dict = {}
        for p in sorted(all_pairs):
            display_dict[p] = COIN_SYMBOLS[p] if p in COIN_SYMBOLS else f"🪙 {p}"
        return display_dict
    except:
        return COIN_SYMBOLS

def get_crypto_data(symbol, interval, limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        response = requests.get(url, params=params)
        raw_data = response.json()
        df = pd.DataFrame(raw_data, columns=["Time", "Open", "High", "Low", "Close", "Volume", "CloseTime", "QA", "Trades", "TBA", "TAQ", "Ignore"])
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = df[col].astype(float)
        return df
    except:
        return None

# Math Core
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    return 100 - (100 / (100 + (gain / loss)))

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def calculate_macd(series, fast=12, slow=26, signal=9):
    macd_line = calculate_ema(series, fast) - calculate_ema(series, slow)
    return macd_line, calculate_ema(macd_line, signal)

def calculate_atr(df, period=14):
    tr = pd.concat([df["High"] - df["Low"], abs(df["High"] - df["Close"].shift()), abs(df["Low"] - df["Close"].shift())], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

# Telegram Alert Function
def send_telegram_alert(token, chat_id, message):
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try: requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        except: pass

# Dynamic Scanning Logic
def analyze_coin_for_scanner(coin, htf, ltf):
    df_htf = get_crypto_data(coin, htf, 100)
    df_ltf = get_crypto_data(coin, ltf, 100)
    if df_htf is None or df_ltf is None or len(df_htf) < 50 or len(df_ltf) < 50: return None
    
    bullish_points, bearish_points, total_checks = 0, 0, 0
    df_htf["EMA_50"] = calculate_ema(df_htf["Close"], 50)
    df_htf["EMA_200"] = calculate_ema(df_htf["Close"], 200)
    
    htf_trend = "BULLISH" if df_htf["Close"].iloc[-1] > df_htf["EMA_50"].iloc[-1] else "BEARISH"
    bullish_points += 10 if htf_trend == "BULLISH" else 0
    bearish_points += 10 if htf_trend == "BEARISH" else 0
    total_checks += 10
    
    df_ltf["RSI"] = calculate_rsi(df_ltf["Close"], 14)
    c_rsi = df_ltf["RSI"].iloc[-1]
    if c_rsi < 35: bullish_points += 15
    elif c_rsi > 65: bearish_points += 15
    total_checks += 15
    
    df_ltf["MACD"], df_ltf["Signal"] = calculate_macd(df_ltf["Close"])
    if df_ltf["MACD"].iloc[-1] > df_ltf["Signal"].iloc[-1]: bullish_points += 10
    else: bearish_points += 10
    total_checks += 10
    
    c_last, c_prev = df_ltf.iloc[-2], df_ltf.iloc[-3]
    if c_last["Close"] > c_prev["Open"] and c_prev["Close"] < c_prev["Open"]: bullish_points += 15
    elif c_last["Close"] < c_prev["Open"] and c_prev["Close"] > c_prev["Open"]: bearish_points += 15
    total_checks += 15
    
    bull_per = (bullish_points / total_checks) * 100
    bear_per = (bearish_points / total_checks) * 100
    c_price = df_ltf["Close"].iloc[-1]
    df_ltf["ATR"] = calculate_atr(df_ltf)
    c_atr = df_ltf["ATR"].iloc[-1] if not pd.isna(df_ltf["ATR"].iloc[-1]) else (c_price * 0.003)
    dec = 6 if c_price < 0.1 else 4
    
    coin_display = COIN_SYMBOLS.get(coin, f"🪙 {coin}")
    if bull_per >= 55 and htf_trend == "BULLISH":
        return {"Coin": coin_display, "Signal": "🟩 BUY / LONG", "Strength": f"{bull_per:.1f}%", "Entry": f"${c_price:.{dec}f}", "SL": f"${c_price - (c_atr*2):.{dec}f}", "TP": f"${c_price + (c_atr*4):.{dec}f}"}
    elif bear_per >= 55 and htf_trend == "BEARISH":
        return {"Coin": coin_display, "Signal": "🟥 SELL / SHORT", "Strength": f"{bear_per:.1f}%", "Entry": f"${c_price:.{dec}f}", "SL": f"${c_price + (c_atr*2):.{dec}f}", "TP": f"${c_price - (c_atr*4):.{dec}f}"}
    return None

# =====================================================================
# ⚙️ SIDEBAR MANAGEMENT CONTROL PANEL
# =====================================================================
all_symbols_dict = get_all_binance_symbols_with_symbols()

with st.sidebar:
    st.markdown("### 👑 TERMINAL CONTROL PANEL")
    
    # ⏱️ 1. Multi-Timeframe Strategy Selector
    st.markdown("#### ⏱️ STRATEGY TIMEFRAME")
    strategy = st.radio("Select Trading Profile:", ["⚡ Scalping (1H + 5M)", "📈 Day Trading (4H + 15M)", "🐋 Swing Trading (1D + 1H)"], index=1)
    htf, ltf = ("1h", "5m") if "Scalping" in strategy else ("4h", "15m") if "Day Trading" in strategy else ("1d", "1h")
    
    st.markdown("---")
    
    # 🎯 2. Coin Selector
    selected_coin_display = st.selectbox("🎯 DEEP ANALYSIS COIN:", options=list(all_symbols_dict.values()), index=list(all_symbols_dict.keys()).index("BTCUSDT") if "BTCUSDT" in all_symbols_dict else 0)
    selected_coin = [k for k, v in all_symbols_dict.items() if v == selected_coin_display][0]
    
    st.markdown("---")
    
    # 💰 3. Risk & Position Calculator Widget
    st.markdown("#### 💰 RISK CALCULATOR")
    balance = st.number_input("Account Balance ($):", min_value=10.0, value=1000.0, step=50.0)
    risk_pct = st.slider("Risk Per Trade (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
    leverage = st.slider("Target Leverage (x):", min_value=1, max_value=50, value=10)
    
    st.markdown("---")
    
    # 🔔 4. Telegram Alerts Settings
    st.markdown("#### 🔔 TELEGRAM NOTIFIER")
    tg_on = st.checkbox("Enable Live Alerts")
    tg_token = st.text_input("Bot Token:", type="password")
    tg_id = st.text_input("Chat ID:")

# =====================================================================
# 👑 MAIN INTERFACE
# =====================================================================
st.markdown("<h1 style='text-align: center; color: #ffb703;'>👑 ALPHA AUTOMATED QUANT TERMINAL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #8b949e;'>Engine Mode: <b>{strategy}</b> | Live Confluence Scanner</p>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'/>", unsafe_allow_html=True)

# 📡 LIVE SCANNER RADAR RUNNING IN BACKGROUND
st.markdown("### 📡 MARKET RADAR ACTIVE SIGNALS")
active_signals = []
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(lambda c: analyze_coin_for_scanner(c, htf, ltf), SCAN_COINS)
    for r in list(results):
        if r is not None: 
            active_signals.append(r)
            if tg_on and tg_token and tg_id:
                msg = f"⚠️ *ALPHA TERMINAL SIGNAL*\n\n🪙 Coin: {r['Coin']}\n🚨 Action: {r['Signal']}\n💪 Strength: {r['Strength']}\n\n💵 Entry: {r['Entry']}\n🛑 SL: {r['SL']}\n🎯 TP: {r['TP']}"
                send_telegram_alert(tg_token, tg_id, msg)

if active_signals:
    st.dataframe(pd.DataFrame(active_signals), use_container_width=True, hide_index=True)
else:
    st.warning("🔍 Scanner Standby: No asset currently breaks the 55% statistical advantage threshold. Maintain patience.")

st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'/>", unsafe_allow_html=True)

# 📊 TRADINGVIEW LIVE CHARTS EMBEDDING & DEEP VISUALIZER
st.markdown(f"### 🎯 LIVE ANALYSIS & CHART VIEW: <span style='color: #58a6ff;'>{selected_coin_display}</span>", unsafe_allow_html=True)

col_chart, col_metrics = st.columns([2, 1])

with col_chart:
    # TradingView Live Widget Injection
    tv_interval = "5" if ltf == "5m" else "15" if ltf == "15m" else "60"
    tv_html = f"""
    <div id="tradingview_chart" style="height:450px;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({{
      "width": "100%",
      "height": 450,
      "symbol": "BINANCE:{selected_coin}",
      "interval": "{tv_interval}",
      "timezone": "Etc/UTC",
      "theme": "dark",
      "style": "1",
      "locale": "en",
      "toolbar_bg": "#f1f3f6",
      "enable_publishing": false,
      "hide_side_toolbar": false,
      "allow_symbol_change": true,
      "container_id": "tradingview_chart"
    }});
    </script>
    """
    components.html(tv_html, height=460)

# Deep Visualizer Calculations
df_htf = get_crypto_data(selected_coin, htf, 100)
df_ltf = get_crypto_data(selected_coin, ltf, 100)
df_1m = get_crypto_data(selected_coin, "1m", 5)

with col_metrics:
    if df_htf is not None and df_ltf is not None and df_1m is not None:
        bullish_points, bearish_points, total_checks = 0, 0, 0
        
        df_htf["EMA_50"] = calculate_ema(df_htf["Close"], 50)
        htf_trend = "BULLISH 📈" if df_htf["Close"].iloc[-1] > df_htf["EMA_50"].iloc[-1] else "BEARISH 📉"
        if htf_trend == "BULLISH 📈": bullish_points += 10
        else: bearish_points += 10
        total_checks += 10
        
        df_ltf["RSI"] = calculate_rsi(df_ltf["Close"], 14)
        c_rsi = df_ltf["RSI"].iloc[-1]
        if c_rsi < 35: bullish_points += 15
        elif c_rsi > 65: bearish_points += 15
        total_checks += 15
        
        df_ltf["MACD"], df_ltf["Signal"] = calculate_macd(df_ltf["Close"])
        if df_ltf["MACD"].iloc[-1] > df_ltf["Signal"].iloc[-1]: bullish_points += 10
        else: bearish_points += 10
        total_checks += 10
        
        bull_per = (bullish_points / total_checks) * 100
        bear_per = (bearish_points / total_checks) * 100
        
        st.metric(label="🟩 BUY PROBABILITY", value=f"{bull_per:.1f}%")
        st.metric(label="🟥 SELL PROBABILITY", value=f"{bear_per:.1f}%")
        st.info(f"HTF Trend Setup: **{htf_trend}**")
    else:
        st.error("Exchange data mapping failure.")

# Execution & Risk Size Output
if df_htf is not None and df_ltf is not None and df_1m is not None:
    c_price_1m = df_1m["Close"].iloc[-1]
    df_ltf["ATR"] = calculate_atr(df_ltf)
    c_atr = df_ltf["ATR"].iloc[-1] if not pd.isna(df_ltf["ATR"].iloc[-1]) else (c_price_1m * 0.003)
    dec_places = 6 if c_price_1m < 0.1 else 4
    
    # Risk Calc Formula Math
    risk_cash = balance * (risk_pct / 100)
    sl_distance_pct = (c_atr * 2) / c_price_1m
    raw_position_size = risk_cash / sl_distance_pct if sl_distance_pct > 0 else balance
    margin_required = raw_position_size / leverage
    
    st.markdown("#### ⚡ SIGNAL SYSTEM EXECUTION & RISK SHEET")
    
    col_sig, col_risk = st.columns(2)
    
    with col_sig:
        if bull_per >= 55 and htf_trend == "BULLISH 📈":
            st.success(f"### 🚀 SYSTEM DIRECTIVE: BUY / LONG\n**Entry:** ${c_price_1m:.{dec_places}f}\n**Stop Loss:** ${c_price_1m - (c_atr*2):.{dec_places}f}\n**Take Profit:** ${c_price_1m + (c_atr*4):.{dec_places}f}")
        elif bear_per >= 55 and htf_trend == "BEARISH 📉":
            st.error(f"### 📉 SYSTEM DIRECTIVE: SELL / SHORT\n**Entry:** ${c_price_1m:.{dec_places}f}\n**Stop Loss:** ${c_price_1m + (c_atr*2):.{dec_places}f}\n**Take Profit:** ${c_price_1m - (c_atr*4):.{dec_places}f}")
        else:
            st.info("⚪ ENGINE STATUS: Setup conditions inside the noise range. Safe Zone: No Trades.")
            
    with col_risk:
        st.warning(f"### 🧮 CALCULATED RISK QUANTITIES\n"
                   f"* **Risk Cash Amount:** ${risk_cash:.2f}\n"
                   f"* **Recommended Position Size:** ${raw_position_size:.2f}\n"
                   f"* **Margin Allocation Needed:** ${margin_required:.2f} (at {leverage}x)")
