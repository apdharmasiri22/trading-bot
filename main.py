from flask import Flask, render_template_string

app = Flask(__name__)

html = """

<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Institutional Dashboard</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<script src="https://cdn.tailwindcss.com"></script>

<style>

body{
    background:#020617;
    color:white;
    font-family:'Inter',sans-serif;
    margin:0;
    padding:0;
    overflow-x:hidden;
}

.orbitron{
    font-family:'Orbitron',sans-serif;
}

.dashboard-wrapper{
    width:100%;
    min-height:100vh;
    padding:20px;
}

.dashboard-container{
    width:100%;
    min-height:100vh;
    background:#0f172a;
    border:1px solid #22304d;
    border-radius:24px;
    padding:20px;
}

.main-grid{
    display:grid;
    grid-template-columns:repeat(12,minmax(0,1fr));
    gap:20px;
}

.left-panel{
    grid-column:span 4;
}

.center-panel{
    grid-column:span 4;
}

.right-panel{
    grid-column:span 4;
}

.pro-panel{
    background:linear-gradient(
        145deg,
        rgba(15,23,42,0.95),
        rgba(2,6,23,0.98)
    );

    border:1px solid #22304d;
    border-radius:18px;
    padding:16px;
    overflow:hidden;
}

.card-box{
    background:#111827;
    border:1px solid #22304d;
    border-radius:14px;
    padding:14px;
    margin-bottom:14px;
}

.live-dot{
    width:10px;
    height:10px;
    background:#10b981;
    border-radius:50%;
    animation:pulse 1.5s infinite;
}

@keyframes pulse{
    0%{
        opacity:0.3;
        transform:scale(1);
    }

    50%{
        opacity:1;
        transform:scale(1.3);
    }

    100%{
        opacity:0.3;
        transform:scale(1);
    }
}

.copy-target{
    cursor:pointer;
    transition:0.25s;
    padding:4px 8px;
    border-radius:8px;
}

.copy-target:hover{
    background:rgba(56,189,248,0.12);
}

iframe{
    border:none;
}

@media(max-width:1200px){

    .main-grid{
        grid-template-columns:1fr;
    }

    .left-panel,
    .center-panel,
    .right-panel{
        grid-column:span 12;
    }

}

</style>

</head>

<body>

<div class="dashboard-wrapper">

<div class="dashboard-container">

<!-- TOP BAR -->

<div class="flex flex-wrap justify-between items-center gap-4 mb-6">

    <div>

        <h1 class="orbitron text-2xl text-cyan-400 font-bold flex items-center gap-3">

            <i class="fa-solid fa-tower-broadcast text-green-400"></i>

            INSTITUTIONAL UNIVERSAL SCANNER

        </h1>

        <p class="text-slate-400 text-sm mt-2">

            Professional Binance Institutional Dashboard

        </p>

    </div>

    <div class="flex items-center gap-3">

        <div class="live-dot"></div>

        <span class="text-green-400 orbitron text-sm">
            LIVE
        </span>

    </div>

</div>

<!-- MAIN GRID -->

<div class="main-grid">

<!-- LEFT PANEL -->

<div class="left-panel">

    <div class="pro-panel">

        <div class="orbitron text-cyan-400 mb-4">
            MARKET SCANNER
        </div>

        <div id="scannerList"></div>

    </div>

</div>

<!-- CENTER PANEL -->

<div class="center-panel">

    <div class="pro-panel">

        <div class="orbitron text-cyan-400 mb-4">
            ACTIVE ASSET
        </div>

        <div class="card-box">

            <label class="text-slate-400 text-sm">
                Symbol
            </label>

            <div class="flex gap-2 mt-2">

                <input
                id="symbolInput"
                value="BTC"
                class="bg-slate-900 border border-slate-700 px-4 py-2 rounded-lg w-full text-white">

                <button
                onclick="loadSymbol()"
                class="bg-cyan-500 hover:bg-cyan-400 px-4 py-2 rounded-lg text-black font-bold">

                    LOAD

                </button>

            </div>

        </div>

        <div class="card-box">

            <div class="flex justify-between mb-3">

                <span class="text-slate-400">
                    Current Price
                </span>

                <span id="currentPrice"
                class="orbitron text-cyan-400 font-bold">

                    Loading...

                </span>

            </div>

            <div class="flex justify-between mb-3">

                <span class="text-slate-400">
                    24H High
                </span>

                <span id="highPrice"
                class="orbitron text-green-400 font-bold">

                    Loading...

                </span>

            </div>

            <div class="flex justify-between">

                <span class="text-slate-400">
                    24H Low
                </span>

                <span id="lowPrice"
                class="orbitron text-red-400 font-bold">

                    Loading...

                </span>

            </div>

        </div>

        <div class="card-box">

            <div class="orbitron text-sm text-cyan-400 mb-3">
                SIGNAL ENGINE
            </div>

            <div id="signalText"
            class="text-lg font-bold text-green-400">

                WAITING...

            </div>

        </div>

    </div>

</div>

<!-- RIGHT PANEL -->

<div class="right-panel">

    <div class="pro-panel">

        <div class="orbitron text-cyan-400 mb-4">
            LIVE CHART
        </div>

        <iframe
        src="https://s.tradingview.com/widgetembed/?symbol=BINANCE:BTCUSDT&interval=15&theme=dark"
        width="100%"
        height="500">
        </iframe>

    </div>

</div>

</div>

<!-- BOTTOM -->

<div class="grid grid-cols-1 lg:grid-cols-4 gap-4 mt-6">

    <div class="card-box">

        <div class="text-slate-400 text-sm mb-2">
            AI SCORE
        </div>

        <div id="aiScore"
        class="orbitron text-2xl text-cyan-400">

            82 / 100

        </div>

    </div>

    <div class="card-box">

        <div class="text-slate-400 text-sm mb-2">
            Funding Rate
        </div>

        <div id="fundingRate"
        class="orbitron text-green-400">

            Loading...

        </div>

    </div>

    <div class="card-box">

        <div class="text-slate-400 text-sm mb-2">
            Open Interest
        </div>

        <div id="openInterest"
        class="orbitron text-yellow-400">

            Loading...

        </div>

    </div>

    <div class="card-box">

        <div class="text-slate-400 text-sm mb-2">
            Whale Status
        </div>

        <div id="whaleStatus"
        class="orbitron text-red-400">

            Monitoring...

        </div>

    </div>

</div>

</div>

</div>

<script>

let activeSymbol = "BTCUSDT";

async function loadSymbol(){

    const symbol =
    document.getElementById("symbolInput")
    .value
    .toUpperCase() + "USDT";

    activeSymbol = symbol;

    await loadTicker();
}

async function loadTicker(){

    try{

        const response =
        await fetch(
        `https://api.binance.com/api/v3/ticker/24hr?symbol=${activeSymbol}`
        );

        const data = await response.json();

        document.getElementById("currentPrice").innerText =
        "$" + parseFloat(data.lastPrice).toLocaleString();

        document.getElementById("highPrice").innerText =
        "$" + parseFloat(data.highPrice).toLocaleString();

        document.getElementById("lowPrice").innerText =
        "$" + parseFloat(data.lowPrice).toLocaleString();

        const change =
        parseFloat(data.priceChangePercent);

        const signal =
        document.getElementById("signalText");

        if(change > 0){

            signal.innerText =
            "STRONG LONG";

            signal.className =
            "text-lg font-bold text-green-400";

        }else{

            signal.innerText =
            "STRONG SHORT";

            signal.className =
            "text-lg font-bold text-red-400";
        }

    }catch(err){

        console.log(err);

    }

}

async function scanner(){

    try{

        const response =
        await fetch(
        "https://api.binance.com/api/v3/ticker/24hr"
        );

        const data = await response.json();

        const usdt =
        data
        .filter(x => x.symbol.endsWith("USDT"))
        .slice(0,15);

        const container =
        document.getElementById("scannerList");

        container.innerHTML = "";

        usdt.forEach(coin => {

            const change =
            parseFloat(coin.priceChangePercent);

            const color =
            change >= 0
            ? "text-green-400"
            : "text-red-400";

            container.innerHTML += `

                <div
                onclick="selectCoin('${coin.symbol}')"
                class="card-box cursor-pointer hover:border-cyan-400 transition-all">

                    <div class="flex justify-between">

                        <span class="orbitron">
                            ${coin.symbol}
                        </span>

                        <span class="${color} font-bold">
                            ${change.toFixed(2)}%
                        </span>

                    </div>

                </div>

            `;
        });

    }catch(err){

        console.log(err);

    }

}

function selectCoin(symbol){

    document.getElementById("symbolInput")
    .value =
    symbol.replace("USDT","");

    activeSymbol = symbol;

    loadTicker();

}

async function funding(){

    try{

        const response =
        await fetch(
        `https://fapi.binance.com/fapi/v1/premiumIndex?symbol=${activeSymbol}`
        );

        const data = await response.json();

        document.getElementById("fundingRate")
        .innerText =
        parseFloat(data.lastFundingRate * 100)
        .toFixed(4) + "%";

    }catch(err){

        console.log(err);

    }

}

async function whale(){

    try{

        const response =
        await fetch(
        `https://api.binance.com/api/v3/depth?symbol=${activeSymbol}&limit=50`
        );

        const data = await response.json();

        let detected = false;

        data.bids.forEach(b => {

            const usd =
            parseFloat(b[0]) *
            parseFloat(b[1]);

            if(usd > 1000000){
                detected = true;
            }

        });

        document.getElementById("whaleStatus")
        .innerText =
        detected
        ? "Whale Wall Detected"
        : "Normal";

    }catch(err){

        console.log(err);

    }

}

async function openInterest(){

    try{

        const response =
        await fetch(
        `https://fapi.binance.com/futures/data/openInterestHist?symbol=${activeSymbol}&period=5m&limit=1`
        );

        const data = await response.json();

        if(data[0]){

            document.getElementById("openInterest")
            .innerText =
            parseFloat(data[0].sumOpenInterest)
            .toLocaleString();

        }

    }catch(err){

        console.log(err);

    }

}

async function boot(){

    await loadTicker();

    await scanner();

    await funding();

    await whale();

    await openInterest();

}

boot();

setInterval(boot,15000);

</script>

</body>
</html>

"""

@app.route("/")
def home():
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
