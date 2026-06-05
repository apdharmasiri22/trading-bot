import requests
import pandas as pd

BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"

# =========================
# 🪙 GET ALL COINS
# =========================
def get_all_coins():

    try:
        data = requests.get(BINANCE_URL, timeout=5).json()

        coins = []

        for item in data:
            symbol = item["symbol"]

            # only USDT pairs
            if symbol.endswith("USDT"):
                coins.append({
                    "symbol": symbol,
                    "priceChangePercent": float(item["priceChangePercent"]),
                    "volume": float(item["quoteVolume"])
                })

        return coins

    except:
        return []


# =========================
# 🔥 TOP VOLUME COINS
# =========================
def get_top_coins(limit=20):

    coins = get_all_coins()

    df = pd.DataFrame(coins)

    if df.empty:
        return []

    df = df.sort_values(by="volume", ascending=False)

    return df.head(limit)["symbol"].tolist()


# =========================
# 💰 GET LIVE PRICE
# =========================
def get_price(symbol):

    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        data = requests.get(url, timeout=5).json()

        return float(data["price"])

    except:
        return None
