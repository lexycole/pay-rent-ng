# _helpers/api.py

import logging
import json
import os
import base64
import algokit_utils
from fastapi import FastAPI, HTTPException, Query
from algosdk.v2client import algod
from algosdk.v2client.indexer import IndexerClient
from algosdk.transaction import Transaction, SignedTransaction
from dotenv import load_dotenv
from algosdk import mnemonic, transaction
from algosdk import transaction
from algosdk.v2client import algod



logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)-10s: %(message)s")
logger = logging.getLogger(__name__)
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Smart Contract API"}

# Configure Algorand clients
def get_algod_client():
    algod_address = os.getenv("ALGOD_ADDRESS", "https://testnet-api.algonode.cloud")
    algod_token = os.getenv("ALGOD_TOKEN", "")
    return algod.AlgodClient(algod_token, algod_address)

def get_indexer_client():
    indexer_address = os.getenv("INDEXER_ADDRESS", "https://testnet-idx.algonode.cloud")
    indexer_token = os.getenv("INDEXER_TOKEN", "")
    return IndexerClient(indexer_token, indexer_address)

def create_signer(private_key):
    def signer(txn: Transaction) -> SignedTransaction:
        return txn.sign(private_key)
    
    # Add the private_key as an attribute to the signer function
    signer.private_key = private_key
    
    return signer

def diagnose_clear_state(smart_contract_client, algod_client, sender_address):
    try:
        # 1. Check Application Existence
        app_id = smart_contract_client.app_id
        if not app_id:
            logger.error("No Application ID found")
            return

        # 2. Retrieve Application Information
        try:
            app_info = algod_client.application_info(app_id)
            logger.info("Application Info: %s", app_info)
        except Exception as app_info_error:
            logger.error(f"Could not retrieve app info: {app_info_error}")
            return

        # 3. Check Sender's Account
        sender_info = algod_client.account_info(sender_address)
        logger.info("Sender Account Info: %s", sender_info)

        # 4. List Local State for Sender
        local_state = [
            state for state in sender_info.get('apps-local-state', [])
            if state.get('id') == app_id
        ]
        logger.info("Local State for App: %s", local_state)

        if not local_state:
            logger.error("No local state found for the application. Ensure the account has opted in.")
            return

        # 5. Attempt Clear State with Verbose Logging
        result = smart_contract_client.clear_state(
            transaction_parameters={
                'sender': sender_address,
                'note': b'Diagnostic Clear State'
            }
        )
        logger.info("Clear State Successful: %s", result)

    except Exception as e:
        logger.error(f"Comprehensive Diagnosis Failed: {e}")
        import traceback
        traceback.print_exc()

def check_application_exists(algod_client, app_id):
    try:
        app_info = algod_client.application_info(app_id)
        logger.info(f"app_info,{app_info}")
        return True
    except Exception as e:
        logger.error(f"Application {app_id} does not exist: {e}")
        return False


# Usage
# diagnose_clear_state(smart_contract_client, algod_client, sender_address)


# def activate_account_localnet(algorand_client, sender_address):
#     # Use AlgoKit to automatically handle online registration
#     algokit_utils.ensure_funded(
#         algorand_client,
#         {
#             "sender": sender_address,
#             "receiver": sender_address,
#             "amount": algokit_utils.get_min_balance(algorand_client, sender_address)
#         }
#     )
    
#     # Automatically brings the account online if needed
#     algokit_utils.make_pay_txn(
#         algorand_client,
#         {
#             "sender": "FBA3RUWOUUEOCMECZF7SXSUDRMROT3BI4UPWLUQZ4OYGSFTI5TCKYSXDWA",
#             "receiver": "SW4BTZGCCNMSDYSANRLKFQOZNYRKH4B7J6DNSEUAYPSRGOYZRGKQEAW5EY",
#             "amount": 0  # Zero-amount transaction
#         }
#     )

def reactivate_account(algod_client, sender_address, private_key):
    # Create a no-op transaction to bring the account online
    params = algod_client.suggested_params()
    txn = transaction.PaymentTxn(
        sender=sender_address,
        sp=params,
        receiver=sender_address,
        amt=0  # Zero amount transaction
    )
    
    # Sign the transaction
    signed_txn = txn.sign(private_key)
    
    # Send the transaction
    try:
        tx_id = algod_client.send_transaction(signed_txn)
        logger.info(f"Transaction sent with ID: {tx_id}")
        
        # Wait for confirmation
        transaction_response = transaction.wait_for_confirmation(algod_client, tx_id, 4)
        logger.info("Transaction confirmed")
    except Exception as e:
        logger.info(f"Error reactivating account: {e}")

