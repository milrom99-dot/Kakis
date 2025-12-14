
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "XRPUSDT"]
url = "https://api.bybit.com/v2/public/tickers"

def get_price_change(symbol):
    try:
        resp = requests.get(url)
        data = resp.json()
        if "result" not in data:
            print(f"Invalid response data structure for {symbol}: {data}")
            return None, None

        for item in data["result"]:
            if item["symbol"] == symbol:
                price = float(item["last_price"])
                change = float(item["percent_change_24h"])
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

thresholds = {
    "BTCUSDT": 0.5,
    "ETHUSDT": 1.0,
    "SOLUSDT": 1.0,
    "LINKUSDT": 1.0,
    "XRPUSDT": 1.0,
}

for sym in symbols:
    price, change = get_price_change(sym)
    if price is not None:
        threshold = thresholds.get(sym, 1.0)
        if abs(change) >= threshold:
            coin = sym.replace("USDT", "")
            arrow = "🔻" if change < 0 else "🔺"
            msg = f"{coin} ${price:.2f} {arrow} ({change:.2f}%)"
            print(msg)
            send_telegram(msg)
        else:
            print(f"{sym}: изменение {change:.2f}% ниже порога {threshold}%")
