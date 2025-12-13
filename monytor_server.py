
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "XRPUSDT"]
url = "https://api.binance.com/api/v3/ticker/24hr"

def get_price_change(symbol):
    try:
        resp = requests.get(f"{url}?symbol={symbol}")
        data = resp.json()

        if isinstance(data, dict) and "lastPrice" in data and "priceChangePercent" in data:
            price = float(data["lastPrice"])
            change = float(data["priceChangePercent"])
            return price, change
        else:
            print(f"Invalid response data structure for {symbol}: {data}")
            return None, None

    except Exception as e:
        print(f"Error for {symbol}: {e}")
        return None, None

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print(f"Telegram error: {e}")

for sym in symbols:
    price, change = get_price_change(sym)
    if price is not None:
        coin = sym.replace("USDT", "")
        arrow = "🔻" if change < 0 else "🔺"
        msg = f"{coin} ${price:.2f} ({arrow} {change:.2f}%)"
        print(msg)
        send_telegram(msg)
