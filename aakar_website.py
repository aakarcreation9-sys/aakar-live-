from flask import Flask, render_template_string
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Aakar Live - NIFTY | SENSEX</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial;background:#0f172a;color:white;text-align:center;padding:20px}
.card{background:#1e293b;padding:20px;margin:15px auto;max-width:400px;border-radius:15px;box-shadow:0 4px 15px rgba(0,0,0,0.3)}
h1{color:#38bdf8}
.price{font-size:32px;font-weight:bold;color:#22c55e}
.time{color:#94a3b8;font-size:14px}
</style>
<script>
setTimeout(()=>{location.reload()}, 30000);
</script>
</head>
<body>
<h1>AAKAR LIVE MARKET</h1>
<p class="time">Last Update: {{time}} | Auto-refresh 30s</p>

<div class="card">
<h2>NIFTY 50</h2>
<div class="price">Rs {{nifty_price}}</div>
<p style="color:{{nifty_color}}">{{nifty_change}}</p>
</div>

<div class="card">
<h2>SENSEX</h2>
<div class="price">Rs {{sensex_price}}</div>
<p style="color:{{sensex_color}}">{{sensex_change}}</p>
</div>

<div class="card">
<h2>BANK NIFTY</h2>
<div class="price">Rs {{banknifty_price}}</div>
<p style="color:{{banknifty_color}}">{{banknifty_change}}</p>
</div>

<p class="time">Made by Aakar Creation</p>
</body>
</html>
"""

def get_live(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1m")
        if len(data)==0:
            data = ticker.history(period="1d")
        price = float(data['Close'].iloc[-1])
        prev = float(data['Close'].iloc[0])
        try:
            prev = ticker.info.get('previousClose', prev)
        except:
            pass
        ch = price - prev
        pct = (ch/prev)*100 if prev!=0 else 0
        color = "#22c55e" if ch>=0 else "#ef4444"
        return f"{price:,.2f}", f"{ch:+.2f} ({pct:+.2f}%)", color
    except:
        return "Loading...", "Live...", "#94a3b8"

@app.route('/')
def home():
    nifty_price, nifty_change, nifty_color = get_live("^NSEI")
    sensex_price, sensex_change, sensex_color = get_live("^BSESN")
    banknifty_price, banknifty_change, banknifty_color = get_live("^NSEBANK")
    return render_template_string(HTML,
        time=datetime.now().strftime("%d-%m-%Y %I:%M:%S %p"),
        nifty_price=nifty_price, nifty_change=nifty_change, nifty_color=nifty_color,
        sensex_price=sensex_price, sensex_change=sensex_change, sensex_color=sensex_color,
        banknifty_price=banknifty_price, banknifty_change=banknifty_change, banknifty_color=banknifty_color
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
