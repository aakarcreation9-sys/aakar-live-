from flask import Flask
import yfinance as yf
import datetime, pytz, json

app = Flask(__name__)

def get_data():
    try:
        ticker = yf.Ticker("^NSEI")
        df = ticker.history(period="1d", interval="5m")
        if df.empty or len(df) < 3:
            return None, None
        df.index = df.index.tz_convert('Asia/Kolkata') if df.index.tz is not None else df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
        
        candles = []
        for idx, row in df.iterrows():
            candles.append({
                "time": int(idx.timestamp()),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close'])
            })

        # 9:25 aur 9:35 levels
        h925 = l925 = h935 = l935 = None
        for idx, row in df.iterrows():
            t = idx.strftime("%H:%M")
            if t == "09:25": h925, l925 = float(row['High']), float(row['Low'])
            if t == "09:30" or t == "09:35":
                if h935 is None: h935, l935 = float(row['High']), float(row['Low'])

        if h925 is None: h925, l925 = float(df['High'][:2].max()), float(df['Low'][:2].min())
        if h935 is None: h935, l935 = float(df['High'][2:4].max()), float(df['Low'][2:4].min())

        ltp = float(df['Close'].iloc[-1])
        signal = "SIDEWAYS"
        if ltp > h935: signal = "BUY BREAKOUT 🚀"
        elif ltp < l935: signal = "SELL BREAKDOWN 🔻"

        info = {"925_H": h925, "925_L": l925, "935_H": h935, "935_L": l935, "LTP": ltp, "SIGNAL": signal}
        return info, candles
    except Exception as e:
        print(e)
        return None, None

@app.route('/')
def home():
    info, candles = get_data()
    now = datetime.datetime.now(datetime.timezone.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%d-%m-%Y %I:%M:%S %p")

    if not info:
        return f"<body style='background:#0f172a;color:white;text-align:center;padding:50px'><h1>Market 9:30 ke baad LIVE hoga</h1><p>{now}</p><script>setTimeout(()=>location.reload(),30000)</script></body>"

    candles_json = json.dumps(candles)

    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Aakar 9:25 9:35</title>
    <script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        body{{background:#0f172a;color:white;font-family:Arial;text-align:center;margin:0;padding:10px}}
        .box{{background:#1e293b;padding:10px;border-radius:12px;max-width:900px;margin:10px auto;display:flex;justify-content:space-around;flex-wrap:wrap}}
        .sig{{font-size:22px;font-weight:bold;padding:10px;border-radius:10px;max-width:400px;margin:10px auto}}
        #chart{{width:100%;max-width:900px;height:500px;margin:15px auto;background:#1e293b;border-radius:12px}}
    </style></head>
    <body>
        <h3>AAKAR LIVE - 9:25 & 9:35 FORMULA (NO TradingView)</h3>
        <p style="color:#94a3b8">{now} | LTP {info['LTP']:.2f}</p>
        <div class="sig" style="background:{'#22c55e33' if 'BUY' in info['SIGNAL'] else '#ef444433' if 'SELL' in info['SIGNAL'] else '#334155'};border:2px solid {'#22c55e' if 'BUY' in info['SIGNAL'] else '#ef4444' if 'SELL' in info['SIGNAL'] else '#475569'}">{info['SIGNAL']}</div>
        <div class="box">
            <div>9:25 HIGH <b style="color:#facc15">{info['925_H']:.2f}</b></div>
            <div>9:25 LOW <b style="color:#facc15">{info['925_L']:.2f}</b></div>
            <div>9:35 HIGH <b style="color:#22c55e">{info['935_H']:.2f}</b></div>
            <div>9:35 LOW <b style="color:#ef4444">{info['935_L']:.2f}</b></div>
        </div>
        <div id="chart"></div>
        <script>
            const data = {candles_json};
            const chart = LightweightCharts.createChart(document.getElementById('chart'), {{
                layout: {{background: {{color:'#1e293b'}}, textColor:'#d1d5db'}},
                grid: {{vertLines:{{color:'#334155'}}, horzLines:{{color:'#334155'}}}},
                timeScale: {{timeVisible:true}}
            }});
            const series = chart.addCandlestickSeries();
            series.setData(data);
            series.createPriceLine({{price:{info['925_H']}, color:'#facc15', lineWidth:2, lineStyle:2, title:'9:25 HIGH'}});
            series.createPriceLine({{price:{info['925_L']}, color:'#facc15', lineWidth:2, lineStyle:2, title:'9:25 LOW'}});
            series.createPriceLine({{price:{info['935_H']}, color:'#22c55e', lineWidth:2, title:'9:35 HIGH'}});
            series.createPriceLine({{price:{info['935_L']}, color:'#ef4444', lineWidth:2, title:'9:35 LOW'}});
            chart.timeScale().fitContent();
        </script>
        <script>setTimeout(()=>location.reload(),15000);</script>
        <p style="color:#64748b;font-size:12px">Yellow = 9:25 Formula | Green/Red = 9:35 Formula | Har 15 sec LIVE</p>
    </body></html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
