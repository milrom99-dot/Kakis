import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Монеты и пороги
SYMBOLS = {
    "BTCUSDT": 0.5,
    "ETHUSDT": 1.0,
    "SOLUSDT": 1.0,
    "LINKUSDT": 1.0,
    "XRPUSDT": 1.0,
}

BYBIT_KLINE_URL = "https://api.bybit.com/v5/market/kline"


def get_last_two_closed_30m(symbol):
    """
    Берём 3 свечи, используем 2 ЗАКРЫТЫЕ (предыдущие)
    """
    try:
        r = requests.get(
            BYBIT_KLINE_URL,
            params={
                "category": "linear",
                "symbol": symbol,
                "interval": "30",
                "limit": 3,
            },
            timeout=10
        )
        data = r.json()

        if data.get("retCode") != 0:
            print(f"{symbol}: API error {data}")
            return None

        candles = data["result"]["list"]
        if len(candles) < 3:
            return None

        # две закрытые свечи
        return candles[-3], candles[-2]

    except Exception as e:
        print(f"{symbol}: request error {e}")
        return None


def send_telegram(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")


for symbol, threshold in SYMBOLS.items():
    candles = get_last_two_closed_30m(symbol)
    if not candles:
        continue

    c1, c2 = candles

    try:
        # ВАЖНО: правильные индексы Bybit v5
        high1 = float(c1[2])
        low1 = float(c1[3])
        high2 = float(c2[2])
        low2 = float(c2[3])
        close_price = float(c2[4])

        # ✅ ПРАВИЛЬНО
        high = max(high1, high2)
        low = min(low1, low2)

        if high <= low:
            print(f"{symbol}: invalid high/low, skip")
            continue

        range_pct = (high - low) / low * 100

        print(
            f"{symbol}: high={high}, low={low}, "
            f"price={close_price}, range={range_pct:.2f}%"
        )

        if range_pct >= threshold:
            coin = symbol.replace("USDT", "")
            msg = (
                f"{coin}\n"
                f"Цена: {close_price:.2f}\n"
                f"Диапазон: {range_pct:.2f}% за 2×30м"
            )
            print("Sending:", msg)
            send_telegram(msg)

    except Exception as e:
        print(f"{symbol}: calc error {e}")