def fund_account(algod_client, sender_address, amount):
    # Use the most funded account from LocalNet
    funded_address = "FBA3RUWOUUEOCMECZF7SXSUDRMROT3BI4UPWLUQZ4OYGSFTI5TCKYSXDWA"
    
    # Load the mnemonic from environment or a secure method
    funded_mnemonic = os.getenv("DEPLOYER_MNEMONIC")
    
    if not funded_mnemonic:
        raise ValueError("Funded account mnemonic is not set")
    
    # Convert mnemonic to private key
    funded_private_key = mnemonic.to_private_key(funded_mnemonic)
    
    # Get suggested params
    params = algod_client.suggested_params()
    
    # Create payment transaction
    txn = transaction.PaymentTxn(
        sender=funded_address,
        sp=params,
        receiver=sender_address,
        amt=amount  # Amount in microAlgos
    )
    
    # Sign the transaction
    signed_txn = txn.sign(funded_private_key)
    
    try:
        # Send transaction
        tx_id = algod_client.send_transaction(signed_txn)
        logger.info(f"Funding transaction sent from {funded_address} to {sender_address}")
        logger.info(f"Transaction ID: {tx_id}")
        
        # Wait for confirmation
        transaction_response = transaction.wait_for_confirmation(algod_client, tx_id, 4)
        logger.info("Funding transaction confirmed")
        
        return tx_id
    except Exception as e:
        logger.error(f"Error funding account: {e}")
        raise

# In your .env file, add:
# FUNDED_ACCOUNT_MNEMONIC=your_mnemonic_here

def reactivate_and_fund(algod_client, sender_address, private_key, fund_amount):
    # Log the addresses for transparency
    logger.info(f"Deployed Address: {sender_address}")
    
    # Reactivate the account if needed
    try:
        reactivate_account(algod_client, sender_address, private_key)
        logger.info(f"Reactivated Address: {sender_address}")
    except Exception as e:
        logger.warning(f"Reactivation might not be necessary: {e}")
    
    # Fund the account
    try:
        tx_id = fund_account(algod_client, sender_address, fund_amount)
        logger.info(f"Funded Address: {sender_address}")
        logger.info(f"Funding Transaction ID: {tx_id}")
    except Exception as e:
        logger.error(f"Funding failed: {e}")
        raise

