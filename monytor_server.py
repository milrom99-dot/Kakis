
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT", "XRPUSDT"]
thresholds = {
    "BTCUSDT": 0.7,
    "ETHUSDT": 1.0,
    "SOLUSDT": 1.2,
    "LINKUSDT": 1.2,
    "XRPUSDT": 1.2,
}
sent_alerts = {}

def fetch_klines(symbol):
    try:
        url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval=30&limit=3"
        resp = requests.get(url)
        data = resp.json()
        return data["result"]["list"]
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print(f"Error sending message: {e}")

def analyze_and_alert(symbol):
    klines = fetch_klines(symbol)
    if not klines or len(klines) < 3:
        return

    highs = [float(x[2]) for x in klines[-3:-1]]
    lows = [float(x[3]) for x in klines[-3:-1]]
    last_price = float(klines[-1][4])

    high = max(highs)
    low = min(lows)
    direction = "вверх" if last_price > high else "вниз" if last_price < low else "в бок"
    range_pct = (high - low) / low * 100

    print(f"{symbol}: high={high}, low={low}, price={last_price}, range={range_pct:.2f}%")

    if range_pct >= thresholds.get(symbol, 1.0):
        alert_id = f"{symbol}_{round(high, 2)}_{round(low, 2)}"
        if sent_alerts.get(symbol) == alert_id:
            print(f"{symbol}: уже отправлено.")
            return

        sent_alerts[symbol] = alert_id
        name = symbol.replace("USDT", "")
        msg = f"{name}
Цена: {last_price:.2f}
Диапазон: {range_pct:.2f}% за 2×30м
Движение: {direction}"
        print("Sending:", msg)
        send_telegram(msg)

def main():
    for symbol in symbols:
        analyze_and_alert(symbol)

if __name__ == "__main__":
    main()
