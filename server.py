from flask import Flask, jsonify, request
import subprocess
import os
import json
from xrp_contract import XRPContract
import asyncio
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv('./.env')

app = Flask(__name__)
CORS(app, supports_credentials=True)
# Initialize XRP contract with source wallet seed from environment variable
xrp_contract = XRPContract(metamask_private_key=os.getenv('METAMASK_PRIVATE_KEY'))

def verify_proof(proof, public_signals, verification_key_path):
    """Function to verify the proof"""
    try:
        # Load verification key
        with open(verification_key_path, "r") as vk_file:
            verification_key = json.load(vk_file)

        # Example of calling a proof verification function/library
        # This could use snarkjs, circomlib, or any other tool you are using
        is_valid = some_proof_verification_library.verify(verification_key, proof, public_signals)
        return is_valid
    except Exception as e:
        return {
            "success": False,
            "message": "Error during proof verification.",
            "error": str(e)
        }
    

def execute_generate_call():
    """Helper function to execute the generate call script"""
    try:
        script_path = os.path.join(os.getcwd(), "make_plonk_contract.sh")
        output_dir = os.path.join(os.getcwd(), "commitmentproof_js")
        output_file_path = os.path.join(output_dir, "generatecall_output.txt")

        if not os.path.exists(script_path):
            return {
            "success": False,
                "message": "The 'make_plonk_contract.sh' script does not exist in the current directory."
            }, 500

        process = subprocess.run(
            ["bash", script_path],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if process.returncode != 0:
            return {
                "success": False,
                "message": "Error occurred while running the script.",
                "error": process.stderr
            }, 500

        if os.path.exists(output_file_path):
            with open(output_file_path, 'r') as file:
                output = file.read()
            try:
                output_json = json.loads(output)
                # proof = output_json.get("proof")  # Extract proof
                # public_signals = output_json.get("public_signals")  # Extract public signals
                # Verify the proof
                # is_valid = verify_proof(proof, public_signals, verification_key_path)

                # if is_valid:
                #     verification_message = "Proof verified successfully."
                # else:
                #     verification_message = "Proof verification failed."
            except json.JSONDecodeError:
                output_json = output
        else:
            output_json = "Error: generatecall output not found."

        return {
            "success": True,
            "message": "Script executed successfully.",
            "output": output_json,
            # "verification": verification_message
        }, 200

    except Exception as e:
        return {
            "success": False,
            "message": "An exception occurred.",
            "error": str(e)
        }, 500
    
    

@app.route('/deposit', methods=['POST'])
async def deposit():
    """
    Endpoint to handle deposit requests.
    Input:
        - amount: The amount of XRP to transfer.
        - currency: The currency type (e.g., XRP).
    """
    try:
        # data = request.get_json()
        # amount = data.get('amount', '10')
        # currency = data.get('currency', 'XRP')  # Default currency is XRP

        amount = 10
        currency = 'XRP'

        if not amount:
            return jsonify({
                "success": False,
                "message": "Amount is required"
            }), 400

        if currency != 'XRP':
            return jsonify({
                "success": False,
                "message": "Unsupported currency. Only XRP is allowed."
            }), 400

        # Step 1: Get deposit address
        if xrp_contract.eth_account:
            deposit_address = xrp_contract.eth_account.address
        elif xrp_contract.source_wallet:
            deposit_address = xrp_contract.source_wallet.classic_address
        else:
            return jsonify({
                "success": False,
                "message": "No wallet initialized"
            }), 500

        # Step 2: Generate the SNARK proof using the `generatecall` function
        result, status_code = execute_generate_call()
        print(f"Result: {result}")
        print(f"Status code: {status_code}")
        if not isinstance(result, dict) or not isinstance(status_code, int):
            raise ValueError("Invalid response from execute_generate_call()")

        if not result.get("success"):
            return jsonify({
                "success": False,
                "message": "Failed to generate SNARK proof",
                "details": result.get("message")
            }), 500

        proof = result.get("output", {}).get("proof", "N/A")
        public_signals = result.get("output", {}).get("public_signals", "N/A")

        return jsonify({
            "success": True,
            "message": "Deposit information generated successfully",
            "deposit_address": deposit_address,
            "amount": amount,
            "currency": currency,
            "snark_proof": proof,
            "public_signals": public_signals
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An exception occurred.",
            "error": str(e)
        }), 500



@app.route('/withdraw', methods=['POST'])
async def withdraw():
    """
    Endpoint to handle withdrawal requests.
    Input:
        - proof: The SNARK proof for verification.
        - recipient: The recipient's XRP address.
    Output:
        - success: Whether the withdrawal was successful.
        - message: A status message.
    """
    try:
        # Parse the input data
        data = request.get_json()
        proof = data.get('proof')
        recipient = data.get('recipient')

        # Validate inputs
        if not proof:
            return jsonify({
                "success": False,
                "message": "Proof is required"
            }), 400

        if not recipient:
            return jsonify({
                "success": False,
                "message": "Recipient address is required"
            }), 400

        # Define the amount to transfer
        amount = 10  # Default amount for withdrawal

        # Verify the proof (optional - if needed in your workflow)
        # verification_result = verify_proof(proof, public_signals, verification_key_path)
        # if not verification_result:
        #     return jsonify({
        #         "success": False,
        #         "message": "Proof verification failed."
        #     }), 400

        # Perform the XRP transfer
        response = await xrp_contract.send_xrp(recipient, amount)

        # Verify transaction success
        if response and xrp_contract.verify_transaction(response.result['hash']):
            return jsonify({
                "success": True,
                "message": "Withdrawal successful",
                "transaction_hash": response.result['hash']
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Withdrawal failed. Transaction could not be verified."
            }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An exception occurred.",
            "error": str(e)
        }), 500




if __name__ == '__main__':
    app.run(debug=True, port=5000)