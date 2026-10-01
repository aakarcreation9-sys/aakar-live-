from flask import Flask
import yfinance as yf
import datetime
import pytz

app = Flask(__name__)

def get_orb_levels():
    try:
        ticker = yf.Ticker("^NSEI")
        df = ticker.history(period="1d", interval="5m")
        if df.empty or len(df) < 4:
            return None
        df.index = df.index.tz_convert('Asia/Kolkata') if df.index.tz is not None else df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
        candle_925 = None
        candle_935 = None
        live_price = float(df['Close'].iloc[-1])
        for idx, row in df.iterrows():
            t = idx.strftime("%H:%M")
            if t == "09:25": candle_925 = {"HIGH": float(row['High']), "LOW": float(row['Low'])}
            if t == "09:30" or t == "09:35":
                if not candle_935: candle_935 = {"HIGH": float(row['High']), "LOW": float(row['Low'])}
        if not candle_925: candle_925 = {"HIGH": float(df['High'][:2].max()), "LOW": float(df['Low'][:2].min())}
        if not candle_935: candle_935 = {"HIGH": float(df['High'][:3].max()), "LOW": float(df['Low'][:3].min())}
        
        signal = "WAIT"
        if live_price > candle_935["HIGH"]: signal = "BUY BREAKOUT 🚀"
        elif live_price < candle_935["LOW"]: signal = "SELL BREAKDOWN 🔻"
        else: signal = "SIDEWAYS"
        return {"925_H": candle_925["HIGH"], "925_L": candle_925["LOW"], "935_H": candle_935["HIGH"], "935_L": candle_935["LOW"], "LTP": live_price, "SIGNAL": signal}
    except: return None

@app.route('/')
def home():
    data = get_orb_levels()
    now = datetime.datetime.now(datetime.timezone.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%d-%m-%Y %I:%M:%S %p")
    if not data:
        ohlc = "<p>Market 9:35 ke baad LIVE hoga</p>"
    else:
        col = "#22c55e" if "BUY" in data['SIGNAL'] else "#ef4444" if "SELL" in data['SIGNAL'] else "#64748b"
        ohlc = f"""
        <div style="background:{col}33;border:2px solid {col};padding:12px;border-radius:12px;max-width:500px;margin:10px auto;font-size:22px;font-weight:bold">{data['SIGNAL']} - LTP {data['LTP']:.2f}</div>
        <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;max-width:900px;margin:auto">
            <div style="background:#1e293b;padding:12px 20px;border-radius:10px;border:1px solid #facc15">9:25 H: <b>{data['925_H']:.2f}</b><br>9:25 L: <b>{data['925_L']:.2f}</b></div>
            <div style="background:#1e293b;padding:12px 20px;border-radius:10px;border:2px solid #facc15">9:35 H: <b style="color:#22c55e">{data['935_H']:.2f}</b><br>9:35 L: <b style="color:#ef4444">{data['935_L']:.2f}</b></div>
        </div>
        """

    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Aakar 9:25 9:35</title>
    <style>body{{background:#0f172a;color:white;font-family:Arial;text-align:center;padding:10px;margin:0}} .tv{{max-width:900px;height:600px;margin:15px auto}}</style></head>
    <body>
        <h3>AAKAR LIVE - 9:25 & 9:35 FORMULA</h3><p style="color:#94a3b8">{now}</p>{ohlc}
        <div class="tv" id="tradingview_chart"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script>
        new TradingView.widget({{
          "width": "100%", "height": 600,
          "symbol": "BSE:SENSEX",
          "interval": "5",
          "timezone": "Asia/Kolkata",
          "theme": "dark",
          "style": "1",
          "locale": "in",
          "toolbar_bg": "#1e293b",
          "enable_publishing": false,
          "allow_symbol_change": true,
          "container_id": "tradingview_chart"
        }});
        </script>
        <p style="color:#94a3b8;font-size:12px">Chart me upar search me NIFTY type karke NSE:NIFTY select kar sakta hai. 9:25/9:35 levels upar box me LIVE hai.</p>
        <script>setTimeout(()=>location.reload(),15000);</script>
    </body></html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
