from flask import Flask
import yfinance as yf
import datetime
import pytz

app = Flask(__name__)

def get_orb_levels():
    try:
        ticker = yf.Ticker("^NSEI")
        # Aaj ka 5-min data
        df = ticker.history(period="1d", interval="5m")
        if df.empty or len(df) < 4:
            return None

        # Time ko IST me convert
        df.index = df.index.tz_convert('Asia/Kolkata') if df.index.tz is not None else df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')

        # 9:25 aur 9:35 ki candle dhundo
        candle_925 = None
        candle_935 = None
        live_price = float(df['Close'].iloc[-1])

        for idx, row in df.iterrows():
            t = idx.strftime("%H:%M")
            if t == "09:25":
                candle_925 = {"HIGH": float(row['High']), "LOW": float(row['Low']), "CLOSE": float(row['Close'])}
            if t == "09:35" or t == "09:30": # kabhi 9:30 pe banti hai
                if candle_935 is None: # pehli wali le lo
                    candle_935 = {"HIGH": float(row['High']), "LOW": float(row['Low']), "CLOSE": float(row['Close'])}

        if not candle_925:
            # agar 9:25 ka data nahi hai to pehli 2 candle ka high low le lo
            candle_925 = {"HIGH": float(df['High'][:2].max()), "LOW": float(df['Low'][:2].min()), "CLOSE": float(df['Close'].iloc[1])}
        if not candle_935:
            candle_935 = {"HIGH": float(df['High'][:3].max()), "LOW": float(df['Low'][:3].min()), "CLOSE": float(df['Close'].iloc[2])}

        # FORMULA - Tera 9:25 / 9:35 ka logic
        # Buy = 9:35 High ke upar
        # Sell = 9:35 Low ke niche
        signal = "WAIT"
        if live_price > candle_935["HIGH"]:
            signal = "BUY BREAKOUT 🚀"
        elif live_price < candle_935["LOW"]:
            signal = "SELL BREAKDOWN 🔻"
        else:
            signal = "SIDEWAYS - Range me hai"

        return {
            "925_H": candle_925["HIGH"], "925_L": candle_925["LOW"],
            "935_H": candle_935["HIGH"], "935_L": candle_935["LOW"],
            "LTP": live_price,
            "SIGNAL": signal
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def home():
    data = get_orb_levels()
    now = datetime.datetime.now(datetime.timezone.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%d-%m-%Y %I:%M:%S %p")

    if not data:
        return f"<html><body style='background:#0f172a;color:white;text-align:center;padding:50px'><h1>Market abhi khula nahi - 9:35 ke baad LIVE hoga</h1><p>{now}</p><script>setTimeout(()=>location.reload(),30000);</script></body></html>"

    return f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Aakar 9:25 | 9:35 Formula</title>
        <style>
            body{{background:#0f172a;color:white;font-family:Arial;text-align:center;padding:10px;margin:0}}
           .box{{background:#1e293b;padding:15px;border-radius:12px;max-width:900px;margin:12px auto}}
           .levels{{display:flex;justify-content:space-around;flex-wrap:wrap}}
           .levels div{{background:#0f172a;padding:12px 18px;border-radius:10px;margin:6px;min-width:110px}}
           .buy{{color:#22c55e;border:2px solid #22c55e}}.sell{{color:#ef4444;border:2px solid #ef4444}}
            #tv{{max-width:900px;height:550px;margin:15px auto;border-radius:12px;overflow:hidden}}
           .signal{{font-size:24px;font-weight:bold;padding:12px;border-radius:10px;margin:10px auto;max-width:400px}}
        </style>
    </head>
    <body>
        <h2>AAKAR LIVE - 9:25 & 9:35 FORMULA</h2>
        <p style="color:#94a3b8">{now} | LTP: {data['LTP']:.2f}</p>

        <div class="signal" style="background:{'#22c55e33' if 'BUY' in data['SIGNAL'] else '#ef444433' if 'SELL' in data['SIGNAL'] else '#334155'}">
            {data['SIGNAL']}
        </div>

        <div class="box">
            <h3 style="margin:5px">📍 9:25 Candle (Opening Range)</h3>
            <div class="levels">
                <div class="buy">9:25 HIGH<br><b>{data['925_H']:.2f}</b></div>
                <div class="sell">9:25 LOW<br><b>{data['925_L']:.2f}</b></div>
            </div>
        </div>

        <div class="box" style="border:2px solid #facc15">
            <h3 style="margin:5px;color:#facc15">⭐ 9:35 Candle (Main Formula)</h3>
            <div class="levels">
                <div class="buy">9:35 HIGH<br><b>{data['935_H']:.2f}</b></div>
                <div class="sell">9:35 LOW<br><b>{data['935_L']:.2f}</b></div>
            </div>
            <p style="color:#94a3b8;font-size:13px;margin-top:10px">FORMULA: LTP > 9:35 HIGH = BUY | LTP < 9:35 LOW = SELL</p>
        </div>

        <div id="tv"></div>
        <script src="https://s3.tradingview.com/tv.js"></script>
        <script>
            new TradingView.widget({{
              "autosize": true, "height": 550, "symbol": "NSE:NIFTY",
              "interval": "5", "timezone": "Asia/Kolkata", "theme": "dark",
              "style": "1", "locale": "in", "container_id": "tv",
              "drawings_access": {{"type": "black", "tools": [{{"name": "Horizontal Line"}}]}},
            }});
        </script>
        <script>setTimeout(()=>location.reload(),15000);</script>
        <p style="color:#64748b">Har 15 sec me LIVE update hoga. Subah 9:35 ke baad levels fix ho jayenge.</p>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
