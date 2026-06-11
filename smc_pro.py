import pandas as pd

def apply_smc_pro(df):

    df = df.copy()

    vol_med = df["Volume"].median()

    signals = []

    # =========================
    # MAIN LOOP
    # =========================
    for i in range(len(df)):

        open_p = df["Open"].iloc[i]
        close = df["Close"].iloc[i]
        volume = df["Volume"].iloc[i]

        change = (close - open_p) / open_p * 100

        # =========================
        # SIMPLE SIGNAL LOGIC
        # =========================
        if change > 2 and volume > vol_med:
            simple_signal = "🟢 BUY"
        elif change < -2:
            simple_signal = "🔴 SELL"
        else:
            simple_signal = "🟡 WAIT"

        # =========================
        # ADD SMC STYLE FILTER
        # =========================
        if change > 5:
            smc_bias = "🚀 STRONG BULL"
        elif change < -5:
            smc_bias = "🔻 STRONG BEAR"
        else:
            smc_bias = "⚖️ SIDEWAYS"

        # =========================
        # FINAL COMBINED SIGNAL
        # =========================
        final_signal = f"{simple_signal} | {smc_bias}"

        signals.append(final_signal)

    df["Signal"] = signals

    return df
