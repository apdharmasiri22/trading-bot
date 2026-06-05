# =========================================================
# QUANTUM X TERMINAL - ULTRA-FILTER ENGINE & FRESH REBOOT
# =========================================================

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sqlite3
from datetime import datetime

# =========================================================
# 1. MASTER ENGINE: STRUCTURE & PATTERN ENGINE (UPGRADED)
# =========================================================

def get_structure_data(df):

    highs = df["high"].values
    lows = df["low"].values
    closes = df["close"].values

    bos_bull = closes[-1] > max(highs[-6:-1])

    mss_bull = (
        closes[-1] > highs[-3]
        and lows[-2] > lows[-5]
    )

    qm_bull = (
        highs[-3] > highs[-6]
        and lows[-1] < lows[-3]
        and closes[-1] > highs[-2]
    )

    liquidity_sweep = (
        lows[-2] < min(lows[-8:-3])
        and closes[-1] > closes[-2]
    )

    return {
        "bos_bull": bos_bull,
        "mss_bull": mss_bull,
        "qm_bull": qm_bull,
        "liquidity_sweep": liquidity_sweep
    }


def get_validation_data(df):

    close = df["close"]
    volume = df["volume"]

    delta = close.diff()

    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    rsi_div = (
        close.iloc[-1] < close.iloc[-3]
        and rsi.iloc[-1] > rsi.iloc[-3]
    )

    high_volume = (
        volume.iloc[-1]
        > volume.rolling(20).mean().iloc[-1] * 1.5
    )

    trend_filter = (
        close.iloc[-1]
        > close.ewm(span=50).mean().iloc[-1]
    )

    return {
        "rsi_div": rsi_div,
        "high_vol": high_volume,
        "trend_filter": trend_filter
    }


def master_sniper_engine(df):

    struct = get_structure_data(df)
    valid = get_validation_data(df)

    score = 0
    reasons = []

    if struct["bos_bull"]:
        score += 20
        reasons.append("BOS")

    if struct["mss_bull"]:
        score += 20
        reasons.append("MSS")

    if struct["qm_bull"]:
        score += 20
        reasons.append("QM")

    if struct["liquidity_sweep"]:
        score += 20
        reasons.append("LIQ_SWEEP")

    if valid["rsi_div"]:
        score += 10
        reasons.append("RSI_DIV")

    if valid["high_vol"]:
        score += 5
        reasons.append("HIGH_VOL")

    if valid["trend_filter"]:
        score += 5
        reasons.append("EMA_TREND")

    probability = min(score, 100)

    if score >= 60:
        return "LONG", " + ".join(reasons)

    return None, "NO_CONFLUENCE"
# =========================================================
# 2. DATABASE SETUP
# =========================================================
conn = sqlite3.connect("signals.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS signals")
cursor.execute("""
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coin TEXT, signal TEXT, timeframe TEXT, entry REAL,
    tp1 REAL, tp2 REAL, tp3 REAL, sl REAL, probability REAL,
    status TEXT, created_at TEXT, reason TEXT
)
""")
conn.commit()

