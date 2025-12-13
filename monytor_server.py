import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "XRPUSDT"]

URL = "https://fapi.binance.com/fapi/v1/ticker/24hr"


def get_price_change(symbol):
    try:
        r = requests.get(URL, params={"symbol": symbol}, timeout=10)
        r.raise_for_status()
        data = r.json()

        price = float(data["lastPrice"])
        change = float(data["priceChangePercent"])
        return price, change

    except Exception as e:
        print(f"Error for {symbol}: {e}")
        return None, None


def send_telegram(msg):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram ENV not set")
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")


for sym in symbols:
    price, change = get_price_change(sym)

    if price is not None:
        coin = sym.replace("USDT", "")
        arrow = "🔻" if change < 0 else "🔺"
        msg = f"{coin} {price:.2f} ({arrow} {change:.2f}%)"

        print(msg)
        send_telegram(msg)
