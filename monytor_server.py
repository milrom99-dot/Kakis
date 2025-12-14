import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "XRPUSDT"]
url = "https://api.bybit.com/v5/market/tickers?category=linear"

def get_price_change(symbol):
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Error fetching data: {resp.status_code}")
            return None, None

        data = resp.json()
        if "result" not in data or "list" not in data["result"]:
            print(f"Invalid response format: {data}")
            return None, None

        for item in data["result"]["list"]:
            if item["symbol"] == symbol:
                price = float(item["lastPrice"])
                change = float(item["price24hPcnt"]) * 100  # from 0.0123 to 1.23%
                return price, change

        print(f"Symbol {symbol} not found in response.")
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
