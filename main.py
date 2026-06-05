# =========================================================
# QUANTUM X TERMINAL - LIVE REAL-TIME AUTOMATIC SMC ENGINE
# =========================================================

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sqlite3
from datetime import datetime

# උඩින්ම streamlit-autorefresh එක import කරගැනීම
from streamlit_autorefresh import st_autorefresh

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="QUANTUM X TERMINAL",
    layout="wide"
)

# හැම තත්පර 5කට වරක්ම මුළු App එකම ඔටෝමැටිකලි අප්ඩේට් වෙන්න සෙට් කිරීම
count = st_autorefresh(interval=5000, limit=None, key="quantum_auto_refresh")

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
# ORIGINAL PREMIUM QUANTUM UI (CSS)
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

st.markdown('<div class="card"><div class="title">⚡ QUANTUM X TERMINAL</div><div>Smart Money Concepts & Institutional Auto-Update Engine</div></div>', unsafe_allow_html=True)

# =========================================================
# INDICATORS & ORIGINAL SMC ANALYSIS METHODS
# =========================================================
def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_ema(data, period):
    return data.ewm(span=period, adjust=False).mean()

def calculate_atr(df, period=14):
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return pd.Series(true_range).rolling(period).mean()

def detect_smc_features(df):
    highs = df["high"].values
    lows = df["low"].values
    closes = df["close"].values
    
    bos_bullish, bos_bearish = False, False
    fvg_bullish, fvg_bearish = False, False
    order_block_bullish, order_block_bearish = False, False
    
    # structural shifts
    for i in range(-15, -2):
        if closes[-1] > highs[i]: bos_bullish = True
        if closes[-1] < lows[i]: bos_bearish = True
        
    # FVG
    if highs[-3] < lows[-1]: fvg_bullish = True
    if lows[-3] > highs[-1]: fvg_bearish = True
        
    # Order Blocks
    if closes[-1] > closes[-2] and closes[-3] < closes[-4]: order_block_bullish = True
    if closes[-1] < closes[-2] and closes[-3] > closes[-4]: order_block_bearish = True
        
    return bos_bullish, bos_bearish, fvg_bullish, fvg_bearish, order_block_bullish, order_block_bearish

# =========================================================
# MULTI-NODE API DATA FETCHING (ANTI-FAIL / ANTI-BLOCK)
# =========================================================
@st.cache_data(ttl=3)
def get_market():
    endpoints = [
        "https://api.binance.com/api/v3/ticker/24hr",
        "https://fapi.binance.com/fapi/v1/ticker/24hr",
        "https://api1.binance.com/api/v3/ticker/24hr"
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for url in endpoints:
        try:
            response = requests.get(url, headers=headers, timeout=4)
            if response.status_code == 200:
                data = response.json()
                rows = []
                for coin in data:
                    symbol = str(coin.get("symbol", ""))
                    if symbol.endswith("USDT") and not "_" in symbol:
                        rows.append({
                            "symbol": symbol,
                            "price": float(coin.get("lastPrice", 0)),
                            "change": float(coin.get("priceChangePercent", 0)),
                            "volume": float(coin.get("quoteVolume", 0))
                        })
                if rows:
                    df = pd.DataFrame(rows)
                    return df.sort_values(by="volume", ascending=False).head(35)
        except:
            continue
            
    # CryptoCompare Fallback if Binance completely Blocks connection
    try:
        fallback_url = "https://min-api.cryptocompare.com/data/top/mktcapfull?limit=35&tsym=USDT"
        res = requests.get(fallback_url, timeout=4)
        if res.status_code == 200:
            data = res.json().get("Data", [])
            rows = []
            for coin in data:
                raw = coin.get("RAW", {}).get("USDT", {})
                info = coin.get("CoinInfo", {})
                symbol = f"{info.get('Name', '')}USDT"
                if raw:
                    rows.append({
                        "symbol": symbol,
                        "price": float(raw.get("PRICE", 0)),
                        "change": float(raw.get("CHANGEPCT24HOUR", 0)),
                        "volume": float(raw.get("VOLUME24HOURTO", 0))
                    })
            if rows:
                return pd.DataFrame(rows)
    except:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=3)
