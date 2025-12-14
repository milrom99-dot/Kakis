
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "XRPUSDT"]
price_change_thresholds = {
    "BTCUSDT": 0.5,  # BTC: 0.5%
    "ETHUSDT": 1.0,
    "SOLUSDT": 1.0,
    "LINKUSDT": 1.0,
    "XRPUSDT": 1.0
}

def get_current_price(symbol):
    try:
        url = f"https://api.bybit.com/v2/public/tickers?symbol={symbol}"
        resp = requests.get(url)
        data = resp.json()
        return float(data["result"][0]["last_price"])
    except Exception as e:
        print(f"Error (current) for {symbol}: {e}")
        return None

def get_open_price_1h(symbol):
    try:
        url = f"https://api.bybit.com/public/linear/kline?symbol={symbol}&interval=60&limit=1"
        resp = requests.get(url)
        data = resp.json()
        return float(data["result"][0]["open"])
    except Exception as e:
        print(f"Error (1h open) for {symbol}: {e}")
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
    last = get_current_price(sym)
    open_1h = get_open_price_1h(sym)
    if last and open_1h:
        change = ((last - open_1h) / open_1h) * 100
        threshold = price_change_thresholds.get(sym, 1.0)
        if abs(change) >= threshold:
            coin = sym.replace("USDT", "")
            arrow = "🔻" if change < 0 else "🔺"
            msg = f"{arrow} {coin} {last:.2f} ({change:+.2f}%) — за 1 час"
            print(msg)
            send_telegram(msg)
