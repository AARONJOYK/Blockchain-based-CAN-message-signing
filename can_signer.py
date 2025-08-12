import csv
from eth_account import Account
from eth_account.messages import encode_defunct

# Load the real ECU private key from file
with open("ecu1_private_key.txt", "r") as f:
    private_key = f.read().strip()

# Create real and fake signer accounts
real_signer = Account.from_key(private_key)
fake_signer = Account.create()  # random invalid signer

# Input/output files
input_csv = "Normal.csv"
output_real = "signed_real.csv"
output_fake = "signed_fake.csv"

# Read all lines from the input CSV
with open(input_csv, "r") as f:
    reader = list(csv.reader(f))

# Split the file into two halves
mid = len(reader) // 2
real_lines = reader[:mid]
fake_lines = reader[mid:]

def sign_line(signer, line):
    if len(line) < 2:
        return None

    # Extract only the DATA portion after the #
    can_frame = line[1]  
    if '#' not in can_frame:
        return None
    payload = can_frame.split('#')[1].strip()

    # Compute keccak256 hash of the payload
    from web3 import Web3
    payload_hash = Web3.keccak(text=payload)

    # Sign the prefixed message hash (like Solidity expects)
    from eth_account.messages import encode_defunct
    message = encode_defunct(hexstr=payload_hash.hex())
    signed = signer.sign_message(message)

    # Convert r and s to 32-byte hex strings
    r_hex = '0x' + signed.r.to_bytes(32, byteorder='big').hex()
    s_hex = '0x' + signed.s.to_bytes(32, byteorder='big').hex()

    return [line[0], payload, signed.v, r_hex, s_hex]

# Write the real signed lines
with open(output_real, "w", newline='') as real_out:
    writer = csv.writer(real_out)
    writer.writerow(['timestamp', 'payload', 'v', 'r', 's'])
    for line in real_lines:
        signed = sign_line(real_signer, line)
        if signed:
            writer.writerow(signed)

# Write the fake signed lines
with open(output_fake, "w", newline='') as fake_out:
    writer = csv.writer(fake_out)
    writer.writerow(['timestamp', 'payload', 'v', 'r', 's'])
    for line in fake_lines:
        signed = sign_line(fake_signer, line)
        if signed:
            writer.writerow(signed)

print(f"Signed {len(real_lines)} real and {len(fake_lines)} fake entries.")
print("Outputs:")
print(f"  ✅ {output_real}")
print(f"  ❌ {output_fake}")