def get_klines(symbol, interval="15m"):
    endpoints = [
        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100",
        f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit=100"
    ]
    for url in endpoints:
        try:
            response = requests.get(url, timeout=4)
            if response.status_code == 200:
                data = response.json()
                frame = pd.DataFrame(data).iloc[:, :6]
                frame.columns = ["time", "open", "high", "low", "close", "volume"]
                frame["time"] = pd.to_datetime(frame["time"], unit='ms')
                for col in ["open", "high", "low", "close", "volume"]:
                    frame[col] = frame[col].astype(float)
                return frame
        except:
            continue
            
    # CryptoCompare Historical candles Fallback
    try:
        base_asset = symbol.replace("USDT", "")
        histo_type = "histohour" if "1h" in interval else "histominute"
        agg = 15 if "15m" in interval else 5 if "5m" in interval else 1
        url = f"https://min-api.cryptocompare.com/data/v2/{histo_type}?fsym={base_asset}&tsym=USDT&limit=100&aggregate={agg}"
        res = requests.get(url, timeout=4).json()
        data = res.get("Data", {}).get("Data", [])
        if data:
            frame = pd.DataFrame(data)
            frame = frame[['time', 'open', 'high', 'low', 'close', 'volumeto']]
            frame.columns = ["time", "open", "high", "low", "close", "volume"]
            frame["time"] = pd.to_datetime(frame["time"], unit='s')
            return frame
    except:
        pass
    return pd.DataFrame()

# =========================================================
# SIGNAL LOGISTICS
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
    except:
        pass

# Automation Tracker Loop
try:
    signals = pd.read_sql("SELECT * FROM signals WHERE status='RUNNING' ORDER BY id DESC LIMIT 15", conn)
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
st.subheader("📊 SYSTEM ACCURACY DASHBOARD")
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
    a.metric("TOTAL SIGNALS", total_signals)
    b.metric("RUNNING", running)
    c.metric("TP1 HITS", tp1_hits)
    d.metric("TP2 HITS", tp2_hits)
    e.metric("TP3 HITS", tp3_hits)
    f.metric("WIN RATE", f"{win_rate}%")

# =========================================================
# CONFIGURATION
# =========================================================
df = get_market()
if df.empty:
    st.error("🚨 Syncing institutional data nodes. Connection active but restricted. Standby.")
    st.stop()

trading_type = st.selectbox("🎯 SELECT TRADING TYPE", ["SCALPING", "DAY TRADING", "SWING TRADING"])
if trading_type == "SCALPING": timeframe = "5m"
elif trading_type == "DAY TRADING": timeframe = "15m"
else: timeframe = "1h"

# =========================================================
# SMC CORE ENGINE TERMINAL
# =========================================================
st.subheader(f"🔥 INSTITUTIONAL SMC SCANNER ({timeframe})")
scan_long, scan_short = [], []
coins = df["symbol"].tolist()

for coin in coins:
    try:
        kline = get_klines(coin, timeframe)
        if kline.empty or len(kline) < 30: continue

        close = kline["close"]
        current_price = close.iloc[-1]
        
        ema50 = calculate_ema(close, 50).iloc[-1]
        rsi = calculate_rsi(close).iloc[-1]
        atr = calculate_atr(kline).iloc[-1]
        if atr == 0 or np.isnan(atr): continue

        bos_bull, bos_bear, fvg_bull, fvg_bear, ob_bull, ob_bear = detect_smc_features(kline)

        long_score, short_score = 0, 0
        
        if current_price > ema50: long_score += 20
        if 40 < rsi < 70: long_score += 20
        if bos_bull: long_score += 20
        if fvg_bull: long_score += 20
        if ob_bull: long_score += 20
        
        if current_price < ema50: short_score += 20
        if 30 < rsi < 60: short_score += 20
        if bos_bear: short_score += 20
        if fvg_bear: short_score += 20
        if ob_bear: short_score += 20

        if long_score >= 60:
            sl = current_price - (atr * 1.5)
            scan_long.append({
                "COIN": coin, "PRICE": round(current_price, 4), "SMC SCORE": f"{long_score}%",
                "ENTRY": round(current_price, 4), "TP1": round(current_price + (atr * 1.5), 4),
                "TP2": round(current_price + (atr * 3.0), 4), "SL": round(sl, 4)
            })
            save_signal(coin, "LONG", timeframe, current_price, current_price + (atr * 1.5), current_price + (atr * 3.0), current_price + (atr * 4.5), sl, long_score)

        if short_score >= 60:
            sl = current_price + (atr * 1.5)
            scan_short.append({
                "COIN": coin, "PRICE": round(current_price, 4), "SMC SCORE": f"{short_score}%",
                "ENTRY": round(current_price, 4), "TP1": round(current_price - (atr * 1.5), 4),
                "TP2": round(current_price - (atr * 3.0), 4), "SL": round(sl, 4)
            })
            save_signal(coin, "SHORT", timeframe, current_price, current_price - (atr * 1.5), current_price - (atr * 3.0), current_price - (atr * 4.5), sl, short_score)
    except:
        pass

