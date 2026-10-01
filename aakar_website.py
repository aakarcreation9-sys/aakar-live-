from flask import Flask
import yfinance as yf
import datetime

app = Flask(__name__)

# ===== YAHAN PE LIVE CANDLE FORMULA COPY KIYA HAI =====
def get_live_candle(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval="1m") # 1 min ka live data
        if df.empty:
            return None

        # FORMULA
        OPEN = df['Open'].iloc[0] # 9:15 ka pehla price
        HIGH = df['High'].max() # Din ka sabse high
        LOW = df['Low'].min() # Din ka sabse low
        CLOSE = df['Close'].iloc[-1] # Abhi ka price

        is_green = CLOSE > OPEN
        color = "#22c55e" if is_green else "#ef4444"
        candle_type = "GREEN 🟢" if is_green else "RED 🔴"

        return {
            "OPEN": f"{OPEN:,.2f}",
            "HIGH": f"{HIGH:,.2f}",
            "LOW": f"{LOW:,.2f}",
            "CLOSE": f"{CLOSE:,.2f}",
            "COLOR": color,
            "TYPE": candle_type
        }
    except:
        return None

@app.route('/')
def home():
    nifty = get_live_candle("^NSEI")
    sensex = get_live_candle("^BSESN")
    bank = get_live_candle("^NSEBANK")

    if not nifty:
        return "<h1>Market Closed hai, 9:15 AM pe LIVE hoga</h1>"

    now = datetime.datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

    return f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Aakar Live Candle</title>
        <style>
            body{{background:#0f172a;color:white;font-family:Arial;text-align:center;padding:20px}}
           .card{{background:#1e293b;padding:20px;margin:15px auto;border-radius:15px;max-width:500px;border:2px solid {nifty['COLOR']}}}
           .row{{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #334155}}
           .chart{{max-width:850px;margin:25px auto;background:#1e293b;border-radius:15px;padding:10px}}
        </style>
    </head>
    <body>
        <h1>AAKAR LIVE CANDLE</h1>
        <p>{now} - Auto Refresh 10s</p>

        <div class="card">
            <h2>NIFTY 50 - {nifty['TYPE']}</h2>
            <div class="row"><span>OPEN (9:15)</span><span>{nifty['OPEN']}</span></div>
            <div class="row"><span>HIGH</span><span style="color:#22c55e">{nifty['HIGH']}</span></div>
            <div class="row"><span>LOW</span><span style="color:#ef4444">{nifty['LOW']}</span></div>
            <div class="row"><span>CLOSE (LTP)</span><span style="color:{nifty['COLOR']};font-weight:bold;font-size:22px">{nifty['CLOSE']}</span></div>
        </div>

        <div class="card" style="border-color:{sensex['COLOR']}">
            <h2>SENSEX - {sensex['TYPE']}</h2>
            <div class="row"><span>OPEN</span><span>{sensex['OPEN']}</span></div>
            <div class="row"><span>HIGH</span><span>{sensex['HIGH']}</span></div>
            <div class="row"><span>LOW</span><span>{sensex['LOW']}</span></div>
            <div class="row"><span>CLOSE</span><span style="color:{sensex['COLOR']};font-weight:bold;font-size:22px">{sensex['CLOSE']}</span></div>
        </div>

        <div class="chart">
            <h3>📈 LIVE TradingView Chart</h3>
            <div id="tv"></div>
            <script src="https://s3.tradingview.com/tv.js"></script>
            <script>
                new TradingView.widget({{
                  "width":"100%","height":450,"symbol":"NSE:NIFTY",
                  "interval":"1","timezone":"Asia/Kolkata",
                  "theme":"dark","style":"1","locale":"in","container_id":"tv"
                }});
            </script>
        </div>
        <script>setTimeout(()=>location.reload(),10000);</script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
