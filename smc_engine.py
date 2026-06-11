import pandas as pd


# ==========================
# SWING DETECTION
# ==========================

def find_swings(df, window=3):

    df = df.copy()

    df["Swing High"] = False
    df["Swing Low"] = False


    for i in range(window, len(df)-window):

        high = df["High"].iloc[i]
        low = df["Low"].iloc[i]


        if (
            high > df["High"].iloc[i-window:i].max()
            and high > df["High"].iloc[i+1:i+window+1].max()
        ):
            df.loc[df.index[i], "Swing High"] = True


        if (
            low < df["Low"].iloc[i-window:i].min()
            and low < df["Low"].iloc[i+1:i+window+1].min()
        ):
            df.loc[df.index[i], "Swing Low"] = True


    return df



# ==========================
# BOS / CHoCH
# ==========================

def apply_structure(df):

    df = find_swings(df)

    df["Structure"] = "⚖️ SIDEWAYS"


    last_high = None
    last_low = None


    for i in range(len(df)):

        if df["Swing High"].iloc[i]:
            last_high = df["High"].iloc[i]


        if df["Swing Low"].iloc[i]:
            last_low = df["Low"].iloc[i]


        price = df["Close"].iloc[i]


        if last_high and price > last_high:
            df.loc[df.index[i], "Structure"] = "🚀 BULLISH BOS"


        elif last_low and price < last_low:
            df.loc[df.index[i], "Structure"] = "🔻 BEARISH CHoCH"



    return df



# ==========================
# SMC ENGINE
# ==========================

def apply_smc(df):

    df = df.copy()

    required = ["High", "Low", "Close"]

    # check OHLC
    if not all(col in df.columns for col in required):
        df["Structure"] = "⚠️ NO CANDLE DATA"
        df["Liquidity"] = "N/A"
        return df

    # apply real structure engine
    df = apply_structure(df)

    return df
