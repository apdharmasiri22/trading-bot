import requests
import streamlit as st

st.write("Testing Binance...")

r = requests.get(
    "https://fapi.binance.com/fapi/v1/ticker/24hr",
    timeout=10
)

st.write(r.status_code)
st.write(r.text[:500])

import streamlit as st

from binance_scanner import get_market_data


st.set_page_config(
    page_title="SMC AI Dashboard",
    layout="wide"
)


st.title("📊 SMC AI Trading Dashboard")

st.subheader("Binance Market Scanner")


df = get_market_data()


if df.empty:

    st.error("Binance data loading failed")

else:


    col1,col2,col3 = st.columns(3)


    with col1:

        min_volume = st.number_input(
            "Minimum Volume",
            value=10000000
        )


    with col2:

        change = st.number_input(
            "Change %",
            value=0.0
        )


    with col3:

        limit = st.slider(
            "Show Coins",
            5,
            50,
            20
        )


    filtered = df[

        (df["Volume"] >= min_volume)
        &
        (df["Change %"] >= change)

    ]


    filtered = filtered.sort_values(
        "Volume",
        ascending=False
    )


    st.dataframe(
        filtered.head(limit),
        use_container_width=True
    )


    st.divider()


    st.subheader("🎯 Select Coin")


    coin = st.selectbox(
        "Choose Coin",
        filtered["Symbol"].tolist()
    )


    st.success(
        f"Selected: {coin}"
    )
