import streamlit as st
from streamlit_autorefresh import st_autorefresh
from data.binance_feed import get_top_coins, get_price

# =========================
# 🏆 APP CONFIG
# =========================
st.set_page_config(layout="wide")
st.title("📊 SMC Quantum Trading Dashboard")
st_autorefresh(interval=30000, key="refresh")

# =========================
# 🪙 LIVE BINANCE COIN SELECTOR
# =========================
# මෙතනින් කෙලින්ම BTCUSDT වගේ එන නිසා වෙනස් කරන්න ඕනේ නැහැ
coins = get_top_coins(20)

if coins:
    coin = st.selectbox("🔍 Select Coin", coins)
    st.markdown(f"### 📌 Selected Coin: `{coin}`")

    # =========================
    # 💰 LIVE PRICE
    # =========================
    price = get_price(coin)
    
    if price:
        st.success(f"💰 Live Price: {price}")
    else:
        st.error("Price loading failed")

    # =========================
    # 📈 TRADINGVIEW CHART
    # =========================
    st.subheader("📈 TradingView Chart")
    symbol = f"BINANCE:{coin}"

    html_code = f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "width": "100%", "height": 500,
        "symbol": "{symbol}",
        "interval": "15",
        "theme": "dark",
        "style": "1",
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    st.components.v1.html(html_code, height=550)
else:
    st.error("Could not fetch coin list. Check your internet or API connection.")

# =========================
# 🧠 ANALYSIS PANEL (Engine ready)
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 Market Bias")
    st.info("⏳ Waiting for SMC Engine (Part 3)")

with col2:
    st.subheader("🎯 Entry Zone")
    st.warning("FVG / Order Block will appear here")

with col3:
    st.subheader("⚠️ Risk (SL / TP)")
    st.error("TP1 / TP2 / SL pending engine")

st.markdown("---")

# =========================
# 📌 FOOTER
# =========================
st.caption("SMC Quantum Trading Dashboard v1.0 - Integrated Version")
