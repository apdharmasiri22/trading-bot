import requests
import pandas as pd

BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"


# =========================
# GET ALL BINANCE COINS
# =========================
def get_all_coins():
    try:
        response = requests.get(BINANCE_URL, timeout=10)
        data = response.json()

        coins = []

        for item in data:
            symbol = item.get("symbol")

            if symbol and symbol.endswith("USDT"):
                coins.append({
                    "symbol": symbol,
                    "volume": float(item.get("quoteVolume", 0))
                })

        return coins

    except Exception as e:
        print("Binance Error:", e)
        return []


# =========================
# TOP COINS
# =========================
def get_top_coins(limit=100):
    coins = get_all_coins()

    if not coins:
        return ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]

    df = pd.DataFrame(coins)

    df = df.sort_values(by="volume", ascending=False)

    return df.head(limit)["symbol"].tolist()


# =========================
# LIVE PRICE (FIXED)
# =========================
def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        res = requests.get(url, timeout=10)
        data = res.json()

        # safety check
        if "price" not in data:
            print("Invalid response:", data)
            return None

        return float(data["price"])

    except Exception as e:
        print("Price Error:", e)
        return None
