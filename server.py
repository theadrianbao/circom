from flask import Flask, jsonify, request
import subprocess
import os
import json

app = Flask(__name__)

@app.route('/verifyproof', methods=['POST'])
def verifyproof():
    try:
        data = request.json
        proof = data.get("proof")
        user_output = data.get("user_output")

        if not proof or not user_output:
            return jsonify({
                "success": False,
                "message": "Proof and user output are required."
            }), 400

        is_valid = verify_proof_function(proof, user_output)

        if is_valid:
            return jsonify({
                "success": True,
                "message": "Proof is valid."
            })
        else:
            return jsonify({
                "success": False,
                "message": "Invalid proof."
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An exception occurred during proof verification.",
            "error": str(e)
        }), 500

def verify_proof_function(proof, user_output):
    # 你的验证逻辑可以使用外部库或脚本
    # 示例：调用一个外部程序
    return proof == "expected_proof" and user_output == "expected_output"

@app.route('/transferfunds', methods=['POST'])
def transfer_funds():
    try:
        data = request.json
        withdrawal_address = data.get("withdrawal_address")
        amount = data.get("amount")

        if not withdrawal_address or not amount:
            return jsonify({
                "success": False,
                "message": "Withdrawal address and amount are required."
            }), 400

        # 调用 Trisha 的转账逻辑
        transfer_success = execute_transfer(withdrawal_address, amount)

        if transfer_success:
            return jsonify({
                "success": True,
                "message": "Funds transferred successfully."
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to transfer funds."
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An exception occurred during fund transfer.",
            "error": str(e)
        }), 500


def execute_transfer(address, amount):
    # 使用 Trisha 的代码执行转账逻辑
    return True  # 示例：假设转账成功


@app.route('/generatecall', methods=['POST'])
def generatecall():
    try:
        # Define the script path in the current working directory
        script_path = os.path.join(os.getcwd(), "make_plonk_contract.sh")
        
        # Define the directory for the output file
        output_dir = os.path.join(os.getcwd(), "commitmentproof_js")
        output_file_path = os.path.join(output_dir, "generatecall_output.txt")

        # Ensure the script exists in the current directory
        if not os.path.exists(script_path):
            return jsonify({
                "success": False,
                "message": "The 'make_plonk_contract.sh' script does not exist in the current directory."
            }), 500

        # Execute the script directly
        process = subprocess.run(
            ["bash", script_path],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Capture the output
        stdout = process.stdout
        stderr = process.stderr

        # Check for errors
        if process.returncode != 0:
            return jsonify({
                "success": False,
                "message": "Error occurred while running the script.",
                "error": stderr
            }), 500

        # Check if the output file exists in the commitmentproof_js directory
        if os.path.exists(output_file_path):
            with open(output_file_path, 'r') as file:
                output = file.read()

            # Ensure proper JSON formatting, remove extra escaping
            try:
                # Parse the JSON array and return it as a proper JSON response
                output_json = json.loads(output)
            except json.JSONDecodeError:
                output_json = output  # If not valid JSON, return the raw output as a string
        else:
            output_json = "Error: generatecall output not found."

        # Return the output as JSON
        return jsonify({
            "success": True,
            "message": "Script executed successfully.",
            "output": output_json
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "An exception occurred.",
            "error": str(e)
        }), 500



if __name__ == '__main__':
    app.run(debug=True)
