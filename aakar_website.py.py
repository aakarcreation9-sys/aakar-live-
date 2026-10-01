from flask import Flask, jsonify
from SmartApi import SmartConnect
import pyotp, threading, time, datetime, os
API_KEY="ZnpCcXHa"; CLIENT_ID="AABS241306"; PASSWORD="9783"; TOTP_SECRET="DL562FMHIM6CJLUSOCEWCKK3LQ"
app=Flask(__name__)
obj=SmartConnect(api_key=API_KEY)
obj.generateSession(CLIENT_ID,PASSWORD,pyotp.TOTP(TOTP_SECRET).now())
live_data={"NIFTY":{"price":0,"upper":0,"bottom":0,"signal":"WAIT"},"SENSEX":{"price":0,"upper":0,"bottom":0,"signal":"WAIT"}}
TOKENS={"NIFTY":("NSE","99926000"),"SENSEX":("BSE","99919000")}
def get_hist(token,exch):
    try:
        today=datetime.date.today()
        p={"exchange":exch,"symboltoken":token,"interval":"FIVE_MINUTE","fromdate":f"{today} 09:15","todate":f"{today} 15:30"}
        d=obj.getCandleData(p)
        return d['data'] if d and 'data' in d else []
    except: return []
def get_levels(hist):
    c925=None; c935=None
    for c in hist:
        if "T09:20:00" in c[0]: c925=c
        if "T09:30:00" in c[0]: c935=c
    if c925 and c935: return max(c925[2],c935[2]), min(c925[3],c935[3])
    return 0,0
def live_loop():
    last_date=None
    while True:
        today = datetime.date.today()
        now = datetime.datetime.now()
        # Roz 9:41 pe naya level
        if last_date!= today and now.hour==9 and now.minute>=41:
            for sym in TOKENS:
                exch,tok=TOKENS[sym]; hist=get_hist(tok,exch); u,b=get_levels(hist)
                if u: live_data[sym]["upper"]=u; live_data[sym]["bottom"]=b
            last_date=today
        # Pehli baar start hote hi bhi level le le
        if live_data["NIFTY"]["upper"]==0:
            for sym in TOKENS:
                exch,tok=TOKENS[sym]; hist=get_hist(tok,exch); u,b=get_levels(hist)
                if u: live_data[sym]["upper"]=u; live_data[sym]["bottom"]=b
        for sym in TOKENS:
            exch,tok=TOKENS[sym]
            try:
                ltp=obj.ltpData(exch,sym,tok)['data']['ltp']
                u=live_data[sym]["upper"]; b=live_data[sym]["bottom"]; sig=f"WAIT ({ltp})"
                if u and b:
                    if ltp>u: sig=f"🚀 {sym} CALL BUY @ {ltp}"
                    elif ltp<b: sig=f"🔻 {sym} PUT BUY @ {ltp}"
                live_data[sym].update({"price":ltp,"signal":sig})
            except: pass
        time.sleep(2)
threading.Thread(target=live_loop,daemon=True).start()

