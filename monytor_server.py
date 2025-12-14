import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "XRPUSDT"]
bybit_url = "https://api.bybit.com/v5/market/kline"

def get_change(symbol):
    try:
        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": "30",
            "limit": "2"
        }
        resp = requests.get(bybit_url, params=params)
        data = resp.json()
        if data["retCode"] != 0:
            print(f"Bybit error: {data.get('retMsg')}")
            return None

        klines = data["result"]["list"]
        if len(klines) < 2:
            return None

        open_price = float(klines[0][1])
        close_price = float(klines[1][4])
        change_pct = (close_price - open_price) / open_price * 100
        return round(change_pct, 2)
    except Exception as e:
        print(f"Error for {symbol}: {e}")
        return None

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print(f"Telegram error: {e}")

for sym in symbols:
    change = get_change(sym)
    if change is not None and abs(change) >= 1:
        arrow = "🔻" if change < 0 else "🔺"
        coin = sym.replace("USDT", "")
        msg = f"{coin} {arrow} {abs(change):.2f}% за последние 2×30мин"
        print(msg)
        send_telegram(msg)
