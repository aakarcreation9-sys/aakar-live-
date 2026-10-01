from flask import Flask
import yfinance as yf
import datetime
import json

app = Flask(__name__)

def get_chart_data(symbol="^NSEI"):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval="5m")
        if df.empty:
            return None, None

        # LIVE CANDLE FORMULA
        OPEN = float(df['Open'].iloc[0])
        HIGH = float(df['High'].max())
        LOW = float(df['Low'].min())
        CLOSE = float(df['Close'].iloc[-1])

        # Chart ke liye data banao
        chart_data = []
        for idx, row in df.iterrows():
            chart_data.append({
                "time": int(idx.timestamp()),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close'])
            })

        info = {"OPEN": OPEN, "HIGH": HIGH, "LOW": LOW, "CLOSE": CLOSE}
        return info, chart_data
    except Exception as e:
        print(e)
        return None, None

@app.route('/')
def home():
    info, candles = get_chart_data("^NSEI")
    if not info:
        return "<h1 style='color:white;background:#0f172a;text-align:center;padding:50px'>Market band hai - 9:15 AM ko LIVE hoga</h1>"

    candles_json = json.dumps(candles)
    now = datetime.datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    color = "#22c55e" if info['CLOSE'] > info['OPEN'] else "#ef4444"
    ctype = "GREEN 🟢" if info['CLOSE'] > info['OPEN'] else "RED 🔴"

    return f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Aakar Live Candle</title>
        <script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
        <style>
            body{{background:#0f172a;color:white;font-family:Arial;margin:0;padding:15px;text-align:center}}
          .info{{background:#1e293b;padding:15px;border-radius:12px;max-width:850px;margin:10px auto;display:flex;justify-content:space-around;flex-wrap:wrap;border:2px solid {color}}}
          .info div{{margin:5px 15px}}.info span{{color:#94a3b8;font-size:13px}}.info b{{display:block;font-size:18px;margin-top:4px}}
            #chart{{max-width:850px;height:500px;margin:20px auto;background:#1e293b;border-radius:12px}}
        </style>
    </head>
    <body>
        <h2>AAKAR LIVE - NIFTY 50 {ctype}</h2>
        <p style="color:#94a3b8">{now} | 5-Min LIVE Candle | Auto 10s</p>

        <div class="info">
            <div><span>OPEN (9:15)</span><b>{info['OPEN']:.2f}</b></div>
            <div><span style="color:#22c55e">HIGH</span><b style="color:#22c55e">{info['HIGH']:.2f}</b></div>
            <div><span style="color:#ef4444">LOW</span><b style="color:#ef4444">{info['LOW']:.2f}</b></div>
            <div><span>CLOSE (LTP)</span><b style="color:{color};font-size:22px">{info['CLOSE']:.2f}</b></div>
        </div>

        <div id="chart"></div>

        <script>
            const data = {candles_json};
            const chart = LightweightCharts.createChart(document.getElementById('chart'), {{
                layout: {{background: {{color: '#1e293b'}}, textColor: '#d1d5db'}},
                grid: {{vertLines: {{color: '#334155'}}, horzLines: {{color: '#334155'}}}},
                timeScale: {{timeVisible:true, secondsVisible:false}}
            }});
            const candleSeries = chart.addCandlestickSeries();
            candleSeries.setData(data);

            // ===== FORMULA LINES CHART PE =====
            // OPEN Line - Yellow
            const openLine = {{
                price: {info['OPEN']},
                color: '#facc15',
                lineWidth: 2,
                lineStyle: 2,
                axisLabelVisible: true,
                title: 'OPEN {info['OPEN']:.2f}'
            }};
            // HIGH Line - Green
            const highLine = {{
                price: {info['HIGH']},
                color: '#22c55e',
                lineWidth: 1,
                lineStyle: 1,
                axisLabelVisible: true,
                title: 'HIGH {info['HIGH']:.2f}'
            }};
            // LOW Line - Red
            const lowLine = {{
                price: {info['LOW']},
                color: '#ef4444',
                lineWidth: 1,
                lineStyle: 1,
                axisLabelVisible: true,
                title: 'LOW {info['LOW']:.2f}'
            }};

            candleSeries.createPriceLine(openLine);
            candleSeries.createPriceLine(highLine);
            candleSeries.createPriceLine(lowLine);

            chart.timeScale().fitContent();
        </script>
        <script>setTimeout(()=>location.reload(),10000);</script>
        <p style="color:#64748b;margin-top:20px">Yellow Dashed = OPEN Formula | Green = HIGH Formula | Red = LOW Formula</p>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
    """

Commit karte hi 2 min me teri link pe chart pe 3 lines aa jayengi:

- **Yellow Dotted Line = OPEN** (9:15 ka price)
- **Green Line = HIGH**
- **Red Line = LOW**

Ab dikhega toh screenshot bhejna!
