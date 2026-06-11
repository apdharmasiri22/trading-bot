import pandas as pd

# =========================
# SWINGS (BASIS FOR BOS/CHoCH)
# =========================
def find_swings(df, lookback=3):

    df = df.copy()
    highs = df["High"]
    lows = df["Low"]

    df["SwingHigh"] = highs[(highs.shift(1) < highs) & (highs.shift(-1) < highs)]
    df["SwingLow"] = lows[(lows.shift(1) > lows) & (lows.shift(-1) > lows)]

    return df


# =========================
# BOS / CHOCH
# =========================
def detect_structure(df):

    df = find_swings(df)

    last_high = None
    last_low = None

    bos = []
    choch = []

    for i in range(len(df)):

        high = df["High"].iloc[i]
        low = df["Low"].iloc[i]
        close = df["Close"].iloc[i]

        if pd.notna(df["SwingHigh"].iloc[i]):
            last_high = df["SwingHigh"].iloc[i]

        if pd.notna(df["SwingLow"].iloc[i]):
            last_low = df["SwingLow"].iloc[i]

        # BOS
        if last_high and close > last_high:
            bos.append("🚀 BOS Bullish")
        elif last_low and close < last_low:
            bos.append("🔻 BOS Bearish")
        else:
            bos.append("")

        # CHoCH
        if last_high and close < last_high:
            choch.append("🔄 CHoCH Bearish")
        elif last_low and close > last_low:
            choch.append("🔄 CHoCH Bullish")
        else:
            choch.append("")

    df["BOS"] = bos
    df["CHoCH"] = choch

    return df


# =========================
# ORDER BLOCK (SIMPLE VERSION)
# =========================
def order_blocks(df):

    df = df.copy()
    ob = [""] * len(df)

    for i in range(2, len(df)):

        if df["Close"].iloc[i] > df["High"].iloc[i-1]:
            ob[i-1] = "🟢 Bullish OB"

        if df["Close"].iloc[i] < df["Low"].iloc[i-1]:
            ob[i-1] = "🔴 Bearish OB"

    df["OrderBlock"] = ob
    return df


# =========================
# FVG
# =========================
def fvg(df):

    df = df.copy()
    gap = [""] * len(df)

    for i in range(2, len(df)):

        if df["Low"].iloc[i] > df["High"].iloc[i-2]:
            gap[i] = "🟢 Bullish FVG"

        if df["High"].iloc[i] < df["Low"].iloc[i-2]:
            gap[i] = "🔴 Bearish FVG"

    df["FVG"] = gap
    return df


# =========================
# LIQUIDITY SWEEP
# =========================
def liquidity_sweep(df):

    df = df.copy()
    sweep = [""] * len(df)

    for i in range(1, len(df)):

        # wick sweep high
        if df["High"].iloc[i] > df["High"].iloc[i-1] and df["Close"].iloc[i] < df["High"].iloc[i-1]:
            sweep[i] = "⚡ High Sweep"

        # wick sweep low
        if df["Low"].iloc[i] < df["Low"].iloc[i-1] and df["Close"].iloc[i] > df["Low"].iloc[i-1]:
            sweep[i] = "⚡ Low Sweep"

    df["LiquiditySweep"] = sweep
    return df


# =========================
# MAIN ENGINE
# =========================
def apply_smc(df):

    df = detect_structure(df)
    df = order_blocks(df)
    df = fvg(df)
    df = liquidity_sweep(df)

    return df
