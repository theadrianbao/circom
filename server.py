from flask import Flask, jsonify, request
import subprocess
import os
import json
from xrp_contract import XRPContract
import asyncio
from dotenv import load_dotenv

load_dotenv('./.env')

app = Flask(__name__)
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
                proof = output_json.get("proof")  # Extract proof
                public_signals = output_json.get("public_signals")  # Extract public signals
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
    

@app.route('/generatecall', methods=['POST'])
def generatecall():
    # Endpoint to generate call
    try:
        result, status_code = execute_generate_call()
        if not isinstance(result, dict) or not isinstance(status_code, int):
            raise ValueError("Invalid response from execute_generate_call()")
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/deploy_contract', methods=['POST'])
async def deploy_contract():
    try:
        data = request.get_json()
        destination_address = data.get('destination_address')
        amount = data.get('amount', 10)  # Default amount is 10 XRP if not specified
        
        if not destination_address:
            return jsonify({
                "success": False,
                "message": "Destination address is required"
            }), 400

        # Send XRP from our wallet to the user's destination address
        response = await xrp_contract.send_xrp(destination_address, amount)
        
        # Verify transaction
        if xrp_contract.verify_transaction(response.result['hash']):
            return jsonify({
                "success": True,
                "message": "XRP transfer successful",
                "transaction_hash": response.result['hash']
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "XRP transfer failed"
            }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An exception occurred.",
            "error": str(e)
        }), 500



if __name__ == '__main__':
    app.run(debug=True, port=5500)