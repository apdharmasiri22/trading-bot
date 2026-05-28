<!-- ================= CLEAN RESPONSIVE UPGRADE PATCH ================= -->

<style>

/* ===== GLOBAL RESET ===== */

*{
    box-sizing:border-box;
}

html,
body{
    margin:0;
    padding:0;
    width:100%;
    min-height:100vh;
    overflow-x:hidden;
    background:#020617;
    font-family:'Inter',sans-serif;
}

/* ===== BODY FIX ===== */

body{
    background:#020617 !important;
    color:#f8fafc;
}

/* ===== MAIN WRAPPER ===== */

.dashboard-wrapper{
    width:100%;
    min-height:100vh;
    padding:16px;
}

.dashboard-container{
    width:100%;
    min-height:100vh;
    background:#0f172a;
    border:1px solid #22304d;
    border-radius:24px;
    padding:20px;
    overflow:hidden;
}

/* ===== TOP BAR ===== */

.topbar{
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:16px;
    flex-wrap:wrap;
    margin-bottom:20px;
}

/* ===== MAIN GRID ===== */

.main-grid{
    display:grid;
    grid-template-columns:repeat(12,minmax(0,1fr));
    gap:20px;
    align-items:start;
}

/* ===== LEFT ===== */

.left-panel{
    grid-column:span 4;
}

/* ===== CENTER ===== */

.center-panel{
    grid-column:span 4;
}

/* ===== RIGHT ===== */

.right-panel{
    grid-column:span 4;
}

/* ===== PANEL STYLE ===== */

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
    backdrop-filter:blur(12px);
    box-shadow:0 0 25px rgba(56,189,248,0.05);
}

/* ===== RESPONSIVE ===== */

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

/* ===== MOBILE ===== */

@media(max-width:768px){

    .dashboard-wrapper{
        padding:10px;
    }

    .dashboard-container{
        border-radius:14px;
        padding:12px;
    }

    .orbitron{
        font-size:90% !important;
        letter-spacing:0 !important;
    }

    .copy-target{
        font-size:11px !important;
    }

    .pro-panel{
        padding:12px;
    }

}

/* ===== COPY TARGET ===== */

.copy-target{
    cursor:pointer;
    transition:0.25s;
    user-select:all;
    padding:4px 8px;
    border-radius:8px;
}

.copy-target:hover{
    background:rgba(56,189,248,0.12);
}

/* ===== SCROLLBAR ===== */

::-webkit-scrollbar{
    width:6px;
}

::-webkit-scrollbar-track{
    background:#0f172a;
}

::-webkit-scrollbar-thumb{
    background:#22304d;
    border-radius:10px;
}

::-webkit-scrollbar-thumb:hover{
    background:#38bdf8;
}

</style>

<!-- ================= END CLEAN UPGRADE ================= -->



<!-- ================= BODY REPLACE ================= -->

<body>

<div class="dashboard-wrapper">

<div class="dashboard-container">

<!-- TOP BAR -->
<div class="topbar">

    <div>
        <h1 class="orbitron text-xl lg:text-2xl font-bold text-accentBlue tracking-wider flex items-center gap-3">
            <i class="fa-solid fa-tower-broadcast text-accentGreen"></i>
            INSTITUTIONAL
            <span class="text-white">UNIVERSAL SCANNER</span>
        </h1>

        <p class="text-xs text-textSecondary mt-1">
            Sifting 300+ Binance Coins instantly to find trades with Setup Scores above 75%
        </p>
    </div>

    <div class="flex flex-wrap items-center gap-3">

        <span id="scanLoader"
        class="text-accentBlue orbitron text-xs flex items-center gap-2 bg-accentBlue/10 border border-accentBlue/30 px-3 py-1.5 rounded-full">

            <i class="fa-solid fa-spinner fa-spin"></i>
            DISCOVERING GOLDEN SETUPS...

        </span>

        <div class="bg-accentGreen/10 border border-accentGreen/30 text-accentGreen px-3 py-1.5 rounded-full text-xs orbitron flex items-center gap-2 font-semibold">

            <i class="fa-solid fa-circle pulse-indicator"></i>
            WEBSOCKET LIVE

        </div>

    </div>