lcol, scol = st.columns(2)
with lcol:
    st.subheader("🚀 LONG SIGNALS (BULLISH SMC)")
    if scan_long: st.dataframe(pd.DataFrame(scan_long), use_container_width=True)
    else: st.info("Scanning Market for Order Blocks & BOS Long setups...")
with scol:
    st.subheader("🔴 SHORT SIGNALS (BEARISH SMC)")
    if scan_short: st.dataframe(pd.DataFrame(scan_short), use_container_width=True)
    else: st.info("Scanning Market for Order Blocks & BOS Short setups...")

# =========================================================
# DEEP INTERACTION PORTAL WITH CHART
# =========================================================
st.markdown("---")
st.subheader("🔍 COIN SPECIFIC SMC DEEP INTERACTION")

search_coin = st.text_input("Enter Coin Asset Name (e.g., BTC, ETH, SOL)", "BTC")
selected_coin = f"{search_coin.upper()}USDT"

kline = get_klines(selected_coin, timeframe)

if not kline.empty:
    close = kline["close"]
    current_price = close.iloc[-1]
    rsi_val = calculate_rsi(close).iloc[-1]
    atr_val = calculate_atr(kline).iloc[-1]
    ema50_val = calculate_ema(close, 50).iloc[-1]
    
    bos_bull, bos_bear, fvg_bull, fvg_bear, ob_bull, ob_bear = detect_smc_features(kline)
    
    long_score = sum([20 if current_price > ema50_val else 0, 20 if 40 < rsi_val < 70 else 0, 20 if bos_bull else 0, 20 if fvg_bull else 0, 20 if ob_bull else 0])
    short_score = sum([20 if current_price < ema50_val else 0, 20 if 30 < rsi_val < 60 else 0, 20 if bos_bear else 0, 20 if fvg_bear else 0, 20 if ob_bear else 0])
    
    css, status_txt = "neutral", "⚪ SMC MARKET STRUCTURE CONSOLIDATION"
    if long_score >= 60: css, status_txt = "buy", "🚀 SMC BULLISH EXPANSION DETECTED"
    elif short_score >= 60: css, status_txt = "sell", "🔴 SMC BEARISH EXPANSION DETECTED"
    
    st.markdown(f"""
    <div class="card">
        <h2 style='text-align: center; color:#38bdf8;'>{selected_coin} Advanced SMC Portal (Auto-Updating)</h2>
        <div class="{css}">{status_txt}</div><br>
        <table style='width:100%; text-align:center; font-size:16px;'>
            <tr>
                <th>REAL-TIME PRICE</th>
                <th>BOS DETECTED</th>
                <th>FVG PRESENT</th>
                <th>ORDER BLOCK ACTIVE</th>
            </tr>
            <tr>
                <td style='color:#38bdf8; font-weight:bold; font-size:20px;'>${current_price:,.4f}</td>
                <td>{"🟢 Bullish BOS" if bos_bull else "🔴 Bearish BOS" if bos_bear else "❌ No"}</td>
                <td>{"🟢 Bullish FVG" if fvg_bull else "🔴 Bearish FVG" if fvg_bear else "❌ No"}</td>
                <td>{"🟢 Bullish OB" if ob_bull else "🔴 Bearish OB" if ob_bear else "❌ No"}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=kline['time'], open=kline['open'], high=kline['high'],
        low=kline['low'], close=kline['close'], name="Market Price"
    ))
    
    kline['EMA50'] = calculate_ema(close, 50)
    fig.add_trace(go.Scatter(
        x=kline['time'], y=kline['EMA50'], 
        line=dict(color='#6366f1', width=2), name="EMA 50 Line"
    ))
    
    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=500,
        paper_bgcolor='rgba(15,23,42,0.55)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    t1, t2 = st.columns(2)
    with t1:
        st.success(f"🟢 INSTITUTIONAL LONG MATRIX\n\n"
                   f"🔹 entry point: {current_price:,.4f}\n\n"
                   f"🎯 target 1: {current_price+(atr_val*1.5):,.4f}\n"
                   f"🎯 target 2: {current_price+(atr_val*3.0):,.4f}\n\n"
                   f"🛑 stop trigger: {current_price-(atr_val*1.5):,.4f}")
    with t2:
        st.error(f"🔴 INSTITUTIONAL SHORT MATRIX\n\n"
                 f"🔹 entry point: {current_price:,.4f}\n\n"
                 f"🎯 target 1: {current_price-(atr_val*1.5):,.4f}\n"
                 f"🎯 target 2: {current_price-(atr_val*3.0):,.4f}\n\n"
                 f"🛑 stop trigger: {current_price+(atr_val*1.5):,.4f}")
else:
    st.warning("Please type a valid asset name or wait for data synchronization...")
