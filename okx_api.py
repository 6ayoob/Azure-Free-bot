import hmac
import hashlib
import time
import requests
import json
from config import API_KEY, SECRET_KEY, PASSPHRASE

BASE_URL = "https://www.okx.com"

# ===============================
# 📌 دوال مساعدة لتوقيع الطلبات
# ===============================
def generate_signature(timestamp, method, request_path, body=""):
    message = timestamp + method.upper() + request_path + body
    mac = hmac.new(bytes(SECRET_KEY, 'utf-8'), bytes(message, 'utf-8'), hashlib.sha256)
    return mac.digest().hex()

def request_headers(method, request_path, body=""):
    timestamp = str(time.time())
    signature = generate_signature(timestamp, method, request_path, body)
    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }
    return headers

# ===============================
# 📊 بيانات السوق
# ===============================
def fetch_ohlcv(symbol, timeframe, limit=100):
    try:
        instId = symbol.replace("/", "-")
        url = f"{BASE_URL}/api/v5/market/history-candles?instId={instId}&bar={timeframe}&limit={limit}"
        response = requests.get(url)
        data = response.json()
        if "data" in data:
            return [[int(item[0]), float(item[1]), float(item[2]), float(item[3]), float(item[4]), float(item[5])] for item in data["data"]]
    except Exception as e:
        print(f"⚠️ خطأ في fetch_ohlcv: {e}")
    return []

def fetch_price(symbol):
    try:
        instId = symbol.replace("/", "-")
        url = f"{BASE_URL}/api/v5/market/ticker?instId={instId}"
        response = requests.get(url).json()
        return float(response["data"][0]["last"])
    except Exception as e:
        print(f"⚠️ خطأ في fetch_price: {e}")
        return 0

# ===============================
# 🛒 أوامر السوق
# ===============================
def place_market_order(symbol, side, amount):
    try:
        instId = symbol.replace("/", "-")
        url = f"{BASE_URL}/api/v5/trade/order"
        body = json.dumps({
            "instId": instId,
            "tdMode": "cash",
            "side": side,
            "ordType": "market",
            "sz": str(amount)
        })
        headers = request_headers("POST", "/api/v5/trade/order", body)
        response = requests.post(url, data=body, headers=headers)
        return response.json()
    except Exception as e:
        print(f"⚠️ خطأ في place_market_order: {e}")
        return None

# ===============================
# 💰 أرصدة الحساب
# ===============================
def fetch_balance(asset):
    try:
        url = f"{BASE_URL}/api/v5/account/balance?ccy={asset}"
        headers = request_headers("GET", f"/api/v5/account/balance?ccy={asset}")
        response = requests.get(url, headers=headers).json()
        if "data" in response and len(response["data"]) > 0:
            return float(response["data"][0]["details"][0]["eq"])
    except Exception as e:
        print(f"⚠️ خطأ في fetch_balance: {e}")
    return 0
