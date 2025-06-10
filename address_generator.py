from Crypto.Hash import keccak
import base58
from hashlib import sha256
from eth_abi import encode
import time

FACTORY_BASE58 = "TS5FTZKfRu1SupoKexz7uzDArbw8tMPz9L"
IMPLEMENTATION_BASE58 = "TNFUSK7N1HpTe4ex6PtSurZnohvCmX2wA3"
REAL_USDT_BASE58 = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

# Remix’te derlenmiş TokenProxy.sol bytecode’u
TOKEN_PROXY_BYTECODE = "0x..."  # TODO: Remix’ten al, keccak256 ile doğrula

def base58_to_bytes(base58_addr):
    decoded = base58.b58decode(base58_addr)
    return decoded[1:-4]

def compute_tron_address(salt):
    salt_bytes = keccak.new(data=salt.to_bytes(32, byteorder='big'), digest_bits=256).digest()
    bytecode = bytes.fromhex(TOKEN_PROXY_BYTECODE[2:]) + encode(['address'], [base58_to_bytes(IMPLEMENTATION_BASE58)])
    factory_bytes = base58_to_bytes(FACTORY_BASE58)
    bytecode_hash = keccak.new(data=bytecode, digest_bits=256).digest()
    data = b'\xff' + factory_bytes + salt_bytes + bytecode_hash
    raw_address = keccak.new(data=data, digest_bits=256).digest()[-20:]
    tron_address = b'\x41' + raw_address
    checksum = sha256(sha256(tron_address).digest()).digest()[:4]
    return base58.b58encode(tron_address + checksum).decode()

if __name__ == "__main__":
    TARGET_PREFIX = "TR7NHq"
    for salt in range(1000000):
        computed_addr = compute_tron_address(salt)
        if computed_addr.startswith(TARGET_PREFIX):
            print(f"Found: Salt: {salt}, Address: {computed_addr}")
            break