from flask import Flask
import threading, time, traceback
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, SYMBOLS, MAX_OPEN_POSITIONS
from strategy import check_signal, execute_buy, manage_position, load_position
import requests

app = Flask(__name__)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})
    except Exception as e:
        print(f"Telegram error: {e}")

def trading_loop():
    send_telegram_message("🚀 البوت بدأ العمل | EMA9/EMA21 + RSI مع هدف ووقف خسارة ✅")
    while True:
        try:
            open_positions_count = sum(1 for s in SYMBOLS if load_position(s))
            for symbol in SYMBOLS:
                position = load_position(symbol)
                if position is None:
                    if open_positions_count >= MAX_OPEN_POSITIONS:
                        continue
                    signal = check_signal(symbol)
                    if signal == "buy":
                        order, message = execute_buy(symbol)
                        if message:
                            send_telegram_message(message)
                        if order:
                            open_positions_count += 1
                else:
                    closed = manage_position(symbol)
                    if closed:
                        send_telegram_message(f"صفقة {symbol} أُغلقت بناءً على هدف أو وقف خسارة.")
                        open_positions_count -= 1
        except Exception:
            send_telegram_message(f"⚠️ خطأ في البوت:\n{traceback.format_exc()}")
        time.sleep(60)

@app.route('/')
def index():
    return "بوت التداول يعمل 🚀"

def start_trading_thread():
    thread = threading.Thread(target=trading_loop)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    start_trading_thread()
    app.run(host="0.0.0.0", port=8000)

