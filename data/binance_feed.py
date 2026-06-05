@st.cache_data(ttl=60)
def get_top_coins(limit=200):

    try:

        coins = []

        pages = 5   # more coins fetch

        for page in range(pages):

            url = "https://min-api.cryptocompare.com/data/top/mktcapfull"

            params = {
                "tsym": "USD",
                "limit": 100,
                "page": page
            }

            r = requests.get(
                url,
                params=params,
                timeout=10
            )

            data = r.json()


            for item in data.get("Data", []):

                symbol = item["CoinInfo"]["Name"]

                if symbol:
                    coins.append(
                        symbol + "USDT"
                    )


        # remove duplicates
        coins = list(set(coins))


        return coins[:limit]


    except Exception as e:

        st.error(f"Data Error: {e}")
        return []
