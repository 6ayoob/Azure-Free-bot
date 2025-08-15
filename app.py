from flask import Flask
import threading
import time
import traceback
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, SYMBOLS, MAX_OPEN_POSITIONS
from strategy import check_signal, execute_buy, manage_position, load_position
import requests

# -----------------------------
# ⚡ إعداد Flask
# -----------------------------
app = Flask(__name__)

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})
    except Exception as e:
        print(f"[ERROR] Telegram error: {e}")

# -----------------------------
# 🔁 حلقة التداول الرئيسية
# -----------------------------
def trading_loop():
    send_telegram_message("🚀 البوت بدأ العمل | EMA9/EMA21 + RSI مع هدف واحد ووقف خسارة ✅")
    print("[INFO] Trading loop started")

    while True:
        try:
            open_positions_count = 0
            for symbol in SYMBOLS:
                if load_position(symbol):
                    open_positions_count += 1

            for symbol in SYMBOLS:
                position = load_position(symbol)
                print(f"[INFO] تحقق من {symbol}")

                if position is None:
                    if open_positions_count >= MAX_OPEN_POSITIONS:
                        print(f"[INFO] الحد الأقصى للصفقات المفتوحة وصل ({MAX_OPEN_POSITIONS})")
                        continue
                    signal = check_signal(symbol)
                    if signal == "buy":
                        order, message = execute_buy(symbol)
                        if message:
                            send_telegram_message(message)
                            print(f"[INFO] {message}")
                        if order:
                            open_positions_count += 1
                            print(f"[INFO] تم فتح صفقة {symbol}")
                else:
                    closed = manage_position(symbol)
                    if closed:
                        msg = f"صفقة {symbol} أُغلقت بناءً على هدف الربح أو وقف الخسارة."
                        send_telegram_message(msg)
                        print(f"[INFO] {msg}")
                        open_positions_count -= 1
        except Exception:
            err = traceback.format_exc()
            send_telegram_message(f"⚠️ خطأ في البوت:\n{err}")
            print(f"[ERROR] {err}")

        time.sleep(60)  # تحقق كل دقيقة

# -----------------------------
# 🌐 Routes
# -----------------------------
@app.route('/')
def index():
    return "بوت التداول يعمل 🚀"

# -----------------------------
# 🔹 Start loop in a separate thread
# -----------------------------
def start_trading_thread():
    thread = threading.Thread(target=trading_loop)
    thread.daemon = True
    thread.start()
    print("[INFO] Trading thread started")

# -----------------------------
# 🔹 تشغيل التطبيق
# -----------------------------
if __name__ == "__main__":
    start_trading_thread()
    app.run(host="0.0.0.0", port=8000)
