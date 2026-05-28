import numpy as np
import pandas as pd
import requests
import streamlit as st
import concurrent.futures
import streamlit.components.v1 as components
import datetime
import time

# 🔑 CRYPTOCOMPARE LIVE GLOBAL FEED API KEY
CRYPTOCOMPARE_API_KEY = "02cde33bf0c2982646ebb3aee6b63db7811ac11fae16a81a230d6c79f2cc6437"

# වෙබ් පිටුවේ සැකසුම් (Page Configuration)
st.set_page_config(
    page_title="ALPHA TRADING TERMINAL v4.5",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# 🎨 PREMIUM UI DESIGN
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
# 🛠️ DATA MODULES (CRYPTOCOMPARE COMPATIBLE)
# =====================================================================
COIN_SYMBOLS = {
    "BTCUSDT": "₿ BTCUSDT", "ETHUSDT": "♦️ ETHUSDT", "SOLUSDT": "☀️ SOLUSDT", "BNBUSDT": "🔶 BNBUSDT",
    "XRPUSDT": "💧 XRPUSDT", "ADAUSDT": "₳ ADAUSDT", "DOGEUSDT": "🐕 DOGEUSDT", "SHIBUSDT": "🦊 SHIBUSDT",
    "AVAXUSDT": "🔺 AVAXUSDT", "DOTUSDT": "● DOTUSDT", "LINKUSDT": "🔗 LINKUSDT", "MATICUSDT": "💜 MATICUSDT",
    "NEARUSDT": "Ⓝ NEARUSDT", "UNIUSDT": "🦄 UNIUSDT", "LTCUSDT": "Ł LTCUSDT", "APTUSDT": "🌀 APTUSDT",
    "SUIUSDT": "💧 SUIUSDT", "OPUSDT": "🔴 OPUSDT", "ARBUSDT": "🔵 ARBUSDT", "ATOMUSDT": "⚛️ ATOMUSDT",
    "PEPEUSDT": "🐸 PEPEUSDT", "FILUSDT": "📁 FILUSDT", "LDOUSDT": "💧 LDOUSDT", "ICPUSDT": "♾️ ICPUSDT",
    "VETUSDT": "📐 VETUSDT", "RNDRUSDT": "🎨 RNDRUSDT", "MKRUSDT": "Ⓜ️ MKRUSDT", "INJUSDT": "💉 INJUSDT",
    "RUNEUSDT": "⚡ RUNEUSDT", "GRTUSDT": "📊 GRTUSDT", "SEIUSDT": "🌊 SEIUSDT", "THETAUSDT": "📹 THETAUSDT",
    "IMXUSDT": "🎮 IMXUSDT", "FETUSDT": "🤖 FETUSDT", "AAVEUSDT": "👻 AAVEUSDT", "FTMUSDT": "👻 FTMUSDT",
    "GALAUSDT": "🎮 GALAUSDT", "EGLDUSDT": "⚡ EGLDUSDT", "AXSUSDT": "👾 AXSUSDT", "SANDUSDT": "⏳ SANDUSDT",
    "MANAUSDT": "🏛️ MANAUSDT", "CHZUSDT": "⚽ CHZUSDT", "EOSUSDT": "🪙 EOSUSDT", "IOTAUSDT": "🤖 IOTAUSDT",
    "NEOUSDT": "💚 NEOUSDT", "CRVUSDT": "🪙 CRVUSDT", "ALGOUSDT": "₳ ALGOUSDT", "XLMUSDT": "🚀 XLMUSDT",
    "TRXUSDT": "🔴 TRXUSDT", "WIFUSDT": "👒 WIFUSDT", "FLOKIUSDT": "🐕 FLOKIUSDT", "BONKUSDT": "🐕 BONKUSDT",
    "TIAUSDT": "🌌 TIAUSDT", "DYDXUSDT": "📊 DYDXUSDT", "ENSUSDT": "🌐 ENSUSDT", "WOOUSDT": "🪙 WOOUSDT",
    "GMTUSDT": "👟 GMTUSDT", "JUPUSDT": "🪐 JUPUSDT", "PYTHUSDT": "🔮 PYTHUSDT", "ZETAUSDT": "🪙 ZETAUSDT",
    "MANTAUSDT": "🪙 MANTAUSDT", "STRKUSDT": "🪙 STRKUSDT", "PENDLEUSDT": "🪙 PENDLEUSDT", "AGIXUSDT": "🧠 AGIXUSDT",
    "OCEANUSDT": "🌊 OCEANUSDT", "XMRUSDT": "🔒 XMRUSDT", "ZECUSDT": "🔒 ZECUSDT", "DASHUSDT": "🪙 DASHUSDT",
    "WAVESUSDT": "🌊 WAVESUSDT", "1INCHUSDT": "🦄 1INCHUSDT", "ANKRUSDT": "⚓ ANKRUSDT", "BATUSDT": "🦁 BATUSDT",
    "CELOUSDT": "🪙 CELOUSDT", "COMPUSDT": "🪙 COMPUSDT", "ENJUSDT": "🎮 ENJUSDT", "KAVAUSDT": "🪙 KAVAUSDT",
    "KSMUSDT": "🐦 KSMUSDT", "LRCUSDT": "🪙 LRCUSDT", "ONEUSDT": "🪙 ONEUSDT", "QTUMUSDT": "🪙 QTUMUSDT",
    "RVNUSDT": "🦅 RVNUSDT", "SNXUSDT": "🪙 SNXUSDT", "SUSHIUSDT": "🍣 SUSHIUSDT", "YFIUSDT": "🪙 YFIUSDT",
    "ZILUSDT": "🪙 ZILUSDT", "JTOUSDT": "🪙 JTOUSDT", "ORDIUSDT": "🪙 ORDIUSDT", "SATSUSDT": "🪙 SATSUSDT",
    "MEMEUSDT": "🪙 MEMEUSDT", "BLURUSDT": "🪙 BLURUSDT", "ILVUSDT": "🪙 ILVUSDT", "SUPERUSDT": "🪙 SUPERUSDT",
    "RAREUSDT": "🪙 RAREUSDT", "AUDIOUSDT": "🎵 AUDIOUSDT", "HBARUSDT": "🪙 HBARUSDT", "ZENUSDT": "🪙 ZENUSDT",
    "BCHUSDT": "₿ BCHUSDT", "ETCUSDT": "🪙 ETCUSDT"
}
SCAN_COINS = list(COIN_SYMBOLS.keys())

def get_all_binance_symbols_with_symbols():
    return COIN_SYMBOLS

def get_crypto_data(symbol, interval, limit=100):
    coin = symbol.replace("USDT", "")
    
    # Default value එකක් දාමු, එතකොට NameError එන්නේ නැහැ
    agg = 1 
    
    if interval in ["1m", "5m", "15m"]:
        url = "https://min-api.cryptocompare.com/data/v2/histominute"
        agg = 1 if interval == "1m" else 5 if interval == "5m" else 15
    elif interval in ["1h", "4h"]:
        url = "https://min-api.cryptocompare.com/data/v2/histohour"
        agg = 1 if interval == "1h" else 4
    else:
        url = "https://min-api.cryptocompare.com/data/v2/histoday"
        agg = 1

    headers = {"Authorization": f"Apikey {CRYPTOCOMPARE_API_KEY}"}
    params = {"fsym": coin, "tsym": "USDT", "limit": limit, "aggregate": agg}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            res_json = response.json()
            raw_list = res_json.get("Data", {}).get("Data", [])
            if not raw_list: 
                return None
            
            df = pd.DataFrame(raw_list)
            df = df.rename(columns={"time": "Time", "open": "Open", "high": "High", "low": "Low", "close": "Close", "volumeto": "Volume"})
            
            for col in ["Open", "High", "Low", "Close", "Volume"]:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
            return df
    except Exception as e:
        return None
    return None

# =====================================================================
# 🧠 ADVANCED QUANT MATH & HIGH ACCURACY SMC ENGINE
# =====================================================================
def calculate_rsi(series, period=14):
    if len(series) < period: return pd.Series(50, index=series.index)
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    return 100 - (100 / (1 + (gain / (loss + 1e-10))))

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def calculate_macd(series, fast=12, slow=26, signal=9):
    macd_line = calculate_ema(series, fast) - calculate_ema(series, slow)
    return macd_line, calculate_ema(macd_line, signal)

def calculate_atr(df, period=14):
    if len(df) < period: return pd.Series(df["Close"] * 0.003)
    tr = pd.concat([df["High"] - df["Low"], abs(df["High"] - df["Close"].shift()), abs(df["Low"] - df["Close"].shift())], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def calculate_cvd_delta(df):
    if df is None or df.empty or len(df) < 5: return 0
    typical_price_change = df['Close'] - df['Open']
    high_low_spread = df['High'] - df['Low'] + 1e-10
    buyer_volume = df['Volume'] * (0.5 + (typical_price_change / (2 * high_low_spread)))
    seller_volume = df['Volume'] - buyer_volume
    cvd = (buyer_volume - seller_volume).iloc[-5:].sum()
    return cvd

def is_news_block_active():
    now = datetime.datetime.utcnow()
    if now.weekday() in [2, 3] and now.hour in [13, 14]: 
        return True
    return False

def detect_smc_features(df):
    if df is None or len(df) < 15: return 0, 0, "NONE"
    
    bos_signal = "NONE"
    if df['Close'].iloc[-1] > df['High'].shift(1).iloc[-6:-1].max():
        bos_signal = "BULLISH_BOS"
    elif df['Close'].iloc[-1] < df['Low'].shift(1).iloc[-6:-1].min():
        bos_signal = "BEARISH_BOS"
        
    bullish_ob = 1 if (df['Close'].iloc[-2] < df['Open'].iloc[-2]) and (df['Close'].iloc[-1] > df['High'].iloc[-2]) and (df['Volume'].iloc[-1] > df['Volume'].rolling(20).mean().fillna(0).iloc[-1] * 1.3) else 0
    bearish_ob = 1 if (df['Close'].iloc[-2] > df['Open'].iloc[-2]) and (df['Close'].iloc[-1] < df['Low'].iloc[-2]) and (df['Volume'].iloc[-1] > df['Volume'].rolling(20).mean().fillna(0).iloc[-1] * 1.3) else 0
    
    fvg_bullish = 1 if (df['Low'].iloc[-1] > df['High'].iloc[-3]) and (df['Close'].iloc[-2] > df['Open'].iloc[-2]) else 0
    fvg_bearish = 1 if (df['High'].iloc[-1] < df['Low'].iloc[-3]) and (df['Close'].iloc[-2] < df['Open'].iloc[-2]) else 0
    
    liq_sweep_bullish = 1 if (df['Low'].iloc[-1] < df['Low'].shift(1).rolling(10).min().fillna(0).iloc[-2]) and (df['Close'].iloc[-1] > df['Open'].iloc[-1]) else 0
    liq_sweep_bearish = 1 if (df['High'].iloc[-1] > df['High'].shift(1).rolling(10).max().fillna(0).iloc[-2]) and (df['Close'].iloc[-1] < df['Open'].iloc[-1]) else 0

    bull_points = (bullish_ob * 15) + (fvg_bullish * 15) + (liq_sweep_bullish * 10) + (15 if bos_signal == "BULLISH_BOS" else 0)
    bear_points = (bearish_ob * 15) + (fvg_bearish * 15) + (liq_sweep_bearish * 10) + (15 if bos_signal == "BEARISH_BOS" else 0)
    
    return bull_points, bear_points, bos_signal

def send_telegram_alert(token, chat_id, message):
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try: requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        except: pass

def analyze_coin_for_scanner(coin, htf, ltf):
    df_htf = get_crypto_data(coin, htf, 100)
    df_ltf = get_crypto_data(coin, ltf, 100)
    
    if df_htf is None or df_ltf is None or len(df_htf) < 50 or len(df_ltf) < 50: 
        return None
    
    if is_news_block_active(): return None

    bullish_points, bearish_points, total_checks = 0, 0, 0
    df_htf["EMA_50"] = calculate_ema(df_htf["Close"], 50)
    
    htf_trend = "BULLISH" if df_htf["Close"].iloc[-1] > df_htf["EMA_50"].iloc[-1] else "BEARISH"
    bullish_points += 15 if htf_trend == "BULLISH" else 0
    bearish_points += 15 if htf_trend == "BEARISH" else 0
    total_checks += 15
    
    df_ltf["RSI"] = calculate_rsi(df_ltf["Close"], 14)
    c_rsi = df_ltf["RSI"].iloc[-1]
    if c_rsi < 35: bullish_points += 15
    elif c_rsi > 65: bearish_points += 15
    total_checks += 15
    
    df_ltf["MACD"], df_ltf["Signal"] = calculate_macd(df_ltf["Close"])
    if df_ltf["MACD"].iloc[-1] > df_ltf["Signal"].iloc[-1]: bullish_points += 10
    else: bearish_points += 10
    total_checks += 10
    
    smc_bull, smc_bear, bos_sig = detect_smc_features(df_ltf)
    if htf_trend == "BULLISH" and bos_sig == "BULLISH_BOS": bullish_points += 20
    if htf_trend == "BEARISH" and bos_sig == "BEARISH_BOS": bearish_points += 20
    
    bullish_points += smc_bull
    bearish_points += smc_bear
    total_checks += 75 
    
    cvd_flow = calculate_cvd_delta(df_ltf)
    if cvd_flow > 0: bullish_points += 15
    elif cvd_flow < 0: bearish_points += 15
    total_checks += 15

    bull_per = (bullish_points / total_checks) * 100
    bear_per = (bearish_points / total_checks) * 100
    c_price = df_ltf["Close"].iloc[-1]
    df_ltf["ATR"] = calculate_atr(df_ltf)
    c_atr = df_ltf["ATR"].iloc[-1] if not pd.isna(df_ltf["ATR"].iloc[-1]) else (c_price * 0.003)
    dec = 6 if c_price < 0.1 else 4
    
    coin_display = COIN_SYMBOLS.get(coin, f"🪙 {coin}")
    
    if bull_per >= 60 and htf_trend == "BULLISH" and cvd_flow > 0:
        return {"Coin": coin_display, "Signal": "🟩 BUY / LONG", "Strength": f"{bull_per:.1f}%", "Structure": bos_sig, "Entry": f"{c_price:.{dec}f}", "SL": f"{c_price - (c_atr*2):.{dec}f}", "TP": f"{c_price + (c_atr*4):.{dec}f}"}
    elif bear_per >= 60 and htf_trend == "BEARISH" and cvd_flow < 0:
        return {"Coin": coin_display, "Signal": "🟥 SELL / SHORT", "Strength": f"{bear_per:.1f}%", "Structure": bos_sig, "Entry": f"{c_price:.{dec}f}", "SL": f"{c_price + (c_atr*2):.{dec}f}", "TP": f"{c_price - (c_atr*4):.{dec}f}"}
    return None

# =====================================================================
# ⚙️ SIDEBAR MANAGEMENT CONTROL PANEL
# =====================================================================
all_symbols_dict = get_all_binance_symbols_with_symbols()

with st.sidebar:
    st.markdown("### 👑 TERMINAL CONTROL PANEL")
    
    st.markdown("#### ⏱️ STRATEGY TIMEFRAME")
    strategy = st.radio("Select Trading Profile:", ["⚡ Scalping (1H + 5M)", "📈 Day Trading (4H + 15M)", "🐋 Swing Trading (1D + 1H)"], index=1)
    htf, ltf = ("1h", "5m") if "Scalping" in strategy else ("4h", "15m") if "Day Trading" in strategy else ("1d", "1h")
    
    st.markdown("---")
    
    selected_coin_display = st.selectbox("🎯 DEEP ANALYSIS COIN:", options=list(all_symbols_dict.values()), index=list(all_symbols_dict.keys()).index("BTCUSDT") if "BTCUSDT" in all_symbols_dict else 0)
    selected_coin = [k for k, v in all_symbols_dict.items() if v == selected_coin_display][0]
    
    st.markdown("---")
    
    st.markdown("#### 💰 RISK CALCULATOR")
    balance = st.number_input("Account Balance ($):", min_value=10.0, value=1000.0, step=50.0)
    risk_pct = st.slider("Risk Per Trade (%):", min_value=0.5, max_value=5.0, value=1.0, step=0.5)
    leverage = st.slider("Target Leverage (x):", min_value=1, max_value=50, value=10)
    
    st.markdown("---")
    
    st.markdown("#### 🔔 TELEGRAM NOTIFIER")
    tg_on = st.checkbox("Enable Live Alerts")
    tg_token = st.text_input("Bot Token:", type="password")
    tg_id = st.text_input("Chat ID:")

# =====================================================================
# 👑 MAIN INTERFACE
# =====================================================================
st.markdown("<h1 style='text-align: center; color: #ffb703;'>👑 ALPHA AUTOMATED QUANT TERMINAL v4.5</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #8b949e;'>Engine Mode: <b>{strategy}</b> | Live CryptoCompare Global Feed Stream</p>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'/>", unsafe_allow_html=True)

if is_news_block_active():
    st.warning("⚠️ HIGH IMPACT ECONOMIC NEWS WINDOW OPEN: Signals are locked to prevent false breakout traps.")

# 📡 LIVE SCANNER RADAR RUNNING IN BACKGROUND
st.markdown("### 📡 MARKET RADAR MULTI-CONFLUENCE SIGNALS")
active_signals = []
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor: 
    results = executor.map(lambda c: analyze_coin_for_scanner(c, htf, ltf), SCAN_COINS)
    for r in list(results):
        if r is not None: 
            active_signals.append(r)
            if tg_on and tg_token and tg_id:
                msg = f"⚠️ *ALPHA TERMINAL MASTER v4.5*\n\n🪙 Coin: {r['Coin']}\n🚨 Action: {r['Signal']}\n💪 Strength: {r['Strength']}\n🏛️ Structure: {r['Structure']}\n\n💵 Entry: {r['Entry']}\n🛑 SL: {r['SL']}\n🎯 TP: {r['TP']}"
                send_telegram_alert(tg_token, tg_id, msg)

if active_signals:
    st.dataframe(pd.DataFrame(active_signals), use_container_width=True, hide_index=True)
else:
    st.warning("🔍 Scanner Standby: No asset currently breaks the 60% Multi-Timeframe Confluence Threshold. Maintain patience.")

st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'/>", unsafe_allow_html=True)

# 📊 TRADINGVIEW LIVE CHARTS EMBEDDING & DEEP VISUALIZER
st.markdown(f"### 🎯 LIVE ANALYSIS & CHART VIEW: <span style='color: #58a6ff;'>{selected_coin_display}</span>", unsafe_allow_html=True)

col_chart, col_metrics = st.columns([2, 1])

with col_chart:
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

# Deep Visualizer Calculations with Fallover Protection
df_htf = get_crypto_data(selected_coin, htf, 100)
df_ltf = get_crypto_data(selected_coin, ltf, 100)
df_1m = get_crypto_data(selected_coin, "1m", 5)

data_isValid = (df_htf is not None and df_ltf is not None and df_1m is not None and 
                len(df_htf) >= 20 and len(df_ltf) >= 20 and len(df_1m) >= 1)

with col_metrics:
    if data_isValid:
        try:
            bullish_points, bearish_points, total_checks = 0, 0, 0
            
            current_market_price = df_1m["Close"].iloc[-1]
            st.metric("📊 LIVE MARKET PRICE", f"${current_market_price:,.2f}")
            
            df_htf["EMA_50"] = calculate_ema(df_htf["Close"], 50)
            htf_trend = "BULLISH 📈" if df_htf["Close"].iloc[-1] > df_htf["EMA_50"].iloc[-1] else "BEARISH 📉"
            if htf_trend == "BULLISH 📈": bullish_points += 15
            else: bearish_points += 15
            total_checks += 15
            
            df_ltf["RSI"] = calculate_rsi(df_ltf["Close"], 14)
            c_rsi = df_ltf["RSI"].iloc[-1]
            if c_rsi < 35: bullish_points += 15
            elif c_rsi > 65: bearish_points += 15
            total_checks += 15
            
            df_ltf["MACD"], df_ltf["Signal"] = calculate_macd(df_ltf["Close"])
            if df_ltf["MACD"].iloc[-1] > df_ltf["Signal"].iloc[-1]: bullish_points += 10
            else: bearish_points += 10
            total_checks += 10
            
            smc_bull, smc_bear, bos_sig = detect_smc_features(df_ltf)
            if htf_trend == "BULLISH 📈" and bos_sig == "BULLISH_BOS": bullish_points += 20
            if htf_trend == "BEARISH 📉" and bos_sig == "BEARISH_BOS": bearish_points += 20
            
            bullish_points += smc_bull
            bearish_points += smc_bear
            total_checks += 75
            
            cvd_flow = calculate_cvd_delta(df_ltf)
            if cvd_flow > 0: bullish_points += 15
            elif cvd_flow < 0: bearish_points += 15
            total_checks += 15
            
            bull_per = (bullish_points / total_checks) * 100
            bear_per = (bearish_points / total_checks) * 100
            
            st.metric(label="🟩 ACCURATE BUY PROBABILITY", value=f"{bull_per:.1f}%")
            st.metric(label="🟥 ACCURATE SELL PROBABILITY", value=f"{bear_per:.1f}%")
            st.info(f"HTF Trend Setup: **{htf_trend}**\nCVD Flow: **{'BULLISH 🟢' if cvd_flow > 0 else 'BEARISH 🔴'}**")
        except:
            data_isValid = False
    
    if not data_isValid:
        st.error("🔄 Connecting to Live Feed Stream... Ensure API Key is correct.")
        bull_per, bear_per, htf_trend, cvd_flow = 0, 0, "NONE", 0

# Execution & Risk Size Output
if data_isValid:
    try:
        c_price_1m = df_1m["Close"].iloc[-1]
        df_ltf["ATR"] = calculate_atr(df_ltf)
        c_atr = df_ltf["ATR"].iloc[-1] if not pd.isna(df_ltf["ATR"].iloc[-1]) else (c_price_1m * 0.003)
        dec_places = 6 if c_price_1m < 0.1 else 4
        
        risk_cash = balance * (risk_pct / 100)
        sl_distance_pct = (c_atr * 2) / c_price_1m
        raw_position_size = risk_cash / sl_distance_pct if sl_distance_pct > 0 else balance
        margin_required = raw_position_size / leverage
        
        trailing_sl_step = c_atr * 1.5
        
        st.markdown("#### ⚡ SIGNAL SYSTEM EXECUTION & RISK SHEET")
        
        col_sig, col_risk = st.columns(2)
        
        with col_sig:
            if bull_per >= 60 and htf_trend == "BULLISH 📈" and cvd_flow > 0:
                buy_msg = f"### 🚀 SYSTEM DIRECTIVE: BUY / LONG\n\n**Entry:** ${c_price_1m:.{dec_places}f}\n\n**Stop Loss:** ${c_price_1m - (c_atr*2):.{dec_places}f}\n\n**Take Profit:** ${c_price_1m + (c_atr*4):.{dec_places}f}\n\n*🛡️ Trailing SL Step:* Move SL up every +${trailing_sl_step:.{dec_places}f} profit."
                st.success(buy_msg)
            elif bear_per >= 60 and htf_trend == "BEARISH 📉" and cvd_flow < 0:
                sell_msg = f"### 📉 SYSTEM DIRECTIVE: SELL / SHORT\n\n**Entry:** ${c_price_1m:.{dec_places}f}\n\n**Stop Loss:** ${c_price_1m + (c_atr*2):.{dec_places}f}\n\n**Take Profit:** ${c_price_1m - (c_atr*4):.{dec_places}f}\n\n*🛡️ Trailing SL Step:* Move SL down every -${trailing_sl_step:.{dec_places}f} profit."
                st.error(sell_msg)
            else:
                st.info("⚪ ENGINE STATUS: High-accuracy confluence threshold not met. Standby.")
                
        with col_risk:
            risk_msg = f"### 🧮 CALCULATED RISK QUANTITIES\n\n* **Risk Cash Amount:** ${risk_cash:.2f}\n\n* **Recommended Position Size:** ${raw_position_size:.2f}\n\n* **Margin Allocation Needed:** ${margin_required:.2f} (at {leverage}x)"
            st.warning(risk_msg)
    except:
        pass
