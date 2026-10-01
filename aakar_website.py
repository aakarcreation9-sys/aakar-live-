from flask import Flask
import yfinance as yf
import datetime

app = Flask(__name__)

def get_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            prev = data['Open'].iloc[0]
            change = price - prev
            pct = (change/prev)*100
            return f"{price:,.2f}", f"{change:+.2f} ({pct:+.2f}%)", change>=0
    except:
        pass
    return "Loading...", "", True

@app.route('/')
def home():
    nifty_p, nifty_c, nifty_up = get_price("^NSEI")
    sensex_p, sensex_c, sensex_up = get_price("^BSESN")
    bank_p, bank_c, bank_up = get_price("^NSEBANK")

    now = datetime.datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    c1 = "#22c55e" if nifty_up else "#ef4444"
    c2 = "#22c55e" if sensex_up else "#ef4444"
    c3 = "#22c55e" if bank_up else "#ef4444"

    return f"""
    <html>
    <head>
        <title>Aakar Live - NIFTY | SENSEX</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body{{background:#0f172a;color:white;font-family:Arial;text-align:center;margin:0;padding:20px}}
           .card{{background:#1e293b;padding:25px;margin:15px auto;border-radius:15px;max-width:400px}}
            h1{{color:#38bdf8}}
           .price{{font-size:32px;font-weight:bold;margin:10px 0}}
           .chart{{max-width:800px;margin:20px auto;background:#1e293b;border-radius:15px;padding:10px}}
        </style>
    </head>
    <body>
        <h1>AAKAR LIVE MARKET</h1>
        <p>Last Update: {now} | Auto-refresh 30s</p>

        <div class="card">
            <h2>NIFTY 50</h2>
            <div class="price" style="color:{c1}">Rs {nifty_p}</div>
            <div style="color:{c1}">{nifty_c}</div>
        </div>

        <div class="card">
            <h2>SENSEX</h2>
            <div class="price" style="color:{c2}">Rs {sensex_p}</div>
            <div style="color:{c2}">{sensex_c}</div>
        </div>

        <div class="card">
            <h2>BANK NIFTY</h2>
            <div class="price" style="color:{c3}">Rs {bank_p}</div>
            <div style="color:{c3}">{bank_c}</div>
        </div>

        <div class="chart">
            <h3>📈 Live Chart - NIFTY 50</h3>
            <div class="tradingview-widget-container">
              <div id="tradingview_nifty"></div>
              <script src="https://s3.tradingview.com/tv.js"></script>
              <script>
                new TradingView.widget({{
                  "width": "100%", "height": 400, "symbol": "NSE:NIFTY",
                  "interval": "D", "timezone": "Asia/Kolkata",
                  "theme": "dark", "style": "1", "locale": "in",
                  "toolbar_bg": "#f1f3f6", "enable_publishing": false,
                  "allow_symbol_change": true, "container_id": "tradingview_nifty"
                }});
              </script>
            </div>
        </div>

        <div class="chart">
            <h3>📈 Live Chart - SENSEX</h3>
            <div id="tradingview_sensex"></div>
            <script>
                new TradingView.widget({{
                  "width": "100%", "height": 400, "symbol": "BSE:SENSEX",
                  "interval": "D", "timezone": "Asia/Kolkata",
                  "theme": "dark", "style": "1", "locale": "in",
                  "container_id": "tradingview_sensex"
                }});
            </script>
        </div>
        <script>setTimeout(()=>location.reload(),30000);</script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
