import requests, time, datetime

# Замените на свои значения или используйте dotenv для безопасности
TOKEN = 'ВАШ_ТОКЕН'
CHAT_ID = 'ВАШ_CHAT_ID'

# Пороговые значения по умолчанию (можно расширить)
THRESHOLDS = {
    'BTCUSDT': 1.0,
    'ETHUSDT': 1.0,
    'SOLUSDT': 1.0
}

def load_coins():
    try:
        with open("coins.txt", "r") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        print("Файл coins.txt не найден. Создан пустой шаблон.")
        with open("coins.txt", "w") as f:
            f.write("BTCUSDT\nETHUSDT\nSOLUSDT\n")
        return ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={'chat_id': CHAT_ID, 'text': text})
        r.raise_for_status()
    except Exception as e:
        print("Ошибка отправки:", e)

def check_prices():
    coins = load_coins()
    for symbol in coins:
        url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}"
        try:
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()
            change = float(data['priceChangePercent'])
            price = float(data['lastPrice'])
            emoji = "🔺" if change > 0 else "🔻"
            if abs(change) >= THRESHOLDS.get(symbol, 1.0):
                msg = f"{emoji} {symbol.replace('USDT','').lower()} {price:.2f} ({change:+.2f}%)"
                send_message(msg)
        except Exception as e:
            print(f"Ошибка для {symbol}:", e)

def main():
    while True:
        print(f"[{datetime.datetime.now()}] Проверка...")
        check_prices()
        time.sleep(900)  # 15 минут

if __name__ == '__main__':
    main()