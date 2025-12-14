import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
THRESHOLDS = {
    "BTCUSDT": 0.5,
    "ETHUSDT": 1.0,
    "SOLUSDT": 1.0,
    "LINKUSDT": 1.0,
    "XRPUSDT": 1.0,
}
symbols = list(THRESHOLDS.keys())
sent_flags = {}

def get_klines(symbol):
    url = f"https://api.bybit.com/v5/market/kline"
    params = {
        "category": "linear",
        "symbol": symbol,
        "interval": "30",
        "limit": 3
    }
    try:
        res = requests.get(url, params=params)
        data = res.json()
        return data["result"]["list"]
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
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
    name = symbol.replace("USDT", "")
    klines = get_klines(symbol)
    if len(klines) < 3:
        continue

    # берём две последние закрытые свечи
    k1 = klines[-3]
    k2 = klines[-2]
    high = max(float(k1[2]), float(k2[2]))
    low = min(float(k1[3]), float(k2[3]))
    price = float(klines[-1][4])
    direction = "вверх" if price > high else "вниз" if price < low else "флэт"
    range_pct = (high - low) / low * 100

    print(f"{symbol}: high={high}, low={low}, price={price}, range={range_pct:.2f}%")

    threshold = THRESHOLDS[symbol]
    msg_key = f"{symbol}_{direction}"

    if range_pct >= threshold and not sent_flags.get(msg_key):
        msg = f"{name}: диапазон {range_pct:.2f}% за 2x30м свечи ({direction}), цена: {price}"
        print("Sending:", msg)
        send_telegram(msg)
        sent_flags[msg_key] = True
