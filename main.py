# =========================================================
# QUANTUM X TERMINAL - GRAND FINAL (REAL-TIME LIVE FIX)
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
# DATABASE SETUP
# =========================================================
conn = sqlite3.connect("signals.db", check_same_thread=False)
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
# ULTRA PREMIUM QUANTUM UI (CSS)
# =========================================================
st.markdown("""
<style>
html, body, .stApp {
    background: linear-gradient(135deg, rgba(2,6,23,0.96), rgba(15,23,42,0.96), rgba(17,24,39,0.97)),
        url("https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-attachment: fixed;
    color: white;
    font-family: Arial;
}
.card {
    background: rgba(15,23,42,0.55);
    backdrop-filter: blur(20px);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:28px;
    padding:24px;
    margin-bottom:24px;
    box-shadow: 0 0 30px rgba(56,189,248,0.08);
}
.title {
    font-size:58px;
    font-weight:900;
    background:linear-gradient(90deg, #38bdf8, #818cf8, #22c55e, #38bdf8);
    background-size:300%;
    animation: titleFlow 8s linear infinite;
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
@keyframes titleFlow { 0%{background-position:0%;} 100%{background-position:300%;} }
.buy { background: linear-gradient(90deg, rgba(34,197,94,0.75), rgba(22,163,74,0.92)); padding:14px; border-radius:16px; font-size:20px; font-weight:bold; text-align:center; }
.sell { background: linear-gradient(90deg, rgba(239,68,68,0.75), rgba(127,29,29,0.95)); padding:14px; border-radius:16px; font-size:20px; font-weight:bold; text-align:center; }
.neutral { background: linear-gradient(90deg, rgba(148, 163, 184, 0.5), rgba(71, 85, 105, 0.7)); padding:14px; border-radius:16px; font-size:20px; font-weight:bold; text-align:center; }
[data-testid="metric-container"] { background: rgba(15,23,42,0.72); backdrop-filter: blur(16px); border-radius:22px; border:1px solid rgba(255,255,255,0.06); padding:18px; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="card"><div class="title">⚡ QUANTUM X TERMINAL</div><div>Institutional Multi-Confluence Trading Engine</div></div>', unsafe_allow_html=True)

# =========================================================
# TECHNICAL INDICATORS
# =========================================================
def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_ema(data, period):
    return data.ewm(span=period, adjust=False).mean()

def calculate_macd(data):
    ema12 = calculate_ema(data, 12)
    ema26 = calculate_ema(data, 26)
    macd = ema12 - ema26
    signal = calculate_ema(macd, 9)
    return macd, signal

def calculate_atr(df, period=14):
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return pd.Series(true_range).rolling(period).mean()

# =========================================================
# REAL-TIME MARKET DATA FETCHING (NO MORE FAKE PRICES)
# =========================================================
# Cache එක තත්පර 5කට අඩු කරා එවෙලේම live price එක ගන්න
@st.cache_data(ttl=5)
def get_market():
    # 100% Real-time prices එන Binance API endpoints
    urls = [
        "https://fapi.binance.com/fapi/v1/ticker/24hr",  # Futures API (Highly Recommended for Trading)
        "https://api.binance.com/api/v3/ticker/24hr"
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                rows = []
                for coin in data:
                    symbol = str(coin.get("symbol", ""))
                    # USDT pairs පමණක් පෙරා ගැනීම (e.g., BTCUSDT)
                    if symbol.endswith("USDT") and not "_" in symbol:
                        rows.append({
                            "symbol": symbol,
                            "price": float(coin.get("lastPrice", 0)),
                            "change": float(coin.get("priceChangePercent", 0)),
                            "volume": float(coin.get("quoteVolume", 0))
                        })
                if rows:
                    df = pd.DataFrame(rows)
                    return df.sort_values(by="volume", ascending=False).head(40) # Top 40 coins for speed optimization
        except Exception as e:
            continue
            
    st.error("⚠️ Binance API Connection Failed! Please refresh page.")
    return pd.DataFrame()

@st.cache_data(ttl=5)
def get_klines(symbol, interval="15m"):
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit=100"
        response = requests.get(url, timeout=10)
        data = response.json()
        frame = pd.DataFrame(data).iloc[:, :6]
        frame.columns = ["time", "open", "high", "low", "close", "volume"]
        for col in ["open", "high", "low", "close", "volume"]:
            frame[col] = frame[col].astype(float)
        return frame
    except:
        return pd.DataFrame()

# =========================================================
# SIGNAL MANAGEMENT
# =========================================================
def save_signal(coin, signal, timeframe, entry, tp1, tp2, tp3, sl, probability):
    try:
        existing = pd.read_sql(f"SELECT * FROM signals WHERE coin='{coin}' AND signal='{signal}' AND timeframe='{timeframe}' AND status='RUNNING'", conn)
        if existing.empty:
            cursor.execute("""
            INSERT INTO signals (coin, signal, timeframe, entry, tp1, tp2, tp3, sl, probability, status, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (coin, signal, timeframe, entry, tp1, tp2, tp3, sl, probability, "RUNNING", str(datetime.now())))
            conn.commit()
    except Exception as e:
        pass

# Real-time Track old signals
try:
    signals = pd.read_sql("SELECT * FROM signals WHERE status='RUNNING' ORDER BY id DESC LIMIT 20", conn)
    for _, row in signals.iterrows():
        coin, signal_type, signal_id, timeframe_sig = row["coin"], row["signal"], row["id"], row["timeframe"]
        tp1, tp2, tp3, sl_val = row["tp1"], row["tp2"], row["tp3"], row["sl"]
        
        kline = get_klines(coin, timeframe_sig)
        if not kline.empty:
            current_price = kline["close"].iloc[-1]
            if signal_type == "LONG":
                if current_price >= tp3: cursor.execute("UPDATE signals SET status='TP3 HIT' WHERE id=?", (signal_id,))
                elif current_price >= tp2: cursor.execute("UPDATE signals SET status='TP2 HIT' WHERE id=?", (signal_id,))
                elif current_price >= tp1: cursor.execute("UPDATE signals SET status='TP1 HIT' WHERE id=?", (signal_id,))
                elif current_price <= sl_val: cursor.execute("UPDATE signals SET status='SL HIT' WHERE id=?", (signal_id,))
            else:
                if current_price <= tp3: cursor.execute("UPDATE signals SET status='TP3 HIT' WHERE id=?", (signal_id,))
                elif current_price <= tp2: cursor.execute("UPDATE signals SET status='TP2 HIT' WHERE id=?", (signal_id,))
                elif current_price <= tp1: cursor.execute("UPDATE signals SET status='TP1 HIT' WHERE id=?", (signal_id,))
                elif current_price >= sl_val: cursor.execute("UPDATE signals SET status='SL HIT' WHERE id=?", (signal_id,))
            conn.commit()
except:
    pass

# =========================================================
# ACCURACY DASHBOARD
# =========================================================
st.subheader("📊 ACCURACY DASHBOARD")
signals_df = pd.read_sql("SELECT * FROM signals", conn)

if not signals_df.empty:
    total_signals = len(signals_df)
    tp1_hits = len(signals_df[signals_df["status"] == "TP1 HIT"])
    tp2_hits = len(signals_df[signals_df["status"] == "TP2 HIT"])
    tp3_hits = len(signals_df[signals_df["status"] == "TP3 HIT"])
    sl_hits = len(signals_df[signals_df["status"] == "SL HIT"])
    running = len(signals_df[signals_df["status"] == "RUNNING"])
    win_rate = round(((tp1_hits+tp2_hits+tp3_hits) / total_signals) * 100, 2) if total_signals > 0 else 0

    a, b, c, d, e, f = st.columns(6)
    a.metric("TOTAL", total_signals)
    b.metric("RUNNING", running)
    c.metric("TP1 HITS", tp1_hits)
    d.metric("TP2 HITS", tp2_hits)
    e.metric("TP3 HITS", tp3_hits)
    f.metric("WIN RATE", f"{win_rate}%")

# =========================================================
# TRADING CONFIGURATION
# =========================================================
df = get_market()
if df.empty:
    st.stop()

trading_type = st.selectbox("🎯 SELECT TRADING TYPE", ["SCALPING", "DAY TRADING", "SWING TRADING"])
if trading_type == "SCALPING": timeframe = "5m"
elif trading_type == "DAY TRADING": timeframe = "15m"
else: timeframe = "1h"

# =========================================================
# HIGH ACCURACY ALGORITHMIC SCANNER (CONFLUENCE METHOD)
# =========================================================
st.subheader(f"🔥 ELITE PRO SCANNER ({timeframe} - {trading_type})")
scan_long, scan_short = [], []
coins = df["symbol"].tolist()

for coin in coins:
    try:
        kline = get_klines(coin, timeframe)
        if kline.empty or len(kline) < 50: continue

        close = kline["close"]
        current_price = close.iloc[-1]
        
        # 1. Trend Filter (EMA Confluence)
        ema50 = calculate_ema(close, 50).iloc[-1]
        ema200 = calculate_ema(close, 200).iloc[-1]
        
        # 2. Momentum Filter (RSI & MACD)
        rsi = calculate_rsi(close).iloc[-1]
        macd, macd_sig = calculate_macd(close)
        macd_val = macd.iloc[-1]
        macd_sig_val = macd_sig.iloc[-1]
        
        # 3. Volatility (ATR) for Risk Management
        atr = calculate_atr(kline).iloc[-1]
        if atr == 0 or np.isnan(atr): continue

        # --- Professional Score System ---
        long_score, short_score = 0, 0
        
        # Bullish Scoring
        if current_price > ema50: long_score += 30
        if ema50 > ema200: long_score += 20
        if rsi > 45 and rsi < 65: long_score += 25  # Healthy momentum
        if macd_val > macd_sig_val: long_score += 25
        
        # Bearish Scoring
        if current_price < ema50: short_score += 30
        if ema50 < ema200: short_score += 20
        if rsi < 55 and rsi > 35: short_score += 25
        if macd_val < macd_sig_val: short_score += 25

        # Signal Generation (75% Threshold for stable entries)
        if long_score >= 75:
            sl = current_price - (atr * 1.5)
            tp1 = current_price + (atr * 1.5)
            tp2 = current_price + (atr * 3.0)
            tp3 = current_price + (atr * 4.5)
            
            scan_long.append({
                "COIN": coin, "PRICE": round(current_price, 4), "ACCURACY": f"{long_score}%",
                "ENTRY": round(current_price, 4), "TP1": round(tp1, 4), "TP2": round(tp2, 4), "TP3": round(tp3, 4), "SL": round(sl, 4)
            })
            save_signal(coin, "LONG", timeframe, current_price, tp1, tp2, tp3, sl, long_score)

        if short_score >= 75:
            sl = current_price + (atr * 1.5)
            tp1 = current_price - (atr * 1.5)
            tp2 = current_price - (atr * 3.0)
            tp3 = current_price - (atr * 4.5)
            
            scan_short.append({
                "COIN": coin, "PRICE": round(current_price, 4), "ACCURACY": f"{short_score}%",
                "ENTRY": round(current_price, 4), "TP1": round(tp1, 4), "TP2": round(tp2, 4), "TP3": round(tp3, 4), "SL": round(sl, 4)
            })
            save_signal(coin, "SHORT", timeframe, current_price, tp1, tp2, tp3, sl, short_score)
    except:
        pass

# Display Tables
lcol, scol = st.columns(2)
with lcol:
    st.subheader("🚀 LONG SIGNALS")
    if scan_long: st.dataframe(pd.DataFrame(scan_long), use_container_width=True)
    else: st.warning("Scanning Market for Institutional Long Setups...")

with scol:
    st.subheader("🔴 SHORT SIGNALS")
    if scan_short: st.dataframe(pd.DataFrame(scan_short), use_container_width=True)
    else: st.warning("Scanning Market for Institutional Short Setups...")

# =========================================================
# INDIVIDUAL COIN DEEP ANALYSIS
# =========================================================
st.markdown("---")
st.subheader("🔍 COIN DEEP ANALYSIS FILTER")
search_coin = st.text_input("Type Coin Symbol (e.g., BTC, ETH, SOL)", "BTC")
coin_to_analyze = f"{search_coin.upper()}USDT"

if coin_to_analyze in df["symbol"].tolist():
    kline = get_klines(coin_to_analyze, timeframe)
    if not kline.empty:
        close = kline["close"]
        current_price = close.iloc[-1]
        rsi = calculate_rsi(close).iloc[-1]
        atr = calculate_atr(kline).iloc[-1]
        
        # Confluence Signals
        ema50 = calculate_ema(close, 50).iloc[-1]
        macd, macd_sig = calculate_macd(close)
        
        long_score = sum([30 if current_price > ema50 else 0, 35 if rsi < 40 else 20, 35 if macd.iloc[-1] > macd_sig.iloc[-1] else 0])
        short_score = 100 - long_score
        
        css, status_txt = "neutral", "⚪ NEUTRAL MARKET"
        if long_score >= 70: css, status_txt = "buy", "🚀 STRONG LONG OPPORTUNITY"
        elif short_score >= 70: css, status_txt = "sell", "🔴 STRONG SHORT OPPORTUNITY"
        
        st.markdown(f"""
        <div class="card">
            <h2 style='text-align: center;'>{coin_to_analyze} Live Analysis</h2>
            <div class="{css}">{status_txt}</div><br>
            <table style='width:100%; text-align:center; font-size:18px;'>
                <tr>
                    <th>LIVE PRICE</th>
                    <th>LONG SCORE</th>
                    <th>SHORT SCORE</th>
                    <th>RSI</th>
                </tr>
                <tr>
                    <td style='color:#38bdf8; font-weight:bold;'>${current_price:,.4f}</td>
                    <td style='color:#22c55e;'>{long_score}%</td>
                    <td style='color:#ef4444;'>{short_score}%</td>
                    <td>{rsi:.2f}</td>
                </tr>
            </table>
            <hr>
            <h4 style='color:#22c55e;'>🎯 IF LONG SETUP:</h4>
            <p>Entry: {current_price:,.4f} | TP1: {current_price+(atr*1.5):,.4f} | TP2: {current_price+(atr*3):,.4f} | SL: {current_price-(atr*1.5):,.4f}</p>
            <h4 style='color:#ef4444;'>🎯 IF SHORT SETUP:</h4>
            <p>Entry: {current_price:,.4f} | TP1: {current_price-(atr*1.5):,.4f} | TP2: {current_price-(atr*3):,.4f} | SL: {current_price+(atr*1.5):,.4f}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.error("Coin not found or active in Top Volume list. Check the symbol again.")
