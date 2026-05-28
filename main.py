# =========================================================
# TRADING TYPE + AI SCANNER + ACCURACY DASHBOARD
# =========================================================

st.markdown("---")

trading_type = st.selectbox(

    "🎯 SELECT TRADING TYPE",

    [
        "SCALPING",
        "DAY TRADING",
        "SWING TRADING"
    ]

)

# =========================================================
# AUTO TIMEFRAME
# =========================================================

if trading_type == "SCALPING":

    auto_timeframe = "5m"

elif trading_type == "DAY TRADING":

    auto_timeframe = "15m"

else:

    auto_timeframe = "1h"

st.success(
    f"ACTIVE TIMEFRAME : {auto_timeframe}"
)

# =========================================================
# SIGNAL TRACKER DATABASE
# =========================================================

try:

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

        created_at TEXT

    )

    """)

    conn.commit()

except:
    pass

# =========================================================
# SAVE SIGNAL
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
    probability
):

    try:

        cursor.execute("""

        INSERT INTO signals (

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
            created_at

        )

        VALUES (?,?,?,?,?,?,?,?,?,?,?)

        """, (

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
            str(datetime.now())

        ))

        conn.commit()

    except:
        pass

# =========================================================
# UPDATE SIGNAL STATUS
# =========================================================

def update_signal_status():

    try:

        signals = pd.read_sql(
            "SELECT * FROM signals WHERE status='RUNNING'",
            conn
        )

        if signals.empty:
            return

        for _, row in signals.iterrows():

            try:

                coin = row["coin"]

                timeframe = row["timeframe"]

                signal_type = row["signal"]

                tp1 = float(row["tp1"])

                tp2 = float(row["tp2"])

                tp3 = float(row["tp3"])

                sl = float(row["sl"])

                signal_id = int(row["id"])

                kline = get_klines(
                    coin,
                    timeframe
                )

                current_price = kline["close"].iloc[-1]

                # =====================================
                # LONG
                # =====================================

                if signal_type == "LONG":

                    if current_price >= tp3:

                        cursor.execute(

                            "UPDATE signals SET status='TP3 HIT' WHERE id=?",

                            (signal_id,)

                        )

                    elif current_price >= tp2:

                        cursor.execute(

                            "UPDATE signals SET status='TP2 HIT' WHERE id=?",

                            (signal_id,)

                        )

                    elif current_price >= tp1:

                        cursor.execute(

                            "UPDATE signals SET status='TP1 HIT' WHERE id=?",

                            (signal_id,)

                        )

                    elif current_price <= sl:

                        cursor.execute(

                            "UPDATE signals SET status='SL HIT' WHERE id=?",

                            (signal_id,)

                        )

                # =====================================
                # SHORT
                # =====================================

                else:

                    if current_price <= tp3:

                        cursor.execute(

                            "UPDATE signals SET status='TP3 HIT' WHERE id=?",

                            (signal_id,)

                        )

                    elif current_price <= tp2:

                        cursor.execute(

                            "UPDATE signals SET status='TP2 HIT' WHERE id=?",

                            (signal_id,)

                        )

                    elif current_price <= tp1:

                        cursor.execute(

                            "UPDATE signals SET status='TP1 HIT' WHERE id=?",

                            (signal_id,)

                        )

                    elif current_price >= sl:

                        cursor.execute(

                            "UPDATE signals SET status='SL HIT' WHERE id=?",

                            (signal_id,)

                        )

                conn.commit()

            except:
                pass

    except:
        pass

# =========================================================
# RUN STATUS CHECKER
# =========================================================

update_signal_status()

# =========================================================
# AI SIGNAL SCANNER
# =========================================================

st.subheader(
    "🔥 80%+ AI SIGNAL SCANNER"
)

long_signals = []

short_signals = []

scan_coins = df["symbol"].head(75).tolist()

progress = st.progress(0)

status_text = st.empty()

for idx, coin in enumerate(scan_coins):

    try:

        progress.progress(
            (idx + 1) / len(scan_coins)
        )

        status_text.info(
            f"Scanning {coin}"
        )

        scan_kline = get_klines(
            coin,
            auto_timeframe
        )

        close = scan_kline["close"]

        current_price = close.iloc[-1]

        rsi = calculate_rsi(close).iloc[-1]

        macd, sig = calculate_macd(close)

        macd_value = macd.iloc[-1]

        ema20 = calculate_ema(
            close,
            20
        ).iloc[-1]

        ema50 = calculate_ema(
            close,
            50
        ).iloc[-1]

        ema200 = calculate_ema(
            close,
            100
        ).iloc[-1]

        atr = calculate_atr(
            scan_kline
        ).iloc[-1]

        # =========================================
        # LONG SCORE
        # =========================================

        long_score = 0

        if rsi < 35:
            long_score += 25

        if macd_value > 0:
            long_score += 25

        if ema20 > ema50:
            long_score += 25

        if ema50 > ema200:
            long_score += 25

        short_score = 100 - long_score

        # =========================================
        # LONG SIGNALS
        # =========================================

        if long_score >= 80:

            entry = current_price

            sl = current_price - (
                atr * 1.5
            )

            tp1 = current_price + (
                atr * 2
            )

            tp2 = current_price + (
                atr * 4
            )

            tp3 = current_price + (
                atr * 6
            )

            long_signals.append({

                "COIN":coin,

                "PRICE":round(
                    current_price,
                    4
                ),

                "LONG %":long_score,

                "ENTRY":round(
                    entry,
                    4
                ),

                "TP1":round(
                    tp1,
                    4
                ),

                "TP2":round(
                    tp2,
                    4
                ),

                "SL":round(
                    sl,
                    4
                )

            })

            save_signal(

                coin,
                "LONG",
                auto_timeframe,
                entry,
                tp1,
                tp2,
                tp3,
                sl,
                long_score

            )

        # =========================================
        # SHORT SIGNALS
        # =========================================

        if short_score >= 80:

            entry = current_price

            sl = current_price + (
                atr * 1.5
            )

            tp1 = current_price - (
                atr * 2
            )

            tp2 = current_price - (
                atr * 4
            )

            tp3 = current_price - (
                atr * 6
            )

            short_signals.append({

                "COIN":coin,

                "PRICE":round(
                    current_price,
                    4
                ),

                "SHORT %":short_score,

                "ENTRY":round(
                    entry,
                    4
                ),

                "TP1":round(
                    tp1,
                    4
                ),

                "TP2":round(
                    tp2,
                    4
                ),

                "SL":round(
                    sl,
                    4
                )

            })

            save_signal(

                coin,
                "SHORT",
                auto_timeframe,
                entry,
                tp1,
                tp2,
                tp3,
                sl,
                short_score

            )

    except:
        pass

progress.empty()
status_text.empty()

# =========================================================
# DISPLAY LONG / SHORT TABLES
# =========================================================

lcol, scol = st.columns(2)

with lcol:

    st.markdown(
        "## 🚀 LONG 80%+"
    )

    if len(long_signals) > 0:

        long_df = pd.DataFrame(
            long_signals
        )

        st.dataframe(

            long_df,

            use_container_width=True,

            height=500

        )

    else:

        st.warning(
            "NO LONG SIGNALS"
        )

with scol:

    st.markdown(
        "## 🔴 SHORT 80%+"
    )

    if len(short_signals) > 0:

        short_df = pd.DataFrame(
            short_signals
        )

        st.dataframe(

            short_df,

            use_container_width=True,

            height=500

        )

    else:

        st.warning(
            "NO SHORT SIGNALS"
        )

# =========================================================
# ACCURACY DASHBOARD
# =========================================================

st.subheader(
    "📊 AI ACCURACY DASHBOARD"
)

signals_df = pd.read_sql(
    "SELECT * FROM signals",
    conn
)

if not signals_df.empty:

    total_signals = len(
        signals_df
    )

    tp1_hits = len(

        signals_df[
            signals_df["status"] == "TP1 HIT"
        ]

    )

    tp2_hits = len(

        signals_df[
            signals_df["status"] == "TP2 HIT"
        ]

    )

    tp3_hits = len(

        signals_df[
            signals_df["status"] == "TP3 HIT"
        ]

    )

    sl_hits = len(

        signals_df[
            signals_df["status"] == "SL HIT"
        ]

    )

    running = len(

        signals_df[
            signals_df["status"] == "RUNNING"
        ]

    )

    total_wins = (
        tp1_hits +
        tp2_hits +
        tp3_hits
    )

    if total_signals > 0:

        win_rate = round(

            (
                total_wins /
                total_signals
            ) * 100,

            2

        )

    else:

        win_rate = 0

    a,b,c,d,e,f = st.columns(6)

    with a:
        st.metric(
            "TOTAL",
            total_signals
        )

    with b:
        st.metric(
            "RUNNING",
            running
        )

    with c:
        st.metric(
            "TP1",
            tp1_hits
        )

    with d:
        st.metric(
            "TP2",
            tp2_hits
        )

    with e:
        st.metric(
            "TP3",
            tp3_hits
        )

    with f:
        st.metric(
            "WIN RATE",
            f"{win_rate}%"
        )

    chart_df = pd.DataFrame({

        "STATUS":[
            "TP1",
            "TP2",
            "TP3",
            "SL"
        ],

        "COUNT":[
            tp1_hits,
            tp2_hits,
            tp3_hits,
            sl_hits
        ]

    })

    fig_acc = px.bar(

        chart_df,

        x="STATUS",

        y="COUNT",

        template="plotly_dark",

        title="AI SIGNAL ACCURACY"

    )

    st.plotly_chart(

        fig_acc,

        use_container_width=True

    )

    st.dataframe(

        signals_df.sort_values(

            by="id",

            ascending=False

        ),

        use_container_width=True,

        height=500

    )
