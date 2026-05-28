import streamlit as st

st.set_page_config(
    page_title="Institutional Dashboard",
    layout="wide"
)

# ===== CUSTOM CSS =====

st.markdown("""

<style>

html, body, [class*="css"]{
    background:#020617;
    color:white;
    font-family:Arial;
}

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
}

.main-card{
    background:#0f172a;
    border:1px solid #22304d;
    border-radius:20px;
    padding:20px;
    margin-bottom:20px;
}

.metric-card{
    background:#111827;
    border:1px solid #22304d;
    border-radius:14px;
    padding:15px;
    text-align:center;
}

.title{
    font-size:32px;
    font-weight:bold;
    color:#38bdf8;
}

.sub{
    color:#94a3b8;
}

.green{
    color:#22c55e;
    font-weight:bold;
}

.red{
    color:#ef4444;
    font-weight:bold;
}

.blue{
    color:#38bdf8;
    font-weight:bold;
}

</style>

""", unsafe_allow_html=True)

# ===== HEADER =====

st.markdown("""

<div class="main-card">

<div class="title">
📡 INSTITUTIONAL UNIVERSAL SCANNER
</div>

<div class="sub">
Professional Institutional Trading Dashboard
</div>

</div>

""", unsafe_allow_html=True)

# ===== TOP METRICS =====

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown("""

    <div class="metric-card">

    <h3>BTC PRICE</h3>

    <div class="blue">
    $68,420
    </div>

    </div>

    """, unsafe_allow_html=True)

with col2:

    st.markdown("""

    <div class="metric-card">

    <h3>AI SCORE</h3>

    <div class="green">
    82 / 100
    </div>

    </div>

    """, unsafe_allow_html=True)

with col3:

    st.markdown("""

    <div class="metric-card">

    <h3>FUNDING</h3>

    <div class="green">
    0.014%
    </div>

    </div>

    """, unsafe_allow_html=True)

with col4:

    st.markdown("""

    <div class="metric-card">

    <h3>SIGNAL</h3>

    <div class="red">
    STRONG LONG
    </div>

    </div>

    """, unsafe_allow_html=True)

# ===== MAIN DASHBOARD =====

left, center, right = st.columns([1,1,1])

# ===== LEFT =====

with left:

    st.markdown("""

    <div class="main-card">

    <h2>🔥 MARKET SCANNER</h2>

    </div>

    """, unsafe_allow_html=True)

    pairs = [
        ("BTCUSDT","+2.42%"),
        ("ETHUSDT","+4.11%"),
        ("SOLUSDT","+8.33%"),
        ("BNBUSDT","-1.24%"),
        ("XRPUSDT","+5.91%"),
        ("DOGEUSDT","+12.44%"),
    ]

    for pair, change in pairs:

        color = "green" if "+" in change else "red"

        st.markdown(f"""

        <div class="metric-card">

        <h3>{pair}</h3>

        <div class="{color}">
        {change}
        </div>

        </div>

        """, unsafe_allow_html=True)

# ===== CENTER =====

with center:

    st.markdown("""

    <div class="main-card">

    <h2>📈 ACTIVE ASSET</h2>

    </div>

    """, unsafe_allow_html=True)

    symbol = st.text_input(
        "Symbol",
        "BTCUSDT"
    )

    timeframe = st.selectbox(
        "Timeframe",
        ["1m","5m","15m","1h","4h"]
    )

    st.markdown(f"""

    <div class="metric-card">

    <h3>{symbol}</h3>

    <div class="blue">
    Timeframe: {timeframe}
    </div>

    </div>

    """, unsafe_allow_html=True)

    st.markdown("""

    <div class="metric-card">

    <h3>ENTRY</h3>

    <div class="green">
    68,200
    </div>

    </div>

    """, unsafe_allow_html=True)

    st.markdown("""

    <div class="metric-card">

    <h3>TAKE PROFIT</h3>

    <div class="green">
    69,500
    </div>

    </div>

    """, unsafe_allow_html=True)

    st.markdown("""

    <div class="metric-card">

    <h3>STOP LOSS</h3>

    <div class="red">
    67,400
    </div>

    </div>

    """, unsafe_allow_html=True)

# ===== RIGHT =====

with right:

    st.markdown("""

    <div class="main-card">

    <h2>📊 LIVE CHART</h2>

    </div>

    """, unsafe_allow_html=True)

    tradingview = """
    <iframe
    src="https://s.tradingview.com/widgetembed/?symbol=BINANCE:BTCUSDT&interval=15&theme=dark"
    width="100%"
    height="500"
    frameborder="0">
    </iframe>
    """

    st.components.v1.html(
        tradingview,
        height=520
    )

# ===== FOOTER =====

st.markdown("""

<div class="main-card">

<h3>⚡ SYSTEM STATUS</h3>

<div class="green">
WEBSOCKET LIVE • AI ENGINE ACTIVE • BINANCE CONNECTED
</div>

</div>

""", unsafe_allow_html=True)
