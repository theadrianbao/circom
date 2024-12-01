import sys
import requests
from web3 import Web3

rpc_url = "https://rpc-evm-sidechain.xrpl.org/"
web3 = Web3(Web3.HTTPProvider(rpc_url))

if web3.is_connected():
    print("Connected to XRPL EVM sidechain")
else:
    print("Failed to connect to XRPL EVM sidechain")
    exit()

def send():
    try:
        payload = {
            "amount": 10,  
            "currency": "XRP"  
        }

        headers = {
            'Content-Type': 'application/json'
        }

        print("Sending payload:", payload)

        response = requests.post(f"http://127.0.0.1:5000/deposit", json=payload, headers=headers)

        response_data = response.json()

        contract_address = response_data.get("contract_address", "Unknown")
        generatecall_output = response_data.get("generatecall_output", "No output")

        print("Contract Address:", contract_address)
        print("Generatecall Output:", generatecall_output)
    
    except Exception as e:
        print(f"An exception occurred: {str(e)}")

def prove(contract_address, contract_abi, snarkjs_output, receiving_address):
    try:
        contract = web3.eth.contract(address=contract_address, abi=contract_abi)
        proof_data = snarkjs_output
        proof_verified = contract.functions.verifyProof(*proof_data).call()

        if proof_verified:
            print("Proof verified successfully.")
            private_key = "e582e5988d98eac0d5cb00762619e53fd4f9df96c03e4325234fc29bd357137a"
            sender_address = web3.eth.account.privateKeyToAccount(private_key).address

            transaction = {
                'to': receiving_address,
                'value': web3.toWei(10, 'ether'), 
                'gas': 21000, 
                'gasPrice': web3.toWei(20, 'gwei'), 
                'nonce': web3.eth.getTransactionCount(sender_address),
            }

            signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
            txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
            txn_receipt = web3.eth.waitForTransactionReceipt(txn_hash)

            print(f"Transaction sent! Transaction hash: {txn_hash.hex()}")
            print(f"Transaction receipt: {txn_receipt}")
        else:
            print("Proof verification failed.")
    except Exception as e:
        print(f"An error occurred during proof verification or transaction: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: client.py <command> [arguments]")
        sys.exit(1)
    
    command = sys.argv[1]

    with open('abi_file.json', 'r') as abi_file:
        contract_abi = json.load(abi_file)
        
    if command == "send":
        send()
    elif command == "prove" and len(sys.argv) == 5:
        contract_address = sys.argv[2]
        snarkjs_output = sys.argv[3]
        receiving_address = sys.argv[4]
        
        prove(contract_address, contract_abi, snarkjs_output, receiving_address)
    
    else:
        print("Invalid command or arguments")
        print("Usage:")
        print("  client.py send")
        print("  client.py prove [contract address] [snarkjs output] [receiving address]")
        sys.exit(1)

if __name__ == "__main__":
    main()