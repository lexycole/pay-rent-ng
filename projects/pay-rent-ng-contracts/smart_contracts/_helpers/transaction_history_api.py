from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from algosdk import mnemonic, account
from algosdk.v2client import algod

# Set up the FastAPI application
app = FastAPI()

# Configuration variables
ALGOD_TOKEN = "your_algod_token"
ALGOD_ADDRESS = "your_algod_address"
APP_ID = your_app_id

# Define the payment details model
 class PaymentDetails(BaseModel):
    user_iuc: str
    payment_amount: int
    payment_method: str

# Set up the Algod client
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Define the endpoint to store the payment details
@app.post("/transaction_receipt")
async def store_payment_details(payment_details: PaymentDetails):
    """Stores the payment details in IPFS and records the IPFS hash in the blockchain.
    """
    try:
        # Generate a new Algorand account for the user
        user_account = account.generate_account()
        user_mnemonic = mnemonic.from_private_key(user_account.private_key)

        # Create a new IPFS file for the payment details
        ipfs_hash =  #  ... (Your IPFS storage logic)

        # Create a new transaction to store the IPFS hash in the blockchain
        txn = algod_client.prepare_transaction(
            sender=user_account.address,
            app_id=APP_ID,
            on_complete=algod_client.OnComplete.NoOpOC,
            app_args=["store_payment_details", ipfs_hash],
            note="Payment details stored in IPFS"
        )

        # Sign the transaction with the user's private key
        signed_txn = txn.sign(user_account.private_key)

        # Submit the transaction to the blockchain
        algod_client.send_transaction(signed_txn)

        # Wait for the transaction to be confirmed
        confirmed_txn = algod_client.wait_for_confirmation(signed_txn.get_txid(), 4)

        # Return the transaction receipt
        return {"transaction_id": confirmed_txn.get_txid()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing payment details: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)