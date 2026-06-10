import pandas as pd

def apply_smc(df):

    df = df.copy()

    # =========================
    # 🧠 MOMENTUM CLASSIFICATION
    # =========================
    def trend(x):
        if x > 3:
            return "🟢 STRONG BULLISH"
        elif x > 0:
            return "🟢 BULLISH"
        elif x < -3:
            return "🔴 STRONG BEARISH"
        elif x < 0:
            return "🔴 BEARISH"
        else:
            return "🟡 SIDEWAYS"

    df["SMC Signal"] = df["Change %"].apply(trend)

    # =========================
    # 💧 LIQUIDITY (Volume zones)
    # =========================
    vol_median = df["Volume"].median()

    def liquidity(v):
        if v > vol_median * 2:
            return "🔥 HIGH LIQUIDITY"
        elif v > vol_median:
            return "⚡ MEDIUM"
        else:
            return "🧊 LOW"

    df["Liquidity"] = df["Volume"].apply(liquidity)

    return df
