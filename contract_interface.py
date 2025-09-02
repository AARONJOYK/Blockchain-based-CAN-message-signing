from web3 import Web3
import json

# Connect to Ganache
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Load contract address and ABI
with open("deployed_contract_address.txt") as f:
    contract_address = f.read().strip()

with open("ECUVerification_abi.json") as f:
    abi = json.load(f)

# Account setup
account_address = "0xA97e258C8023EfAED0A480819359fBB496728454"
private_key = "0x451df3c5eb377f56e362d317ed69a28a5b5d2242b7e0687958802461ff9c0a72"

# Contract instance
contract = web3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)

# Register
def register_ecu(ecu_id: str, ecu_address: str):
    txn = contract.functions.registerECU(
        Web3.keccak(text=ecu_id), Web3.to_checksum_address(ecu_address)
    ).build_transaction({
        'chainId': 1337,
        'gas': 200000,
        'gasPrice': web3.to_wei('1', 'gwei'),
        'nonce': web3.eth.get_transaction_count(account_address),
    })

    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f" ECU '{ecu_id}' registered at {ecu_address}.")

# Verify a payload on-chain 
def verify_payload_onchain(ecu_id: str, payload: str, v: int, r: bytes, s: bytes):
    txn = contract.functions.verifyPayload(
        Web3.keccak(text=ecu_id), payload, v, r, s
    ).build_transaction({
        'chainId': 1337,
        'gas': 300000,
        'gasPrice': web3.to_wei('1', 'gwei'),
        'nonce': web3.eth.get_transaction_count(account_address),
        'from': account_address
    })

    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f" Verification transaction mined. TxHash: {web3.to_hex(tx_hash)}")
    return receipt

def get_verification_result(payload: str) -> bool:
    return contract.functions.getVerificationResult(payload).call()

def get_registered_ecu_address(ecu_id: str):
    return contract.functions.ecuAddresses(Web3.keccak(text=ecu_id)).call()
