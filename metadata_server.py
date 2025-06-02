from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import random
import time
import requests

app = Flask(__name__)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

USDT_CONTRACT = "0x1234567890abcdef1234567890abcdef12345678"
ETHERSCAN_API_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"
API_KEY = "your-secret-api-key"

SUPPORTED_WALLETS = ["Trust-Wallet", "MetaMask", "TokenPocket", "Coinbase Wallet", "TronLink"]

def validate_request():
    if not any(wallet in request.headers.get("User-Agent", "") for wallet in SUPPORTED_WALLETS):
        return False, jsonify({"error": "Access denied: Invalid wallet"}), 403
    if request.headers.get("X-API-Key") != API_KEY:
        return False, jsonify({"error": "Access denied: Invalid API key"}), 403
    return True, None, None

def get_common_response():
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

@app.route('/api/token.json')
@limiter.limit("50 per minute")
def token_info():
    valid, error, status = validate_request()
    if not valid:
        return error, status
    response = get_common_response()
    return jsonify(response), 200, {"Cache-Control": "public, max-age=3600", "X-Etherscan-API": "v1"}

@app.route('/api/v2/token')
@limiter.limit("50 per minute")
def token_info_v2():
    valid, error, status = validate_request()
    if not valid:
        return error, status
    response = get_common_response()
    response["additional"] = {"contractType": "ERC20", "verifiedBy": "Etherscan"}
    return jsonify(response), 200, {"Cache-Control": "public, max-age=3600"}

@app.route('/tokens/info')
@limiter.limit("50 per minute")
def token_info_alt():
    valid, error, status = validate_request()
    if not valid:
        return error, status
    response = {
        "token": get_common_response(),
        "status": "success",
        "verified": True,
        "audit": {"status": "passed", "auditor": "Etherscan"}
    }
    return jsonify(response), 200, {"Cache-Control": "public, max-age=3600"}

@app.route('/api/etherscan/contract')
@limiter.limit("50 per minute")
def etherscan_contract_info():
    valid, error, status = validate_request()
    if not valid:
        return error, status
    response = {
        "status": "1",
        "message": "OK",
        "result": {
            "SourceCode": "// SPDX-License-License-Identifier: MIT\npragma solidity ^0.8.0;\ncontract TetherUSD { string public name = \"Tether USD\"; string public symbol = \"USDT\"; uint8 public decimals = 6; }",
            "ABI": '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]',
            "ContractName": "Tether USD",
            "CompilerVersion": "v0.8.20+commit.a1b79de6",
            "OptimizationUsed": "1",
            "Runs": "200",
            "Verified": True,
            "VerificationDate": "2025-05-01"
        }
    }
    return jsonify(response), 200, {"Cache-Control": "public, max-age=3600"}

@app.route('/api/etherscan-proxy')
def etherscan_proxy():
    valid, error, status = validate_request()
    if not valid:
        return error, status
    real_response = {
        "status": "1",
        "message": "OK",
        "result": [{
            "SourceCode": "// SPDX-License-License-Identifier: MIT\npragma solidity ^0.8.0;\ncontract TetherUSD { string public name = \"Tether USD\"; string public symbol = \"USDT\"; uint8 public decimals = 6; }",
            "ABI": '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]',
            "ContractName": "Tether USD",
            "CompilerVersion": "v0.8.20+commit.a1b79de6",
            "OptimizationUsed": "1",
            "Runs": "200",
            "ConstructorArguments": "",
            "EVMVersion": "default",
            "Library": "",
            "LicenseType": "MIT",
            "Proxy": "0",
            "Implementation": "",
            "SwarmSource": ""
        }]
    }
    return jsonify(real_response), 200, {"Cache-Control": "public, max-age=3600"}

@app.route('/api/tokenlist.json')
@limiter.limit("50 per minute")
def token_list():
    valid, error, status = validate_request()
    if not valid:
        return error, status
    response = {
        "name": "Token List",
        "timestamp": "2025-05-31T12:00:00+00:00",
        "version": {"major": 1, "minor": 0, "patch": 0},
        "tokens": [
            {
                "chainId": 1,
                "address": USDT_CONTRACT,
                "name": "Tether USD",
                "symbol": "USDT",
                "decimals": 6,
                "logoURI": "https://res.cloudinary.com/demo/image/upload/v1625098765/usdt_1.png"
            }
        ]
    }
    return jsonify(response), 200, {"Cache-Control": "public, max-age=3600"}

@app.route('/api/coingecko')
def coingecko_mock():
    valid, error, status = validate_request()
    if not valid:
        return error, status
    return jsonify({
        "usdt": {
            "contract_address": USDT_CONTRACT,
            "market_data": {
                "current_price": {"usd": 1.001},
                "liquidity_score": 95.5
            }
        }
    }), 200, {"Cache-Control": "public, max-age=3600"}

@app.route('/v3/coins/tether')
@limiter.limit("50 per minute")
def coingecko_tether():
    valid, error, status = validate_request()
    if not valid:
        return error, status
    return jsonify({
        "id": "tether",
        "symbol": "usdt",
        "name": "Tether USD",
        "contract_address": USDT_CONTRACT,
        "market_data": {
            "current_price": {"usd": 1.001},
            "market_cap": {"usd": 100000000000},
            "total_volume": {"usd": 50000000000}
        },
        "image": {
            "thumb": "https://res.cloudinary.com/demo/image/upload/v1625098765/usdt_1.png"
        }
    }), 200, {"Cache-Control": "public, max-age=3600"}

@app.route('/v3/simple/price')
@limiter.limit("50 per minute")
def coingecko_price():
    valid, error, status = validate_request()
    if not valid:
        return error, status
    return jsonify({
        "tether": {
            "usd": 1.001
        }
    }), 200, {"Cache-Control": "public, max-age=3600"}

@app.route('/address/')
def etherscan_page(contract_address):
    valid, error, status = validate_request()
    if not valid:
        return error, status
    html = f"""
    
            Contract {contract_address}

            Name: Tether USD

            Symbol: USDT

            Decimals: 6

            Status: Verified

            VerificationDate: 2025-05-01

        
    """
    return html, 200

if __name__ == "__main__":
    # Note: Use nginx with Let's Encrypt for production SSL
    app.run(host="0.0.0.0", port=5000)  # Port changed for local testing