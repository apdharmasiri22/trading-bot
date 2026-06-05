# =========================================================
# QUANTUM X TERMINAL - ULTIMATE LIVE TRACKING & ACCURACY ENGINE
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

.stTabs [data-baseweb="tab-list"] { gap: 12px; }
.stTabs [data-baseweb="tab"] {
    background: rgba(15,23,42,0.4) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    padding: 12px 28px !important;
    color: #94a3b8 !important;
    border-radius: 14px 14px 0px 0px !important;
    font-weight: bold !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(56,189,248,0.15) !important;
    border-color: #38bdf8 !important;
    color: #38bdf8 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="card"><div class="title">⚡ QUANTUM X TERMINAL</div><div>Institutional Smart Money Concepts Terminal Engine</div></div>', unsafe_allow_html=True)

# =========================================================
# INDICATORS & SMC ANALYSIS METHODS
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
    
    for i in range(-15, -2):
        if closes[-1] > highs[i]: bos_bullish = True
        if closes[-1] < lows[i]: bos_bearish = True
        
    if highs[-3] < lows[-1]: fvg_bullish = True
    if lows[-3] > highs[-1]: fvg_bearish = True
        
    if closes[-1] > closes[-2] and closes[-3] < closes[-4]: order_block_bullish = True
    if closes[-1] < closes[-2] and closes[-3] > closes[-4]: order_block_bearish = True
        
    return bos_bullish, bos_bearish, fvg_bullish, fvg_bearish, order_block_bullish, order_block_bearish

# =========================================================
# ULTRA STABLE LIVE APIS DATA NODES (BYPASSES BINANCE BLOCKS)
# =========================================================
@st.cache_data(ttl=2)
def get_market():
    # Priority 1: CryptoCompare API (No restrictions in Sri Lanka, highly stable)
    try:
        url = "https://min-api.cryptocompare.com/data/top/mktcapfull?limit=30&tsym=USDT"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            data = res.json().get("Data", [])
            rows = []
            for coin in data:
                raw = coin.get("RAW", {}).get("USDT", {})
                info = coin.get("CoinInfo", {})
                symbol = f"{info.get('Name', '')}USDT"
                if raw and info.get('Name'):
                    rows.append({
                        "symbol": symbol,
                        "price": float(raw.get("PRICE", 0)),
                        "change": float(raw.get("CHANGEPCT24HOUR", 0)),
                        "volume": float(raw.get("VOLUME24HOURTO", 0))
                    })
            if rows:
                return pd.DataFrame(rows)
    except: pass

    # Priority 2: Fallback to Binance Futures Endpoints if CryptoCompare fails
    endpoints = [
        "https://fapi.binance.com/fapi/v1/ticker/24hr",
        "https://api.binance.com/api/v3/ticker/24hr"
    ]
    for url in endpoints:
        try:
            response = requests.get(url, timeout=3)
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
                    return df.sort_values(by="volume", ascending=False).head(30)
        except: continue
    return pd.DataFrame()

@st.cache_data(ttl=2)
def get_klines(symbol, interval="15m"):
    base_asset = symbol.replace("USDT", "")
    
    # Priority 1: CryptoCompare Historical Aggregator Node
    try:
        histo_type = "histohour" if "1h" in interval else "histominute"
        agg = 15 if "15m" in interval else 5 if "5m" in interval else 1
        url = f"https://min-api.cryptocompare.com/data/v2/{histo_type}?fsym={base_asset}&tsym=USDT&limit=100&aggregate={agg}"
        res = requests.get(url, timeout=3).json()
        data = res.get("Data", {}).get("Data", [])
        if data:
            frame = pd.DataFrame(data)
            frame = frame[['time', 'open', 'high', 'low', 'close', 'volumeto']]
            frame.columns = ["time", "open", "high", "low", "close", "volume"]
            frame["time"] = pd.to_datetime(frame["time"], unit='s')
            for col in ["open", "high", "low", "close", "volume"]:
                frame[col] = frame[col].astype(float)
            return frame
    except: pass
            
    # Priority 2: Fallback to Binance Nodes
    endpoints = [
        f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit=100",
        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
    ]
    for url in endpoints:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                frame = pd.DataFrame(data).iloc[:, :6]
                frame.columns = ["time", "open", "high", "low", "close", "volume"]
                frame["time"] = pd.to_datetime(frame["time"], unit='ms')
                for col in ["open", "high", "low", "close", "volume"]:
                    frame[col] = frame[col].astype(float)
                return frame
        except: continue
    return pd.DataFrame()

# =========================================================
# SIGNAL MANAGEMENT & LIVE ACCURACY TRACKING
# =========================================================
def save_signal(coin, signal, timeframe, entry, tp1, tp2, tp3, sl, probability):
    try:
        existing = pd.read_sql(f"SELECT * FROM signals WHERE coin='{coin}' AND signal='{signal}' AND timeframe='{timeframe}' AND status='RUNNING'", conn)
        if existing.empty:
            cursor.execute("""
            INSERT INTO signals (coin, signal, timeframe, entry, tp1, tp2, tp3, sl, probability, status, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (coin, signal, timeframe, entry, tp1, tp2, tp3, sl, probability, "RUNNING", datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
    except: pass

def update_live_signals_status(market_df):
    try:
        running_signals = pd.read_sql("SELECT * FROM signals WHERE status='RUNNING'", conn)
        if running_signals.empty: return

        for _, row in running_signals.iterrows():
            sig_id = row['id']
            coin = row['coin']
            direction = row['signal']
            
            match = market_df[market_df['symbol'] == coin]
            if match.empty: continue
            current_price = float(match.iloc[0]['price'])

            new_status = "RUNNING"
            if direction == "LONG":
                if current_price >= row['tp3']: new_status = "TP3 HIT"
                elif current_price >= row['tp2']: new_status = "TP2 HIT"
                elif current_price >= row['tp1']: new_status = "TP1 HIT"
                elif current_price <= row['sl']: new_status = "SL HIT"
            else: # SHORT
                if current_price <= row['tp3']: new_status = "TP3 HIT"
                elif current_price <= row['tp2']: new_status = "TP2 HIT"
                elif current_price <= row['tp1']: new_status = "TP1 HIT"
                elif current_price >= row['sl']: new_status = "SL HIT"

            if new_status != "RUNNING":
                cursor.execute("UPDATE signals SET status=? WHERE id=?", (new_status, sig_id))
                conn.commit()
    except: pass

def render_accuracy_dashboard(tf_val):
    df_sig = pd.read_sql(f"SELECT * FROM signals WHERE timeframe='{tf_val}'", conn)
    
    total = len(df_sig)
    tp1 = len(df_sig[df_sig['status'] == "TP1 HIT"])
    tp2 = len(df_sig[df_sig['status'] == "TP2 HIT"])
    tp3 = len(df_sig[df_sig['status'] == "TP3 HIT"])
    sl = len(df_sig[df_sig['status'] == "SL HIT"])
    running = len(df_sig[df_sig['status'] == "RUNNING"])
    
    total_hits = tp1 + tp2 + tp3
    win_rate = round((total_hits / (total_hits + sl)) * 100, 1) if (total_hits + sl) > 0 else 0.0

    a, b, c, d, e = st.columns(5)
    a.metric("TOTAL SCANNED", total)
    b.metric("🔥 LIVE RUNNING", running, delta_color="off")
    c.metric("🟢 TARGETS HIT (TP)", total_hits)
    d.metric("🔴 LOSSES (SL)", sl)
    e.metric("🎯 WIN RATE", f"{win_rate}%")

# Fetch Global Market Data
df_market = get_market()
if df_market.empty:
    st.error("🚨 Cloud Data Synchronization Offline. Retrying network nodes...")
    st.stop()

# Update running signals based on latest prices
update_live_signals_status(df_market)

# =========================================================
# ⚡ CORE TABS CHANNELS
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 SCALPING MODE (5m)", 
    "⚡ DAY TRADING MODE (15m)", 
    "🔮 SWING TRADING MODE (1h)",
    "📜 ALL SIGNALS HISTORY"
])

# ---------------------------------------------------------
# TAB 1: SCALPING MODE (5m)
# ---------------------------------------------------------
with tab1:
    st.markdown("### 📊 INDEPENDENT ACCURACY DASHBOARD (5m)")
    render_accuracy_dashboard("5m")
    
    @st.fragment(run_every=30)
    def run_5m_scanner(market_df):
        st.subheader("🔥 REAL-TIME 5m SMC SCANNER (Auto-Updates)")
        scan_long, scan_short = [], []
        for coin in market_df["symbol"].tolist()[:20]: # Restricted to top 20 for extreme speed
            try:
                kline = get_klines(coin, "5m")
                if kline.empty or len(kline) < 30: continue
                close = kline["close"]
                current_price = close.iloc[-1]
                ema50 = calculate_ema(close, 50).iloc[-1]
                rsi = calculate_rsi(close).iloc[-1]
                atr = calculate_atr(kline).iloc[-1]
                if atr == 0 or np.isnan(atr): continue

                bos_bull, bos_bear, fvg_bull, fvg_bear, ob_bull, ob_bear = detect_smc_features(kline)
                long_score = sum([20 if current_price > ema50 else 0, 20 if 40 < rsi < 70 else 0, 20 if bos_bull else 0, 20 if fvg_bull else 0, 20 if ob_bull else 0])
                short_score = sum([20 if current_price < ema50 else 0, 20 if 30 < rsi < 60 else 0, 20 if bos_bear else 0, 20 if fvg_bear else 0, 20 if ob_bear else 0])

                if long_score >= 60:
                    sl = current_price - (atr * 1.5)
                    scan_long.append({"COIN": coin, "PRICE": f"${current_price:,.4f}", "SMC SCORE": f"{long_score}%", "ENTRY": round(current_price, 4), "TP1": round(current_price + (atr * 1.5), 4), "SL": round(sl, 4)})
                    save_signal(coin, "LONG", "5m", current_price, current_price + (atr * 1.5), current_price + (atr * 3.0), current_price + (atr * 4.5), sl, long_score)
                if short_score >= 60:
                    sl = current_price + (atr * 1.5)
                    scan_short.append({"COIN": coin, "PRICE": f"${current_price:,.4f}", "SMC SCORE": f"{short_score}%", "ENTRY": round(current_price, 4), "TP1": round(current_price - (atr * 1.5), 4), "SL": round(sl, 4)})
                    save_signal(coin, "SHORT", "5m", current_price, current_price - (atr * 1.5), current_price - (atr * 3.0), current_price - (atr * 4.5), sl, short_score)
            except: pass
        l, s = st.columns(2)
        with l: st.dataframe(pd.DataFrame(scan_long) if scan_long else pd.DataFrame(columns=["No Active 5m Long"]), use_container_width=True)
        with s: st.dataframe(pd.DataFrame(scan_short) if scan_short else pd.DataFrame(columns=["No Active 5m Short"]), use_container_width=True)

    run_5m_scanner(df_market)

# ---------------------------------------------------------
# TAB 2: DAY TRADING MODE (15m)
# ---------------------------------------------------------
with tab2:
    st.markdown("### 📊 INDEPENDENT ACCURACY DASHBOARD (15m)")
    render_accuracy_dashboard("15m")
    
    @st.fragment(run_every=30)
    def run_15m_scanner(market_df):
        st.subheader("🔥 REAL-TIME 15m SMC SCANNER (Auto-Updates)")
        scan_long, scan_short = [], []
        for coin in market_df["symbol"].tolist()[:20]:
            try:
                kline = get_klines(coin, "15m")
                if kline.empty or len(kline) < 30: continue
                close = kline["close"]
                current_price = close.iloc[-1]
                ema50 = calculate_ema(close, 50).iloc[-1]
                rsi = calculate_rsi(close).iloc[-1]
                atr = calculate_atr(kline).iloc[-1]
                if atr == 0 or np.isnan(atr): continue

                bos_bull, bos_bear, fvg_bull, fvg_bear, ob_bull, ob_bear = detect_smc_features(kline)
                long_score = sum([20 if current_price > ema50 else 0, 20 if 40 < rsi < 70 else 0, 20 if bos_bull else 0, 20 if fvg_bull else 0, 20 if ob_bull else 0])
                short_score = sum([20 if current_price < ema50 else 0, 20 if 30 < rsi < 60 else 0, 20 if bos_bear else 0, 20 if fvg_bear else 0, 20 if ob_bear else 0])

                if long_score >= 60:
                    sl = current_price - (atr * 1.5)
                    scan_long.append({"COIN": coin, "PRICE": f"${current_price:,.4f}", "SMC SCORE": f"{long_score}%", "ENTRY": round(current_price, 4), "TP1": round(current_price + (atr * 1.5), 4), "SL": round(sl, 4)})
                    save_signal(coin, "LONG", "15m", current_price, current_price + (atr * 1.5), current_price + (atr * 3.0), current_price + (atr * 4.5), sl, long_score)
                if short_score >= 60:
                    sl = current_price + (atr * 1.5)
                    scan_short.append({"COIN": coin, "PRICE": f"${current_price:,.4f}", "SMC SCORE": f"{short_score}%", "ENTRY": round(current_price, 4), "TP1": round(current_price - (atr * 1.5), 4), "SL": round(sl, 4)})
                    save_signal(coin, "SHORT", "15m", current_price, current_price - (atr * 1.5), current_price - (atr * 3.0), current_price - (atr * 4.5), sl, short_score)
            except: pass
        l, s = st.columns(2)
        with l: st.dataframe(pd.DataFrame(scan_long) if scan_long else pd.DataFrame(columns=["No Active 15m Long"]), use_container_width=True)
        with s: st.dataframe(pd.DataFrame(scan_short) if scan_short else pd.DataFrame(columns=["No Active 15m Short"]), use_container_width=True)

    run_15m_scanner(df_market)

# ---------------------------------------------------------
# TAB 3: SWING TRADING MODE (1h)
# ---------------------------------------------------------
with tab3:
    st.markdown("### 📊 INDEPENDENT ACCURACY DASHBOARD (1h)")
    render_accuracy_dashboard("1h")
    
    @st.fragment(run_every=30)
    def run_1h_scanner(market_df):
        st.subheader("🔥 REAL-TIME 1h SMC SCANNER (Auto-Updates)")
        scan_long, scan_short = [], []
        for coin in market_df["symbol"].tolist()[:20]:
            try:
                kline = get_klines(coin, "1h")
                if kline.empty or len(kline) < 30: continue
                close = kline["close"]
                current_price = close.iloc[-1]
                ema50 = calculate_ema(close, 50).iloc[-1]
                rsi = calculate_rsi(close).iloc[-1]
                atr = calculate_atr(kline).iloc[-1]
                if atr == 0 or np.isnan(atr): continue

                bos_bull, bos_bear, fvg_bull, fvg_bear, ob_bull, ob_bear = detect_smc_features(kline)
                long_score = sum([20 if current_price > ema50 else 0, 20 if 40 < rsi < 70 else 0, 20 if bos_bull else 0, 20 if fvg_bull else 0, 20 if ob_bull else 0])
                short_score = sum([20 if current_price < ema50 else 0, 20 if 30 < rsi < 60 else 0, 20 if bos_bear else 0, 20 if fvg_bear else 0, 20 if ob_bear else 0])

                if long_score >= 60:
                    sl = current_price - (atr * 1.5)
                    scan_long.append({"COIN": coin, "PRICE": f"${current_price:,.4f}", "SMC SCORE": f"{long_score}%", "ENTRY": round(current_price, 4), "TP1": round(current_price + (atr * 1.5), 4), "SL": round(sl, 4)})
                    save_signal(coin, "LONG", "1h", current_price, current_price + (atr * 1.5), current_price + (atr * 3.0), current_price + (atr * 4.5), sl, long_score)
                if short_score >= 60:
                    sl = current_price + (atr * 1.5)
                    scan_short.append({"COIN": coin, "PRICE": f"${current_price:,.4f}", "SMC SCORE": f"{short_score}%", "ENTRY": round(current_price, 4), "TP1": round(current_price - (atr * 1.5), 4), "SL": round(sl, 4)})
                    save_signal(coin, "SHORT", "1h", current_price, current_price - (atr * 1.5), current_price - (atr * 3.0), current_price - (atr * 4.5), sl, short_score)
            except: pass
        l, s = st.columns(2)
        with l: st.dataframe(pd.DataFrame(scan_long) if scan_long else pd.DataFrame(columns=["No Active 1h Long"]), use_container_width=True)
        with s: st.dataframe(pd.DataFrame(scan_short) if scan_short else pd.DataFrame(columns=["No Active 1h Short"]), use_container_width=True)

    run_1h_scanner(df_market)

# ---------------------------------------------------------
# TAB 4: ALL SIGNALS HISTORY
# ---------------------------------------------------------
with tab4:
    st.subheader("📜 QUANTUM CENTRAL SIGNAL DATABASE")
    st.markdown("මෙතන ඔයාගේ සේව් වුණු සියලුම සිග්නල් සහ ඒවා ලයිව් මාකට් එකේ **TP/SL වැදුණද නැද්ද** කියන ලොග් එක බලාගන්න පුළුවන් මචං.")
    
    all_signals = pd.read_sql("SELECT id, coin, signal, timeframe, entry, tp1, tp2, sl, status, created_at FROM signals ORDER BY id DESC", conn)
    if not all_signals.empty:
        st.dataframe(all_signals, use_container_width=True)
    else:
        st.info("No signals stored inside the database yet. Let the scanner run for a moment!")

# =========================================================
# COIN SPECIFIC INDEPENDENT INTERACTION PORTAL
# =========================================================
st.markdown("---")
st.subheader("🔍 COIN SPECIFIC SMC DEEP INTERACTION")

@st.fragment(run_every=30)
def render_deep_portal():
    p_col1, p_col2 = st.columns([3, 1])
    with p_col1:
        search_coin = st.text_input("Enter Coin Asset Name (e.g., BTC, ETH, SOL)", "BTC", key="stable_search")
    with p_col2:
        portal_tf = st.selectbox("CHART TIMEFRAME", ["5m", "15m", "1h"], index=1, key="portal_tf_select")
        
    selected_coin = f"{search_coin.upper()}USDT"
    kline = get_klines(selected_coin, portal_tf)

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
            <h2 style='text-align: center; color:#38bdf8;'>{selected_coin} ({portal_tf}) Advanced SMC Portal</h2>
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
        fig.add_trace(go.Scatter(x=kline['time'], y=kline['EMA50'], line=dict(color='#6366f1', width=2), name="EMA 50 Line"))
        
        fig.update_layout(
            template="plotly_dark", xaxis_rangeslider_visible=False, height=500,
            paper_bgcolor='rgba(15,23,42,0.55)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        t1, t2 = st.columns(2)
        with t1:
            st.success(f"🟢 INSTITUTIONAL LONG MATRIX\n\n🔹 entry point: {current_price:,.4f}\n\n🎯 target 1: {current_price+(atr_val*1.5):,.4f}\n🎯 target 2: {current_price+(atr_val*3.0):,.4f}\n\n🛑 stop trigger: {current_price-(atr_val*1.5):,.4f}")
        with t2:
            st.error(f"🔴 INSTITUTIONAL SHORT MATRIX\n\n🔹 entry point: {current_price:,.4f}\n\n🎯 target 1: {current_price-(atr_val*1.5):,.4f}\n🎯 target 2: {current_price-(atr_val*3.0):,.4f}\n\n🛑 stop trigger: {current_price+(atr_val*1.5):,.4f}")
    else:
        st.warning("Please type a valid asset name or wait for data synchronization...")

render_deep_portal()