@app.route('/')
def home():
    return """<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
<style>body{background:#0a0a0a;color:white;font-family:Arial;text-align:center;padding:10px}
.card{background:#1e1e1e;border-radius:15px;padding:12px;margin:8px;display:inline-block;min-width:280px;border:2px solid #333}
.price{font-size:32px;color:#00ff88;font-weight:bold}.call{background:#00c853;padding:14px;border-radius:10px;font-weight:bold;animation:blink 1s infinite}.put{background:#d50000;padding:14px;border-radius:10px;font-weight:bold;animation:blink 1s infinite}.wait{background:#333;padding:12px;border-radius:8px}
@keyframes blink{50%{opacity:0.5}}.chartbox{width:95%;max-width:700px;height:400px;margin:15px auto;background:#111;border-radius:12px;border:1px solid #444}
</style></head><body><h1>🔥 Aakar - Live Daily (Auto 9:41)</h1>
<div><div class="card"><h2>NIFTY 50</h2><div class="price" id="n_price">-</div><div>UPPER <b id="n_upper">-</b> | BOTTOM <b id="n_bottom">-</b></div><div id="n_sig" class="wait">Loading...</div></div>
<div class="card"><h2>SENSEX</h2><div class="price" id="s_price">-</div><div>UPPER <b id="s_upper">-</b> | BOTTOM <b id="s_bottom">-</b></div><div id="s_sig" class="wait">Loading...</div></div></div>
<div id="nifty_chart" class="chartbox"></div><div id="sensex_chart" class="chartbox"></div>
<script>
let nChart=LightweightCharts.createChart(document.getElementById('nifty_chart'),{layout:{background:{color:'#111111'},textColor:'#fff'},grid:{vertLines:{visible:false},horzLines:{visible:false}},crosshair:{vertLine:{visible:false},horzLine:{visible:false}},width:document.getElementById('nifty_chart').clientWidth,height:400});
let nSeries=nChart.addCandlestickSeries(); let nU=nChart.addLineSeries({color:'#00aaff',lineWidth:2}); let nB=nChart.addLineSeries({color:'#ffaa00',lineWidth:2});
let sChart=LightweightCharts.createChart(document.getElementById('sensex_chart'),{layout:{background:{color:'#111111'},textColor:'#fff'},grid:{vertLines:{visible:false},horzLines:{visible:false}},crosshair:{vertLine:{visible:false},horzLine:{visible:false}},width:document.getElementById('sensex_chart').clientWidth,height:400});
let sSeries=sChart.addCandlestickSeries(); let sU=sChart.addLineSeries({color:'#00aaff',lineWidth:2}); let sB=sChart.addLineSeries({color:'#ffaa00',lineWidth:2});
async function loadHist(){let r=await fetch('/history/NIFTY');let d=await r.json();nSeries.setData(d.candles);nU.setData(d.upperLine);nB.setData(d.bottomLine);let r2=await fetch('/history/SENSEX');let d2=await r2.json();sSeries.setData(d2.candles);sU.setData(d2.upperLine);sB.setData(d2.bottomLine);}
loadHist();
async function loadLive(){let r=await fetch('/data');let j=await r.json();document.getElementById('n_price').innerText=j.NIFTY.price;document.getElementById('n_upper').innerText=j.NIFTY.upper;document.getElementById('n_bottom').innerText=j.NIFTY.bottom;let ns=document.getElementById('n_sig');ns.innerText=j.NIFTY.signal;ns.className=j.NIFTY.signal.includes('CALL')?'call':j.NIFTY.signal.includes('PUT')?'put':'wait';document.getElementById('s_price').innerText=j.SENSEX.price;document.getElementById('s_upper').innerText=j.SENSEX.upper;document.getElementById('s_bottom').innerText=j.SENSEX.bottom;let ss=document.getElementById('s_sig');ss.innerText=j.SENSEX.signal;ss.className=j.SENSEX.signal.includes('CALL')?'call':j.SENSEX.signal.includes('PUT')?'put':'wait';}
setInterval(loadLive,1000);loadLive();setInterval(loadHist,60000);
</script></body></html>"""
@app.route('/data')
def data(): return jsonify(live_data)
@app.route('/history/<sym>')
def history(sym):
    sym=sym.upper(); exch,tok=TOKENS[sym]; hist=get_hist(tok,exch); candles=[]
    for c in hist:
        try: ts=int(datetime.datetime.fromisoformat(c[0]).timestamp()); candles.append({"time":ts,"open":c[1],"high":c[2],"low":c[3],"close":c[4]})
        except: pass
    u=live_data[sym]["upper"]; b=live_data[sym]["bottom"]; uL=[]; bL=[]
    if candles and u:
        for k in candles: uL.append({"time":k["time"],"value":u}); bL.append({"time":k["time"],"value":b})
    return jsonify({"candles":candles,"upperLine":uL,"bottomLine":bL})

if __name__=='__main__':
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)