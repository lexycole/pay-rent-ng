# Imports (add these at the top of your file)
import logging
from fastapi import FastAPI, HTTPException
from smart_contracts.artifacts.pay_rent_smart_contract.pay_rent_smart_contract_client import PayRentSmartContractClient
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from algokit_utils import get_algod_client, get_indexer_client, get_account

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO or DEBUG
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/api/store-card")
async def store_smart_card(wallet_data: WalletData) -> ResponseData:
    try:
        logger.info("Received request to store smart card data: %s", wallet_data)

        # Validate input
        if not wallet_data.account_address.strip():
            logger.error("Invalid account address provided")
            raise ValueError("Invalid account address")
        
        if not wallet_data.smart_card_number.isdigit() or len(wallet_data.smart_card_number) != 10:
            logger.error("Invalid smart card number format: %s", wallet_data.smart_card_number)
            raise ValueError("Smart card number must be exactly 10 digits")

        # Set up Algorand clients and account
        algod_client = get_algod_client()
        indexer_client = get_indexer_client()
        deployer = get_account(algod_client, "DEPLOYER", fund_with_algos=0)
        logger.info("Algorand clients and deployer account initialized")

        # Initialize the contract client
        app_client = PayRentSmartContractClient(
            algod_client=algod_client,
            creator=deployer,
            indexer_client=indexer_client
        )
        logger.info("Smart contract client initialized")

        # Interact with the smart contract method (e.g., store_card_data)
        app_client.store_card_data(
            account_address=wallet_data.account_address,
            smart_card_number=wallet_data.smart_card_number
        )
        logger.info("Smart card data stored successfully for account: %s", wallet_data.account_address)

        return ResponseData(
            status=True,
            message="Smart card data stored successfully on the blockchain",
            data={
                "account_address": wallet_data.account_address,
                "smart_card_number": wallet_data.smart_card_number
            }
        )
    except ValueError as ve:
        logger.error("Validation error: %s", str(ve))
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        logger.exception("Failed to store smart card data: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="An error occurred while storing smart card data"
        )