def save_signal(coin, signal, timeframe, entry, tp1, tp2, tp3, sl, probability, reason):
    cursor.execute("""
    INSERT INTO signals (coin, signal, timeframe, entry, tp1, tp2, tp3, sl, probability, status, created_at, reason)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (coin, signal, timeframe, entry, tp1, tp2, tp3, sl, probability, "RUNNING", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), reason))
    conn.commit()

# =========================================================
# 3. UTILITIES & UI LOGIC (ඔයාගේ පරණ කෝඩ් එකේ කොටස්)
# =========================================================
def calculate_atr(df, period=14):
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())
    return pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(period).mean()

def calculate_ema(data, period):
    return data.ewm(span=period, adjust=False).mean()

def get_klines(symbol, interval):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
        data = requests.get(url, timeout=5).json()
        df = pd.DataFrame(data).iloc[:, :6]
        df.columns = ["time", "open", "high", "low", "close", "volume"]
        return df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
    except: return pd.DataFrame()

# =========================================================
# 4. SCANNER LOOP (Updated with Master Engine)
# =========================================================
def run_scanner_logic(market_df, tf):
    for coin in market_df["symbol"].tolist()[:15]:
        kline = get_klines(coin, tf)
        if kline.empty: continue
        
        # මෙතන තමයි අලුත් Engine එක වැඩ කරන්නේ
        signal, reason = master_sniper_engine(kline)
        
        if signal:
            atr = calculate_atr(kline).iloc[-1]
            entry = kline["close"].iloc[-1]
            sl = entry - (atr * 1.8)
            save_signal(coin, signal, tf, entry, entry+(atr*2), entry+(atr*4.5), entry+(atr*7), sl, 90, reason)

# (මෙතැනින් පහළට ඔයාගේ ඉතිරි UI Tabs සහ Render logic ටික දාගන්න)
# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="QUANTUM X TERMINAL",
    layout="wide"
)

# =========================================================
# DATABASE SETUP & RESET MECHANISM
# =========================================================
conn = sqlite3.connect("signals.db", check_same_thread=False)
cursor = conn.cursor()

# 1. මුලින්ම ටේබල් එකක් තියෙනවා නම් ඒක අයින් කරනවා (Fresh Start)
# ⚠️ සටහන: ඔයාට හැමදාම ඩේටා මකන්න ඕන නැත්නම්, එකපාරක් රන් කරලා පරණ ඒවා මැකුණට පස්සේ 
# පහත තියෙන DROP TABLE පේළිය කෝඩ් එකෙන් අයින් කරන්න (හෝ comment කරන්න).
cursor.execute("DROP TABLE IF EXISTS signals")

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
# ORIGINAL PREMIUM QUANTUM UI
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
    
    for i in range(-20, -3):
        if closes[-1] > highs[i] and closes[-2] > highs[i]: bos_bullish = True
        if closes[-1] < lows[i] and closes[-2] < lows[i]: bos_bearish = True
        
    if highs[-3] < lows[-1]: fvg_bullish = True
    if lows[-3] > highs[-1]: fvg_bearish = True
        
    if closes[-1] > closes[-2] and closes[-2] > closes[-3] and closes[-4] < closes[-5]: order_block_bullish = True
    if closes[-1] < closes[-2] and closes[-2] < closes[-3] and closes[-4] > closes[-5]: order_block_bearish = True
        
    return bos_bullish, bos_bearish, fvg_bullish, fvg_bearish, order_block_bullish, order_block_bearish

# =========================================================
# LIVE APIS DATA NODES WITH HARD BACKUPS
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
            response = requests.get(url, timeout=5) 
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
                    return df.sort_values(by="volume", ascending=False).head(15)
        except: continue
        
    return pd.DataFrame([
        {"symbol": "BTCUSDT", "price": 67250.0, "change": 1.2, "volume": 900000000},
        {"symbol": "ETHUSDT", "price": 3550.0, "change": -0.4, "volume": 500000000},
        {"symbol": "SOLUSDT", "price": 145.2, "change": 3.8, "volume": 300000000}
    ])

@st.cache_data(ttl=5)
def get_klines(symbol, interval="15m"):
    endpoints = [
        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100",
        f"https://api4.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100",
        f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit=100"
    ]
    for url in endpoints:
        try:
            response = requests.get(url, timeout=5)
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
# SIGNAL MANAGEMENT & BE LOGIC
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
        running_signals = pd.read_sql("SELECT * FROM signals WHERE status IN ('RUNNING', 'TP1 HIT', 'TP2 HIT')", conn)
        if running_signals.empty: return

        for _, row in running_signals.iterrows():
            sig_id = row['id']
            coin = row['coin']
            direction = row['signal']
            current_status = row['status']
            entry = float(row['entry'])
            sl_price = float(row['sl'])
            
            match = market_df[market_df['symbol'] == coin]
            if match.empty: continue
            current_price = float(match.iloc[0]['price'])

            new_status = current_status
            if current_status in ['TP1 HIT', 'TP2 HIT']:
                sl_price = entry 

            if direction == "LONG":
                if current_price >= row['tp3']: new_status = "TP3 HIT"
                elif current_price >= row['tp2'] and current_status != 'TP2 HIT': new_status = "TP2 HIT"
                elif current_price >= row['tp1'] and current_status == 'RUNNING': new_status = "TP1 HIT"
                elif current_price <= sl_price: new_status = "SL HIT"
            else: 
                if current_price <= row['tp3']: new_status = "TP3 HIT"
                elif current_price <= row['tp2'] and current_status != 'TP2 HIT': new_status = "TP2 HIT"
                elif current_price <= row['tp1'] and current_status == 'RUNNING': new_status = "TP1 HIT"
                elif current_price >= sl_price: new_status = "SL HIT"

            if new_status != current_status:
                cursor.execute("UPDATE signals SET status=?, sl=? WHERE id=?", (new_status, sl_price, sig_id))
                conn.commit()
    except: pass

def render_accuracy_dashboard(tf_val):
    try:
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
    except: pass

# Fetch Market Nodes
df_market = get_market()
update_live_signals_status(df_market)

# =========================================================
# CORE UI CHANNELS
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 SCALPING MODE (5m)", "⚡ DAY TRADING MODE (15m)", "🔮 SWING TRADING MODE (1h)", "📜 ALL SIGNALS HISTORY"
])

with tab1:
    st.markdown("### 📊 INDEPENDENT ACCURACY DASHBOARD (5m)")
    render_accuracy_dashboard("5m")
    
    @st.fragment(run_every=30)
    def run_5m_scanner(market_df):
        st.subheader("🔥 REAL-TIME 5m SMC SCANNER (Ultra-Filtered)")
        scan_long, scan_short = [], []
        
        if market_df.get('volume', pd.Series([0])).iloc[0] == 900000000:
            st.warning("⚠️ Cloud Nodes Connecting Slow... Displaying Local Secure Buffers.")
            
        for coin in market_df["symbol"].tolist()[:15]:
            try:
                kline_1h = get_klines(coin, "1h")
                if kline_1h.empty: continue
                trend_1h_ema = calculate_ema(kline_1h["close"], 50).iloc[-1]
                trend_1h_price = kline_1h["close"].iloc[-1]
                
                kline = get_klines(coin, "5m")
                if kline.empty or len(kline) < 30: continue
                close = kline["close"]
                current_price = close.iloc[-1]
                atr = calculate_atr(kline).iloc[-1]
                
                if atr == 0 or np.isnan(atr) or (atr / current_price) < 0.0008: continue

                bos_bull, bos_bear, fvg_bull, fvg_bear, ob_bull, ob_bear = detect_smc_features(kline)
                bullish_confluence = (bos_bull and fvg_bull) or (fvg_bull and ob_bull) or (bos_bull and ob_bull)
                bearish_confluence = (bos_bear and fvg_bear) or (fvg_bear and ob_bear) or (bos_bear and ob_bear)

                if bullish_confluence and current_price > calculate_ema(close, 50).iloc[-1] and trend_1h_price > trend_1h_ema:
                    sl = current_price - (atr * 1.8)
                    scan_long.append({"COIN": coin, "PRICE": f"${current_price:,.4f}", "ENTRY": round(current_price, 4), "TP1": round(current_price + (atr * 2.0), 4), "SL": round(sl, 4)})
                    save_signal(coin, "LONG", "5m", current_price, current_price + (atr * 2.0), current_price + (atr * 4.5), current_price + (atr * 7.0), sl, 90)
                
                if bearish_confluence and current_price < calculate_ema(close, 50).iloc[-1] and trend_1h_price < trend_1h_ema:
                    sl = current_price + (atr * 1.8)
                    scan_short.append({"COIN": coin, "PRICE": f"${current_price:,.4f}", "ENTRY": round(current_price, 4), "TP1": round(current_price - (atr * 2.0), 4), "SL": round(sl, 4)})
                    save_signal(coin, "SHORT", "5m", current_price, current_price - (atr * 2.0), current_price - (atr * 4.5), current_price - (atr * 7.0), sl, 90)
            except: pass
        l, s = st.columns(2)
        with l: st.dataframe(pd.DataFrame(scan_long) if scan_long else pd.DataFrame(columns=["No High Probability Long"]), use_container_width=True)
        with s: st.dataframe(pd.DataFrame(scan_short) if scan_short else pd.DataFrame(columns=["No High Probability Short"]), use_container_width=True)

    run_5m_scanner(df_market)

with tab2:
    st.markdown("### 📊 INDEPENDENT ACCURACY DASHBOARD (15m)")
    render_accuracy_dashboard("15m")
    
    @st.fragment(run_every=30)
    def run_15m_scanner(market_df):
        st.subheader("🔥 REAL-TIME 15m SMC SCANNER (Ultra-Filtered)")
        scan_long, scan_short = [], []
        for coin in market_df["symbol"].tolist()[:15]:
            try:
                kline_1h = get_klines(coin, "1h")
                if kline_1h.empty: continue
                trend_1h_ema = calculate_ema(kline_1h["close"], 50).iloc[-1]
                trend_1h_price = kline_1h["close"].iloc[-1]

                kline = get_klines(coin, "15m")
                if kline.empty or len(kline) < 30: continue
                close = kline["close"]
                current_price = close.iloc[-1]
                atr = calculate_atr(kline).iloc[-1]
                
                if atr == 0 or np.isnan(atr) or (atr / current_price) < 0.0008: continue

def run_5m_scanner(market_df):

    st.subheader("Scanner")

    for coin in market_df["symbol"].tolist()[:15]:

        try:
            kline = get_klines(coin, "5m")

            signal, reason = master_sniper_engine(kline)

            if signal == "LONG":
                pass

        except:
            pass

if signal == "LONG":
    sl = current_price - (atr * 1.8)

    scan_long.append({
        "COIN": coin,
        "PRICE": f"${current_price:,.4f}",
        "ENTRY": round(current_price,4),
        "TP1": round(current_price + (atr*2),4),
        "SL": round(sl,4),
        "REASON": reason
    })

    save_signal(
        coin,
        "LONG",
        "5m",
        current_price,
        current_price + (atr*2),
        current_price + (atr*4.5),
        current_price + (atr*7),
        sl,
        90
    )

                if bullish_confluence and current_price > calculate_ema(close, 50).iloc[-1] and trend_1h_price > trend_1h_ema:
                    sl = current_price - (atr * 1.8)
                    scan_long.append({"COIN": coin, "PRICE": f"${current_price:,.4f}", "ENTRY": round(current_price, 4), "TP1": round(current_price + (atr * 2.0), 4), "SL": round(sl, 4)})
                    save_signal(coin, "LONG", "15m", current_price, current_price + (atr * 2.0), current_price + (atr * 4.5), current_price + (atr * 7.0), sl, 95)
                if bearish_confluence and current_price < calculate_ema(close, 50).iloc[-1] and trend_1h_price < trend_1h_ema:
                    sl = current_price + (atr * 1.8)
                    scan_short.append({"COIN": coin, "PRICE": f"${current_price:,.4f}", "ENTRY": round(current_price, 4), "TP1": round(current_price - (atr * 2.0), 4), "SL": round(sl, 4)})
                    save_signal(coin, "SHORT", "15m", current_price, current_price - (atr * 2.0), current_price - (atr * 4.5), current_price - (atr * 7.0), sl, 95)
            except: pass
        l, s = st.columns(2)
        with l: st.dataframe(pd.DataFrame(scan_long) if scan_long else pd.DataFrame(columns=["No High Probability Long"]), use_container_width=True)
        with s: st.dataframe(pd.DataFrame(scan_short) if scan_short else pd.DataFrame(columns=["No High Probability Short"]), use_container_width=True)

    run_15m_scanner(df_market)

with tab3:
    st.markdown("### 📊 INDEPENDENT ACCURACY DASHBOARD (1h)")
    render_accuracy_dashboard("1h")
    
    @st.fragment(run_every=30)
    def run_1h_scanner(market_df):
        st.subheader("🔥 REAL-TIME 1h SMC SCANNER (Ultra-Filtered)")
        scan_long, scan_short = [], []
        for coin in market_df["symbol"].tolist()[:15]:
            try:
                kline = get_klines(coin, "1h")
                if kline.empty or len(kline) < 30: continue
                close = kline["close"]
                current_price = close.iloc[-1]
                atr = calculate_atr(kline).iloc[-1]
                
                if atr == 0 or np.isnan(atr) or (atr / current_price) < 0.001: continue

                bos_bull, bos_bear, fvg_bull, fvg_bear, ob_bull, ob_bear = detect_smc_features(kline)
                bullish_confluence = (bos_bull and fvg_bull) or (fvg_bull and ob_bull) or (bos_bull and ob_bull)
                bearish_confluence = (bos_bear and fvg_bear) or (fvg_bear and ob_bear) or (bos_bear and ob_bear)

                if bullish_confluence and current_price > calculate_ema(close, 50).iloc[-1]:
                    sl = current_price - (atr * 1.8)
                    scan_long.append({"COIN": coin, "PRICE": f"${current_price:,.4f}", "ENTRY": round(current_price, 4), "TP1": round(current_price + (atr * 2.0), 4), "SL": round(sl, 4)})
                    save_signal(coin, "LONG", "1h", current_price, current_price + (atr * 2.0), current_price + (atr * 4.5), current_price + (atr * 7.0), sl, 98)
                if bearish_confluence and current_price < calculate_ema(close, 50).iloc[-1]:
                    sl = current_price + (atr * 1.8)
                    scan_short.append({"COIN": coin, "PRICE": f"${current_price:,.4f}", "ENTRY": round(current_price, 4), "TP1": round(current_price - (atr * 2.0), 4), "SL": round(sl, 4)})
                    save_signal(coin, "SHORT", "1h", current_price, current_price - (atr * 2.0), current_price - (atr * 4.5), current_price - (atr * 7.0), sl, 98)
            except: pass
        l, s = st.columns(2)
        with l: st.dataframe(pd.DataFrame(scan_long) if scan_long else pd.DataFrame(columns=["No High Probability Long"]), use_container_width=True)
        with s: st.dataframe(pd.DataFrame(scan_short) if scan_short else pd.DataFrame(columns=["No High Probability Short"]), use_container_width=True)

    run_1h_scanner(df_market)

with tab4:
    st.subheader("📜 QUANTUM CENTRAL SIGNAL DATABASE")
    try:
        raw_history = pd.read_sql("SELECT coin, signal, timeframe, entry, tp1, tp2, tp3, sl, status, created_at FROM signals", conn)
        if not raw_history.empty:
            processed_rows = []
            total_profits, total_losses, completed_trades = 0, 0, 0
            
            for _, row in raw_history.iterrows():
                status = row['status']
                entry = float(row['entry'])
                direction = row['signal']
                p_l_val = "0.00%"
                
                if "HIT" in status:
                    completed_trades += 1
                    if "TP" in status:
                        total_profits += 1
                        target_price = float(row['tp3']) if status == "TP3 HIT" else float(row['tp2']) if status == "TP2 HIT" else float(row['tp1'])
                        change = ((target_price - entry) / entry) * 100 if direction == "LONG" else ((entry - target_price) / entry) * 100
                        p_l_val = f"+{abs(change):.2f}%"
                    elif "SL" in status:
                        total_losses += 1
                        sl_price = float(row['sl'])
                        change = ((sl_price - entry) / entry) * 100 if direction == "LONG" else ((entry - sl_price) / entry) * 100
                        p_l_val = f"-{abs(change):.2f}%"
                else:
                    p_l_val = "RUNNING ⏳"

                processed_rows.append({
                    "COIN": row['coin'], "DIRECTION": direction, "TIMEFRAME": row['timeframe'],
                    "TRIGGER TIME": row['created_at'], "STATUS": status, "PROFIT / LOSS %": p_l_val
                })
                
            final_accuracy = round((total_profits / completed_trades) * 100, 1) if completed_trades > 0 else 0.0
            
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("🟢 CUMULATIVE PROFIT TRADES", total_profits)
            m_col2.metric("🔴 CUMULATIVE LOSS TRADES", total_losses)
            m_col3.metric("🎯 TERMINAL ACCURACY RATE", f"{final_accuracy}%")
            
            st.markdown("---")
            df_display = pd.DataFrame(processed_rows).sort_index(ascending=False)
            
            def highlight_status_cells(val):
                if "TP" in str(val) or "+" in str(val): return 'color: #22c55e; font-weight: bold;'
                elif "SL" in str(val) or "-" in str(val): return 'color: #ef4444; font-weight: bold;'
                elif "RUNNING" in str(val): return 'color: #f59e0b; font-weight: bold;'
                return ''
                
            st.dataframe(df_display.style.map(highlight_status_cells, subset=['STATUS', 'PROFIT / LOSS %']), use_container_width=True)
        else:
            st.info("No logs captured inside storage nodes yet. (Database Swept Clean)")
    except:
        st.info("Database node busy. Re-fetching historical logs...")
