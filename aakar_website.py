from flask import Flask, request
import yfinance as yf
import datetime, pytz, json
app = Flask(__name__)

SYMBOLS = {"NIFTY": "^NSEI", "SENSEX": "^BSESN"}

def get_data(symbol_key):
    try:
        ticker = yf.Ticker(SYMBOLS[symbol_key])
        df = ticker.history(period="1d", interval="5m")
        if df.empty or len(df) < 3: return None, None
        df.index = df.index.tz_convert('Asia/Kolkata') if df.index.tz is not None else df.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
        candles = []
        for idx, row in df.iterrows():
            candles.append({"time": int(idx.timestamp()),"open": float(row['Open']),"high": float(row['High']),"low": float(row['Low']),"close": float(row['Close'])})
        
        h935 = l935 = None
        h925 = l925 = 0
        for idx, row in df.iterrows():
            t = idx.strftime("%H:%M")
            if t == "09:25": h925, l925 = float(row['High']), float(row['Low'])
            if t == "09:30" or t == "09:35":
                if h935 is None: h935, l935 = float(row['High']), float(row['Low'])

        if h925 == 0: h925, l925 = float(df['High'][:2].max()), float(df['Low'][:2].min())
        if h935 is None: h935, l935 = float(df['High'][2:4].max()), float(df['Low'][2:4].min())

        ltp = float(df['Close'].iloc[-1])
        signal = "SIDEWAYS"
        if ltp > h935: signal = "BUY BREAKOUT 🚀"
        elif ltp < l935: signal = "SELL BREAKDOWN 🔻"
        return {"925_H": h925, "925_L": l925, "935_H": h935, "935_L": l935, "LTP": ltp, "SIGNAL": signal}, candles
    except: return None, None

@app.route('/')
def home():
    sym = request.args.get("s", "NIFTY")
    if sym not in SYMBOLS: sym = "NIFTY"
    info, candles = get_data(sym)
    now = datetime.datetime.now(datetime.timezone.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%d-%m-%Y %I:%M:%S %p")
    if not info: return f"<body style='background:#0f172a;color:white;text-align:center;padding:50px'><h1>{sym} 9:35 ke baad LIVE hoga</h1></body>"
    candles_json = json.dumps(candles)
    return f"""<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Aakar {sym} 9:35</title><script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script><style>body{{background:#0f172a;color:white;font-family:Arial;text-align:center;margin:0;padding:10px}}.btn{{padding:10px 22px;margin:5px;border-radius:8px;border:none;font-weight:bold;cursor:pointer}}.active{{background:#facc15;color:black}}.inactive{{background:#1e293b;color:white;border:1px solid #475569}}#chart{{width:100%;max-width:900px;height:550px;margin:15px auto;background:#1e293b;border-radius:12px}}</style></head><body><h3>AAKAR LIVE - {sym} - 9:35 FORMULA</h3><div><button class="btn {'active' if sym=='NIFTY' else 'inactive'}" onclick="location.href='/?s=NIFTY'">NIFTY</button><button class="btn {'active' if sym=='SENSEX' else 'inactive'}" onclick="location.href='/?s=SENSEX'">SENSEX</button></div><p style="color:#94a3b8">{now} | LTP {info['LTP']:.2f} | 9:25 H:{info['925_H']:.0f} L:{info['925_L']:.0f}</p><div style="font-size:24px;font-weight:bold;padding:12px;border-radius:10px;max-width:400px;margin:10px auto;background:{'#22c55e33' if 'BUY' in info['SIGNAL'] else '#ef444433' if 'SELL' in info['SIGNAL'] else '#334155'};border:2px solid {'#22c55e' if 'BUY' in info['SIGNAL'] else '#ef4444' if 'SELL' in info['SIGNAL'] else '#475569'}">{info['SIGNAL']} - 9:35 H:{info['935_H']:.0f} L:{info['935_L']:.0f}</div><div id="chart"></div><script>const data = {candles_json};const chart = LightweightCharts.createChart(document.getElementById('chart'),{{layout:{{background:{{color:'#1e293b'}},textColor:'#d1d5db'}},grid:{{vertLines:{{color:'#334155'}},horzLines:{{color:'#334155'}}}},timeScale:{{timeVisible:true}}}});const series = chart.addCandlestickSeries();series.setData(data);series.createPriceLine({{price:{info['935_H']},color:'#22c55e',lineWidth:2,title:'9:35 HIGH {info['935_H']:.0f}'}});series.createPriceLine({{price:{info['935_L']},color:'#ef4444',lineWidth:2,title:'9:35 LOW {info['935_L']:.0f}'}});chart.timeScale().fitContent();</script><script>setTimeout(()=>location.reload(),15000);</script></body></html>"""
if __name__ == '__main__': app.run(host='0.0.0.0', port=10000)
