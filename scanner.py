import requests

def get_top_coins():

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 20,
        "page": 1,
        "sparkline": False
    }

    r = requests.get(url, params=params, timeout=10)

    if r.status_code != 200:
        return ["BTCUSDT"]

    data = r.json()

    coins = []

    for c in data:

        symbol = c.get("symbol")

        if not symbol:
            continue

        symbol = symbol.upper()

        # 🚨 FIX: skip bad values like USDT
        if symbol in ["USDT", "USD", "BUSD"]:
            continue

        coins.append(symbol + "USDT")

    # safety fallback
    if not coins:
        coins = ["BTCUSDT"]

    return coins
