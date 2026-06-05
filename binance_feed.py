import requests

BASE_URL = "https://api.binance.com/api/v3"


def get_top_coins(limit=200):
    try:
        r = requests.get(f"{BASE_URL}/exchangeInfo", timeout=10)
        data = r.json()

        coins = []

        for s in data.get("symbols", []):
            if isinstance(s, dict):
                if s.get("status") == "TRADING" and s.get("symbol", "").endswith("USDT"):
                    coins.append(s["symbol"])

        return coins[:limit] if coins else ["BTCUSDT", "ETHUSDT"]

    except:
        return ["BTCUSDT", "ETHUSDT"]


def get_price(symbol):
    try:
        r = requests.get(
            f"{BASE_URL}/ticker/price",
            params={"symbol": symbol},
            timeout=10
        )
        return float(r.json()["price"])
    except:
        return None


def get_candles(symbol, limit=50):
    try:
        r = requests.get(
            f"{BASE_URL}/klines",
            params={"symbol": symbol, "interval": "1m", "limit": limit},
            timeout=10
        )

        data = r.json()

        candles = []

        for c in data:
            candles.append({
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4])
            })

        return candles

    except:
        return []
