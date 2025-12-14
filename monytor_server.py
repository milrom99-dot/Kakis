import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import time

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "XRPUSDT"]
url = "https://api.bybit.com/v5/market/kline"

thresholds = {
    "BTCUSDT": 0.7,
    "ETHUSDT": 1.0,
    "SOLUSDT": 1.2,
    "LINKUSDT": 1.2,
    "XRPUSDT": 1.2,
}

def get_last_2x30m_klines(symbol):
    try:
        resp = requests.get(url, params={"category": "linear", "symbol": symbol, "interval": "30", "limit": 3})
        data = resp.json()
        if "result" not in data or "list" not in data["result"]:
            print(f"Invalid response for {symbol}: {data}")
            return None
        klines = data["result"]["list"]
        return klines[-3:-1]  # последние 2 закрытые свечи
    except Exception as e:
        print(f"Error fetching klines for {symbol}: {e}")
        return None

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print(f"Telegram error: {e}")

for symbol in symbols:
    klines = get_last_2x30m_klines(symbol)
    if not klines or len(klines) < 2:
        continue

    # Преобразуем строки в числа
    highs = [float(k[3]) for k in klines]
    lows = [float(k[4]) for k in klines]
    closes = [float(k[4]) for k in klines]  # close = low (или k[5] - close)

    high = max(highs)
    low = min(lows)
    price = closes[-1]  # close последней свечи
    range_percent = (high - low) / low * 100

    print(f"{symbol}: high={high}, low={low}, price={price}, range={range_percent:.2f}%")

    if range_percent >= thresholds[symbol]:
        message = f"{symbol.replace('USDT','')}: цена ${price:.2f}, диапазон {range_percent:.2f}% за 2x30м свечи"
        print("Sending:", message)
        send_telegram(message)