</div>

<!-- MAIN GRID -->
<div class="main-grid">

    <!-- LEFT -->
    <div class="left-panel">

        <div class="pro-panel">

            <!-- YOUR LEFT PANEL CONTENT HERE -->

        </div>

    </div>

    <!-- CENTER -->
    <div class="center-panel">

        <div class="pro-panel">

            <!-- YOUR CENTER PANEL CONTENT HERE -->

        </div>

    </div>

    <!-- RIGHT -->
    <div class="right-panel">

        <div class="pro-panel">

            <!-- YOUR RIGHT PANEL CONTENT HERE -->

        </div>

    </div>

</div>

</div>
</div>

</body>

<!-- ================= END BODY REPLACE ================= -->



<!-- ================= REMOVE THESE OLD CSS BLOCKS ================= -->

<!-- REMOVE:
FINAL TOP ADJUST
RIGHT PANEL TOP FIX
GAP REDUCTION FIX
INLINE STATUS POSITION FIX
TOP SPACING FIX
REAL FULLSCREEN FIX
FULLSCREEN PROFESSIONAL MODE
-->



<!-- ================= ADD LIVE TRADINGVIEW CHART ================= -->

<div class="pro-panel mt-5">

    <div class="orbitron text-sm font-bold mb-4 text-textPrimary">
        LIVE TRADINGVIEW CHART
    </div>

    <div class="rounded-xl overflow-hidden border border-borderCol">

        <iframe
        src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_chart&symbol=BINANCE:BTCUSDT&interval=15&theme=dark&style=1&locale=en"
        width="100%"
        height="500"
        frameborder="0"
        allowtransparency="true"
        scrolling="no">
        </iframe>

    </div>

</div>

<!-- ================= END TRADINGVIEW ================= -->



<!-- ================= ULTRA PERFORMANCE FIX ================= -->

<script>

/* ===== PERFORMANCE BOOST ===== */

document.addEventListener('DOMContentLoaded',()=>{

    console.log('Institutional Dashboard Loaded');

    // REMOVE DUPLICATE INTERVALS
    if(window.scannerLoop){
        clearInterval(window.scannerLoop);
    }

    if(window.activeAssetLoop){
        clearInterval(window.activeAssetLoop);
    }

    // START CLEAN LOOPS
    window.scannerLoop = setInterval(()=>{

        if(typeof runMarketScanner === 'function'){
            runMarketScanner();
        }

    },15000);

    window.activeAssetLoop = setInterval(()=>{

        if(typeof fetchLiveSymbol === 'function'){
            fetchLiveSymbol();
        }

    },12000);

});

/* ===== AUTO RESIZE ===== */

window.addEventListener('resize',()=>{

    document.body.style.overflowX='hidden';

});

</script>

<!-- ================= END PERFORMANCE FIX ================= -->



<!-- ================= OPTIONAL GLASS EFFECT ================= -->

<style>

.glass-effect{

    background:rgba(15,23,42,0.72);

    backdrop-filter:blur(16px);

    border:1px solid rgba(255,255,255,0.06);

    box-shadow:
        0 8px 32px rgba(0,0,0,0.35),
        inset 0 1px 0 rgba(255,255,255,0.04);

}

</style>

<!-- ================= END GLASS EFFECT ================= -->



<!-- ================= MOBILE OPTIMIZATION ================= -->

<style>

@media(max-width:640px){

    input,
    button{
        min-height:44px;
    }

    .orbitron{
        font-size:12px !important;
    }

    .text-xs{
        font-size:11px !important;
    }

    .text-sm{
        font-size:12px !important;
    }

}

</style>

<!-- ================= END MOBILE OPTIMIZATION ================= -->
