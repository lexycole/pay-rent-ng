from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from algosdk import algod, account, transaction
from algosdk.future.transaction import ApplicationNoOpTxn, LogicSig
from algosdk.v2client.algod import AlgodClient

app = FastAPI()

# Replace these with your Algorand network details
ALGOD_ADDRESS = "https://lora.algokit.io/localnet/account/FBA3RUWOUUEOCMECZF7SXSUDRMROT3BI4UPWLUQZ4OYGSFTI5TCKYSXDWA"
ALGOD_TOKEN = "Your-API-Token"
APP_ID = 1002  # Replace with your actual Algorand app ID

# Set up the Algod client
algod_client = AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# FastAPI model for request body
class UserData(BaseModel):
    account_address: str = Field(..., regex="^[A-Z0-9]{58}$")
    number: int = Field(..., ge=1000000000, le=9999999999, description="A 10-digit number")

@app.post("/store-data/")
async def store_data(user_data: UserData):
    account_address = user_data.account_address
    number = user_data.number

    # Verify if number is exactly 10 digits
    if len(str(number)) != 10:
        raise HTTPException(status_code=400, detail="Number must be 10 digits.")

    # Verify if account address is a valid Algorand address
    if not account.is_valid_address(account_address):
        raise HTTPException(status_code=400, detail="Invalid Algorand account address.")

    # Prepare transaction to call the smart contract
    try:
        # Retrieve account private key (this is an example, secure your keys in production)
        private_key = "YOUR_ACCOUNT_PRIVATE_KEY"  # Replace with actual private key

        # Get params for the transaction
        params = algod_client.suggested_params()
        
        # Construct the ApplicationNoOpTxn to call set_user_number in the smart contract
        app_args = [b"set_user_number", number.to_bytes(8, "big")]
        txn = ApplicationNoOpTxn(sender=account_address, sp=params, index=APP_ID, app_args=app_args)

        # Sign and send the transaction
        signed_txn = txn.sign(private_key)
        tx_id = algod_client.send_transaction(signed_txn)

        # Wait for transaction confirmation
        transaction.wait_for_confirmation(algod_client, tx_id, 4)

        return {"status": "success", "tx_id": tx_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")



# # Imports (add these at the top of your file)
# import logging
# from fastapi import FastAPI, HTTPException
# from smart_contracts.artifacts.pay_rent_smart_contract.pay_rent_smart_contract_client import PayRentSmartContractClient
# from algosdk.v2client.algod import AlgodClient
# from algosdk.v2client.indexer import IndexerClient
# from algokit_utils import get_algod_client, get_indexer_client, get_account

# # Configure logging
# logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO or DEBUG
# logger = logging.getLogger(__name__)

# app = FastAPI()

# @app.post("/api/store-card")
# async def store_smart_card(wallet_data: WalletData) -> ResponseData:
#     try:
#         logger.info("Received request to store smart card data: %s", wallet_data)

#         # Validate input
#         if not wallet_data.account_address.strip():
#             logger.error("Invalid account address provided")
#             raise ValueError("Invalid account address")
        
#         if not wallet_data.smart_card_number.isdigit() or len(wallet_data.smart_card_number) != 10:
#             logger.error("Invalid smart card number format: %s", wallet_data.smart_card_number)
#             raise ValueError("Smart card number must be exactly 10 digits")

#         # Set up Algorand clients and account
#         algod_client = get_algod_client()
#         indexer_client = get_indexer_client()
#         deployer = get_account(algod_client, "DEPLOYER", fund_with_algos=0)
#         logger.info("Algorand clients and deployer account initialized")

#         # Initialize the contract client
#         app_client = PayRentSmartContractClient(
#             algod_client=algod_client,
#             creator=deployer,
#             indexer_client=indexer_client
#         )
#         logger.info("Smart contract client initialized")

#         # Interact with the smart contract method (e.g., store_card_data)
#         app_client.store_card_data(
#             account_address=wallet_data.account_address,
#             smart_card_number=wallet_data.smart_card_number
#         )
#         logger.info("Smart card data stored successfully for account: %s", wallet_data.account_address)

#         return ResponseData(
#             status=True,
#             message="Smart card data stored successfully on the blockchain",
#             data={
#                 "account_address": wallet_data.account_address,
#                 "smart_card_number": wallet_data.smart_card_number
#             }
#         )
#     except ValueError as ve:
#         logger.error("Validation error: %s", str(ve))
#         raise HTTPException(
#             status_code=400,
#             detail=str(ve)
#         )
#     except Exception as e:
#         logger.exception("Failed to store smart card data: %s", str(e))
#         raise HTTPException(
#             status_code=500,
#             detail="An error occurred while storing smart card data"
#         )
