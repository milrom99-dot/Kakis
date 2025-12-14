import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "XRPUSDT"]
url = "https://api.bybit.com/v5/market/kline"

# thresholds by coin
thresholds = {
    "BTC": 0.5,
    "ETH": 1,
    "SOL": 1,
    "LINK": 1,
    "XRP": 1
}

sent_cache = {}

def get_kline(symbol):
    try:
        resp = requests.get(url, params={
            "category": "linear",
            "symbol": symbol,
            "interval": "30",
            "limit": 3
        })
        data = resp.json()
        if "result" not in data or "list" not in data["result"]:
            print(f"Invalid response structure for {symbol}: {data}")
            return None
        return data["result"]["list"]
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
        print(f"Error sending telegram message: {e}")

def analyze(symbol):
    klines = get_kline(symbol)
    if not klines or len(klines) < 3:
        return

    # use the last two closed candles
    k1 = klines[-3]
    k2 = klines[-2]

    high = max(float(k1[2]), float(k2[2]))
    low = min(float(k1[3]), float(k2[3]))
    last_price = float(k2[4])

    range_percent = round(((high - low) / low) * 100, 2)

    name = symbol.replace("USDT", "")
    threshold = thresholds.get(name, 1)

    print(f"{symbol}: high={high}, low={low}, price={last_price}, range={range_percent}%")

    if range_percent >= threshold:
        # direction logic
        direction = "флэт"
        if float(k1[4]) > float(k1[1]) and float(k2[4]) > float(k2[1]):
            direction = "вверх"
        elif float(k1[4]) < float(k1[1]) and float(k2[4]) < float(k2[1]):
            direction = "вниз"

        msg = f"{name}: диапазон {range_percent}% за 2×30м свечи ({direction}), цена: {last_price}"

        # avoid duplicates
        last_sent = sent_cache.get(symbol)
        if last_sent != msg:
            print("Sending:", msg)
            send_telegram(msg)
            sent_cache[symbol] = msg

for s in symbols:
    analyze(s)
