from flask import Flask, request
import yfinance as yf
import datetime, pytz, json

app = Flask(__name__)
SYMBOLS = {"NIFTY": "^NSEI", "SENSEX": "^BSESN"}

def get_data(sym_key):
    try:
        ticker = yf.Ticker(SYMBOLS[sym_key])
        df = ticker.history(period="1d", interval="5m")
        if df.empty or len(df) < 4: return None, None, None
        df.index = df.index.tz_convert('Asia/Kolkata') if df.index.tz is not None else df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
        
        candles = []
        for idx, row in df.iterrows():
            candles.append({"time": int(idx.timestamp()), "open": float(row['Open']), "high": float(row['High']), "low": float(row['Low']), "close": float(row['Close'])})
        
        h935 = l935 = None
        for idx, row in df.iterrows():
            t = idx.strftime("%H:%M")
            if t in ["09:30", "09:35"]:
                if h935 is None:
                    h935, l935 = float(row['High']), float(row['Low'])
                else:
                    h935 = max(h935, float(row['High']))
                    l935 = min(l935, float(row['Low']))
        if h935 is None:
            h935 = float(df['High'][2:4].max())
            l935 = float(df['Low'][2:4].min())

        ltp = float(df['Close'].iloc[-1])
        signal = "WAIT FOR BREAKOUT"
        if ltp > h935: signal = "BUY BREAKOUT 🚀"
        elif ltp < l935: signal = "SELL BREAKDOWN 🔻"
        
        # ARROW MARKERS LOGIC
        markers = []
        for c in candles:
            if c['close'] > h935:
                markers.append({"time": c['time'], "position": "belowBar", "color": "#22c55e", "shape": "arrowUp", "text": "BUY BREAKOUT"})
            elif c['close'] < l935:
                markers.append({"time": c['time'], "position": "aboveBar", "color": "#ef4444", "shape": "arrowDown", "text": "SELL BREAKDOWN"})
        
        # Sirf last 2 arrow dikhana hai taaki chart clean rahe
        markers = markers[-6:] 

        return {"H": h935, "L": l935, "LTP": ltp, "SIGNAL": signal}, candles, markers
    except: return None, None, None

@app.route('/')
def home():
    sym = request.args.get("s", "NIFTY")
    if sym not in SYMBOLS: sym = "NIFTY"
    info, candles, markers = get_data(sym)
    now = datetime.datetime.now(datetime.timezone.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%d-%m-%Y %I:%M %p")
    if not info: return f"<body style='background:#0f172a;color:white;text-align:center;padding:50px'><h2>{sym} 9:40 ke baad LIVE hoga</h2><script>setTimeout(()=>location.reload(),20000)</script></body>"
    return f"""
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aakar {sym} Arrow Signal</title>
<script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
<style>body{{background:#0f172a;color:white;font-family:Arial;text-align:center;margin:0;padding:10px}}.btn{{padding:12px 25px;margin:5px;border-radius:10px;border:none;font-weight:bold;cursor:pointer}}.active{{background:#facc15;color:black}}.inactive{{background:#1e293b;color:white;border:1px solid #475569}}#chart{{width:100%;max-width:900px;height:620px;margin:15px auto;background:#1e293b;border-radius:12px}}</style>
</head><body>
<h2>AAKAR LIVE - {sym} - STRONG BREAKOUT</h2>
<div><button class="btn {'active' if sym=='NIFTY' else 'inactive'}" onclick="location.href='/?s=NIFTY'">NIFTY</button><button class="btn {'active' if sym=='SENSEX' else 'inactive'}" onclick="location.href='/?s=SENSEX'">SENSEX</button></div>
<p style="color:#94a3b8">{now} | LTP {info['LTP']:.2f}</p>
<div style="font-size:26px;font-weight:bold;padding:12px;border-radius:12px;max-width:500px;margin:10px auto;background:{'#22c55e33' if 'BUY' in info['SIGNAL'] else '#ef444433' if 'SELL' in info['SIGNAL'] else '#334155'};border:3px solid {'#22c55e' if 'BUY' in info['SIGNAL'] else '#ef4444' if 'SELL' in info['SIGNAL'] else '#475569'}">{info['SIGNAL']}</div>
<div style="display:flex;justify-content:center;gap:20px;font-size:18px"><div style="color:#22c55e">BUY ABOVE {info['H']:.0f} ⬆️</div><div style="color:#ef4444">SELL BELOW {info['L']:.0f} ⬇️</div></div>
<div id="chart"></div>
<script>
const data = {json.dumps(candles)};
const markers = {json.dumps(markers)};
const chart = LightweightCharts.createChart(document.getElementById('chart'),{{layout:{{background:{{color:'#1e293b'}},textColor:'#d1d5db'}},grid:{{vertLines:{{color:'#2d3748'}},horzLines:{{color:'#2d3748'}}}},timeScale:{{timeVisible:true}}}});
const series = chart.addCandlestickSeries({{upColor:'#22c55e',downColor:'#ef4444',wickUpColor:'#22c55e',wickDownColor:'#ef4444'}});
series.setData(data);
series.setMarkers(markers);
series.createPriceLine({{price:{info['H']},color:'#22c55e',lineWidth:3,lineStyle:0,title:'STRONG RESISTANCE {info['H']:.0f}'}});
series.createPriceLine({{price:{info['L']},color:'#ef4444',lineWidth:3,lineStyle:0,title:'STRONG SUPPORT {info['L']:.0f}'}});
chart.timeScale().fitContent();
</script><script>setTimeout(()=>location.reload(),15000);</script>
</body></html>"""

if __name__ == '__main__': app.run(host='0.0.0.0', port=10000)
