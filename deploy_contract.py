from web3 import Web3
from solcx import compile_standard, install_solc
import json

# Install Solidity compiler (once)
install_solc('0.8.0')

# Read Solidity contract
with open("ECUVerification.sol", "r") as f:
    source_code = f.read()

# Compile contract
compiled = compile_standard({
    "language": "Solidity",
    "sources": {
        "ECUVerification.sol": {
            "content": source_code
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
            }
        }
    }
}, solc_version="0.8.0")

# Extract ABI and bytecode
abi = compiled['contracts']['ECUVerification.sol']['ECUVerification']['abi']
bytecode = compiled['contracts']['ECUVerification.sol']['ECUVerification']['evm']['bytecode']['object']

# Connect to Ganache
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

account = web3.to_checksum_address("0xA97e258C8023EfAED0A480819359fBB496728454")
private_key = "0x451df3c5eb377f56e362d317ed69a28a5b5d2242b7e0687958802461ff9c0a72"

# Create contract
contract = web3.eth.contract(abi=abi, bytecode=bytecode)

# Build and send transaction
txn = contract.constructor().build_transaction({
    'from': account,
    'nonce': web3.eth.get_transaction_count(account),
    'gas': 2000000,
    'gasPrice': web3.to_wei('1', 'gwei'),
    'chainId': 1337
})

signed_txn = web3.eth.account.sign_transaction(txn, private_key)
tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

# Save details
contract_address = receipt.contractAddress
print(" Contract deployed at:", contract_address)

with open("ECUVerification_abi.json", "w") as f:
    json.dump(abi, f)

with open("deployed_contract_address.txt", "w") as f:
    f.write(contract_address)
