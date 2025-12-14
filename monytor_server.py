
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "XRPUSDT"]
url = "https://api.bybit.com/v5/market/kline"

thresholds = {
    "BTCUSDT": 0.5,
    "ETHUSDT": 1.0,
    "SOLUSDT": 1.0,
    "LINKUSDT": 1.0,
    "XRPUSDT": 1.0,
}

def get_last_two_closed_30m_candles(symbol):
    try:
        resp = requests.get(url, params={
            "category": "linear",
            "symbol": symbol,
            "interval": "30",
            "limit": 3  # берём 3, чтобы гарантированно были 2 закрытые
        })
        data = resp.json()
        if "result" not in data or "list" not in data["result"]:
            print(f"Invalid kline data for {symbol}: {data}")
            return None, None

        candles = data["result"]["list"]
        # Берём 2 предыдущие свечи (не последнюю текущую)
        prev1 = float(candles[-3][1])  # open
        prev2 = float(candles[-2][4])  # close
        return prev1, prev2

    except Exception as e:
        print(f"Error fetching candles for {symbol}: {e}")
        return None, None

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print(f"Telegram error: {e}")

messages = []
for symbol in symbols:
    open_price, close_price = get_last_two_closed_30m_candles(symbol)
    if open_price is not None and close_price is not None:
        change = ((close_price - open_price) / open_price) * 100
        if abs(change) >= thresholds[symbol]:
            emoji = "🔺" if change > 0 else "🔻"
            messages.append(f"{symbol[:-4]} ${close_price:.2f} ({emoji} {change:.2f}%)")
        else:
            print(f"{symbol}: change {change:.2f}% < threshold")
    else:
        print(f"{symbol}: unable to compute change")

if messages:
    send_telegram("\n".join(messages))
