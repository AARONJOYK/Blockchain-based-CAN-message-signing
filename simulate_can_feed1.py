import csv
import os
from contract_interface import verify_payload_onchain, get_verification_result

ECU_ID = "ECU_1"
INPUT_FILE = "signed_real.csv"
INPUT_FILE = "signed_fake.csv"
OUTPUT_FILE = "live_results.csv"

# Create result file with header if it doesn't exist
if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Payload", "ECU_ID", "Verified", "TxHash", "Block", "Gas", "TxStatus"])
        writer.writeheader()

# Run simulation
with open(INPUT_FILE, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        payload = row['payload']
        v = int(row['v'])
        r = bytes.fromhex(row['r'][2:] if row['r'].startswith("0x") else row['r'])
        s = bytes.fromhex(row['s'][2:] if row['s'].startswith("0x") else row['s'])

        receipt = verify_payload_onchain(ECU_ID, payload, v, r, s)
        tx_hash = receipt.transactionHash.hex()
        status = "TX SUCCESS" if receipt.status == 1 else " TX FAILED"
        block = receipt.blockNumber
        gas = receipt.gasUsed

        try:
            result = get_verification_result(payload)
            verified = "✅ VERIFIED" if result else "❌ REJECTED"
        except:
            verified = "ERROR"

        # Append to result CSV for dashboard
        with open(OUTPUT_FILE, "a", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=["Payload", "ECU_ID", "Verified", "TxHash", "Block", "Gas", "TxStatus"])
            writer.writerow({
                "Payload": payload[:10] + "...",
                "ECU_ID": ECU_ID,
                "Verified": verified,
                "TxHash": tx_hash,
                "Block": block,
                "Gas": gas,
                "TxStatus": status
            })

        print(f"[{status}] {verified} | Payload: {payload[:10]}... | Tx: {tx_hash} | Block: {block} | Gas: {gas}")