# FastAPI endpoint
@app.post("/reactivate-and-fund/")
async def handle_reactivate_and_fund(
    address: str = Query(..., description="The address of the account to reactivate and fund"),
    amount: int = Query(default=1_000_000, description="The amount of microAlgos to fund the account with")
):
    try:
        algod_client = get_algod_client()
        
        # Get deployer credentials
        sender_mnemonic_str = os.getenv("DEPLOYER_MNEMONIC")
        private_key = mnemonic.to_private_key(sender_mnemonic_str)
        
        # Comprehensive logging
        logger.info(f"Recipient Address: {address}")
        logger.info(f"Funding Amount: {amount} microAlgos")
        
        # Reactivate and fund the account
        reactivate_and_fund(algod_client, address, private_key, amount)
        
        return {
            "status": "Success", 
            "message": "Account reactivated and funded successfully",
            "recipient_address": address,
            "amount": amount
        }
    
    except Exception as e:
        logger.error(f"Error in reactivating and funding account: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

def comprehensive_account_check(algod_client, address):
    try:
        account_info = algod_client.account_info(address)
        
        logger.info("Comprehensive Account Check:")
        logger.info(f"Address: {address}")
        logger.info(f"Status: {account_info.get('status', 'Unknown')}")
        logger.info(f"Total Balance: {account_info.get('amount', 0)} microAlgos")
        logger.info(f"Minimum Balance: {account_info.get('min-balance', 0)} microAlgos")
        logger.info(f"Pending Rewards: {account_info.get('pending-rewards', 0)} microAlgos")
        logger.info(f"Reward Base: {account_info.get('reward-base', 0)}")
        
        return account_info
    except Exception as e:
        logger.info(f"Account Verification Error: {e}")
        return None

# In your FastAPI route or separate script
# algod_client = get_algod_client()
# comprehensive_account_check(algod_client, sender_address)
# # Reactivate account
# reactivate_account(algod_client, sender_address, private_key)
# # Fund account
# fund_account(algod_client, sender_address, private_key, 1_000_000) 


# Import the client dynamically
from smart_contracts.artifacts.pay_rent_smart_contract.smart_card_contract_client import (
    SmartCardContractClient
)

def check_application_exists(algod_client, app_id):
    try:
        app_info = algod_client.application_info(app_id)
        return True
    except Exception as e:
        logger.error(f"Application {app_id} does not exist: {e}")
        return False

@app.get("/smart-card-number")
async def get_smart_card_number():
    try:
        # Get Algorand clients
        algod_client = get_algod_client()
        indexer_client = get_indexer_client()

        # Get deployer credentials from environment
        sender_address = "FBA3RUWOUUEOCMECZF7SXSUDRMROT3BI4UPWLUQZ4OYGSFTI5TCKYSXDWA"
        sender_mnemonic_str = os.getenv("DEPLOYER_MNEMONIC")
        app_id_from_env = os.getenv("APP_ID")

        # Validate environment variables
        if not sender_address:
            raise ValueError("DEPLOYER_ADDRESS is not set")
        if not sender_mnemonic_str:
            raise ValueError("DEPLOYER_MNEMONIC is not set")
        if not app_id_from_env:
            raise ValueError("APP_ID is not set")

        # Create deployer account
        private_key = mnemonic.to_private_key(sender_mnemonic_str)
        deployer = algokit_utils.Account(
            address=sender_address,
            private_key=private_key
        )

        # Explicitly check and activate the account if needed
        account_info = algod_client.account_info(sender_address)
        logger.info(f"Account balance: {account_info['amount']} microAlgos")
        logger.info(f"Account status: {account_info['status']}")

        # Check if the application exists
        app_id = int(app_id_from_env)
        if not check_application_exists(algod_client, app_id):
            raise HTTPException(status_code=404, detail=f"Application with ID {app_id} does not exist.")


        # Create a signer
        signer = create_signer(private_key)
        
        # Initialize the app client
        app_client = SmartCardContractClient(
            algod_client,
            app_id=int(app_id_from_env),  # Convert to int
            signer=signer,
            indexer_client=indexer_client
        )

        # Fetch the smart card number
        smart_card_number = app_client.get_smart_card_number()
        
        return {"smart_card_number": smart_card_number}
    
    except Exception as e:
        logger.error(f"Error fetching smart card number: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



def check_balance_detailed(algod_client, address):
    try:
        account_info = algod_client.account_info(address)
        
        # Print full account info for debugging
        logger.info("Full Account Info:", json.dumps(account_info, indent=2))
        
        # Extract balance
        balance = account_info.get('amount', 0)
        min_balance = account_info.get('min-balance', 0)
        
        logger.info(f"Raw Balance: {balance} microAlgos")
        logger.info(f"Minimum Balance: {min_balance} microAlgos")
        
        return {
            'total_balance': balance,
            'min_balance': min_balance,
            'spendable_balance': balance - min_balance
        }
    except Exception as e:
        logger.info(f"Error checking balance: {e}")
        return None



@app.post("/send-algos/")
async def send_algos(
    recipient_address: str = Query(..., description="The recipient's Algorand address"),
    amount: int = Query(..., description="The amount of microAlgos to send")
):
    try:
        # Get Algorand clients
        algod_client = get_algod_client()

        # Get deployer credentials from environment
        sender_mnemonic_str = os.getenv("DEPLOYER_MNEMONIC")
        sender_address = "FBA3RUWOUUEOCMECZF7SXSUDRMROT3BI4UPWLUQZ4OYGSFTI5TCKYSXDWA"

        # Create deployer account
        private_key = mnemonic.to_private_key(sender_mnemonic_str)

        # Use detailed balance checking
        balance_details = check_balance_detailed(algod_client, sender_address)
        
        if balance_details:
            logger.info(f"Balance Details: {balance_details}")
        
        # Check account balance
        account_info = algod_client.account_info(sender_address)
        balance = account_info['amount']
        logger.info(f"Account balance: {balance} microAlgos")

        if balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient microAlgos")

        # Create a signer
        signer = create_signer(private_key)

        # Create a transaction
        params = algod_client.suggested_params()
        txn = transaction.PaymentTxn(sender_address, params, recipient_address, amount)

        # Sign the transaction
        signed_txn = txn.sign(private_key)

        # Send the transaction
        txid = algod_client.send_transaction(signed_txn)
        logger.info(f"Transaction ID: ", {txid})

        # Wait for confirmation
        transaction.wait_for_confirmation(algod_client, txid)
        logger.info(f"Transaction confirmed!")

        return {"transaction_id": txid, "status": "Transaction confirmed!"}

    except Exception as e:
        logger.error(f"Error sending microAlgos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


import base64
import logging
from algosdk import transaction, mnemonic
from algosdk.v2client import algod
import os

logger = logging.getLogger(__name__)

def generate_participation_keys():
    """
    Generate participation keys for bringing an account online
    """
    try:
        # Generate proper voting and selection keys
        voting_pk = os.urandom(32)  # 32-byte random key for voting
        selection_pk = os.urandom(32)  # 32-byte random key for selection
        state_proof_pk = os.urandom(64)
        return {
            'voting_pk': base64.b64encode(voting_pk).decode(),
            'selection_pk': base64.b64encode(selection_pk).decode(),
             'state_proof_pk': base64.b64encode(state_proof_pk).decode(),
        }
    except Exception as e:
        logger.error(f"Error generating participation keys: {e}")
        raise

def bring_account_online(algod_client, sender_address, sender_private_key):
    """
    Bring an offline account online by sending a key registration transaction
    """
    try:
        # Fetch the suggested transaction parameters
        params = algod_client.suggested_params()

        # Generate participation keys
        participation_keys = generate_participation_keys()

        # Create the key registration transaction
        txn = transaction.KeyregTxn(
            sender=sender_address,
            sp=params,
            votekey=participation_keys['voting_pk'],  
            selkey=participation_keys['selection_pk'], 
            sprfkey=participation_keys['state_proof_pk'],
            votefst=params.first,
            votelst=params.last + 1000, 
            votekd=10   
        )

        # Sign the transaction
        signed_txn = txn.sign(sender_private_key)

        # Send the transaction
        tx_id = algod_client.send_transaction(signed_txn)

        # Wait for confirmation
        confirmed_txn = wait_for_confirmation(algod_client, tx_id, 4)

        logger.info(f"Transaction information: {confirmed_txn}")
        return tx_id

    except Exception as e:
        logger.error(f"Error bringing account online: {e}")
        raise

def wait_for_confirmation(client, txid, timeout):
    """
    Wait for a transaction to be confirmed
    """
    try:
        start_round = client.status()["last-round"] + 1
        current_round = start_round

        while current_round < start_round + timeout:
            try:
                pending_txn = client.pending_transaction_info(txid)
                
                # Additional logging for debugging
                logger.info(f"Pending Transaction Info: {pending_txn}")
                
                # Check if transaction is confirmed
                if pending_txn.get("confirmed-round", 0) > 0:
                    return pending_txn
                
                current_round += 1
                client.status_after_block(current_round)
            
            except Exception as inner_e:
                logger.error(f"Error in confirmation loop: {inner_e}")
                return None
        
        raise Exception("Timeout waiting for transaction confirmation")
    
    except Exception as e:
        logger.error(f"Confirmation wait error: {e}")
        raise

@app.post("/bring-account-online/")
async def handle_bring_account_online():
    try:
        # Configure logging
        logging.basicConfig(level=logging.INFO)

        # Get Algorand client
        algod_client = get_algod_client()

        # Get sender details
        sender_address = os.getenv("DEPLOYER_ADDRESS")
        sender_mnemonic = os.getenv("DEPLOYER_MNEMONIC")
        
        # Validate environment variables
        if not sender_address:
            raise ValueError("SENDER_ADDRESS is not set")
        if not sender_mnemonic:
            raise ValueError("SENDER_MNEMONIC is not set")
        
        # Convert mnemonic to private key
        sender_private_key = mnemonic.to_private_key(sender_mnemonic)

        # Check current account status
        account_info = algod_client.account_info(sender_address)
        current_status = account_info.get('status', 'Unknown')
        current_balance = account_info.get('amount', 0)

        logger.info(f"Current Account Status: {current_status}")
        logger.info(f"Current Account Balance: {current_balance} microAlgos")

        # Bring account online if offline
        if current_status.lower() == 'offline':
            tx_id = bring_account_online(algod_client, sender_address, sender_private_key)
            
            return {
                "status": "Success",
                "message": "Account brought online",
                "transaction_id": tx_id
            }
        else:
            return {
                "status": "Already Online",
                "message": "Account is already online"
            }

    except Exception as e:
        logger.error(f"Error bringing account online: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    

# @app.get("/check-balance/{address}")
# async def check_balance(address: str):
#     try:
#         algod_client = get_algod_client()
#         account_info = algod_client.account_info(address)
#         balance = account_info['amount']
#         return {
#             "address": address, 
#             "balance": balance, 
#             "algos": balance / 1_000_000
#         }
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=str(e))












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
