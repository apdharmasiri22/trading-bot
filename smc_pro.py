import pandas as pd

def apply_smc_pro(df):

    df = df.copy()

    # =========================
    # 📊 MOMENTUM SCORE (0-100)
    # =========================
    def score(row):

        change = abs(row["Change %"])
        volume = row["Volume"]

        score = min(change * 10, 50) + min(volume / 1e7, 50)

        return round(min(score, 100), 2)

    df["SMC Score"] = df.apply(score, axis=1)

    # =========================
    # 🧠 MARKET STRUCTURE LOGIC
    # =========================
    def structure(x):

        if x > 7:
            return "🚀 BOS (Bullish Break)"
        elif x < -7:
            return "🔻 CHoCH (Bearish Shift)"
        elif x > 2:
            return "📈 Bullish Trend"
        elif x < -2:
            return "📉 Bearish Trend"
        else:
            return "⚖️ Sideways"

    df["Structure"] = df["Change %"].apply(structure)

    # =========================
    # 💧 LIQUIDITY ZONES
    # =========================
    vol_med = df["Volume"].median()

    def liquidity(v):
        if v > vol_med * 2:
            return "🔥 High Liquidity"
        elif v > vol_med:
            return "⚡ Medium"
        else:
            return "🧊 Low"

    df["Liquidity"] = df["Volume"].apply(liquidity)

    # =========================
    # 🎯 TRADE SIGNAL
    # =========================
    def signal(row):

        if row["SMC Score"] > 70 and row["Change %"] > 3:
            return "🟢 BUY SETUP"
        elif row["SMC Score"] > 70 and row["Change %"] < -3:
            return "🔴 SELL SETUP"
        else:
            return "🟡 WAIT"

    df["Signal"] = df.apply(signal, axis=1)

    return df
