# MultiPool Mixer Setup Guide

## Set up the environment
1. clone the repo https://github.com/theadrianbao/circom.git
   git clone https://github.com/theadrianbao/circom.git
2. checkout out to the main branch
   git checkout main
3. use conda to build the environment
conda env create -f environment.yml
4. edit files in .env file
add METAMASK_PRIVATE_KEY and SLUSH_FUND_PRIVATE_KEY in the .env file.

## Deploying the Contract via Remix

1. Navigate to [Remix](https://remix.ethereum.org/).
2. Log in and upload the `multipool-contract` files.
3. Select **MultiPoolMixer.sol**, then compile and deploy it.
4. Specify the number of pools to create, for example, `5`.
5. Click the **Deploy** button.
6. After deployment, copy the contract address displayed in the terminal and paste it into **website.html** at line 148 (replace `contractAddress`).

## Running the Frontend and Backend

1. Start the backend server:
   ```bash
   python server.py
   ```
2. When the server starts, it will display a URL (usually `http://127.0.0.1:5002`). Open this address in your browser.

## Testing in the Frontend

1. Click **Connect Wallet** to connect your wallet.
2. Click **10 XRP Through Mixer** to initiate a deposit.
3. After the deposit, a proof will be generated and returned.
4. Copy the generated proof and paste it into the **SNARK Proof** field. Click **Withdraw**.
5. If the proof is valid, an alert will confirm the successful validation.
6. Confirm the withdrawal to complete the process.

---

This concludes the setup and testing procedure.