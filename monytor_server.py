import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "XRPUSDT"]
thresholds = {
    "BTCUSDT": 0.5,
    "ETHUSDT": 1.0,
    "SOLUSDT": 1.0,
    "LINKUSDT": 1.0,
    "XRPUSDT": 1.0,
}

def get_klines(symbol):
    url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval=30&limit=3"
    try:
        resp = requests.get(url)
        data = resp.json()
        return data.get("result", {}).get("list", [])
    except Exception as e:
        print(f"Error fetching klines for {symbol}: {e}")
        return []

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print(f"Telegram error: {e}")

for symbol in symbols:
    klines = get_klines(symbol)
    if len(klines) >= 3:
        k1 = klines[-3]
        k2 = klines[-2]
        high = max(float(k1[2]), float(k2[2]))
        low = min(float(k1[3]), float(k2[3]))
        change = (high - low) / low * 100
        threshold = thresholds.get(symbol, 1.0)
        if change >= threshold:
            coin = symbol.replace("USDT", "")
            msg = f"{coin}: диапазон {change:.2f}% за 2x30м свечи"
            print("Sending:", msg)
            send_telegram(msg)
        else:
            print(f"{symbol}: change {change:.2f}% < threshold")
    else:
        print(f"Not enough kline data for {symbol}")
