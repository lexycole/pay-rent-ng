# _helpers/api.py

import logging
import json
import os
import base64
import algokit_utils
import base64
import logging
import os
import traceback
from typing import List
from fastapi import FastAPI, HTTPException, Query
from algosdk.v2client import algod
from algosdk.v2client.indexer import IndexerClient
from algosdk.transaction import Transaction, SignedTransaction
from dotenv import load_dotenv
from algosdk import mnemonic, transaction
from pydantic import BaseModel

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)-10s: %(message)s")
logger = logging.getLogger(__name__)
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Pay rent Smart Contract API"}

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
    funded_address = os.getenv("DEPLOYER_ADDRESS")
    
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
        sender_address = os.getenv("DEPLOYER_ADDRESS")
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
        app_info = algod_client.application_info(app_id)

        # Create a signer
        signer = create_signer(private_key)
        logger.info(f"Signer created: {signer}")

        # Initialize the app client BEFORE any initialization attempts
        app_client = SmartCardContractClient(
            algod_client,
            app_id=app_id,
            signer=signer,
            indexer_client=indexer_client
        )

        # Check for global state (graceful handling)
        global_state = app_info.get('params', {}).get('global-state', None)
        
        # Initialize the app if needed
        if not global_state:
            logger.info("Global state not found, initializing the application.")
            
            try:
                # Use the app client to initialize
                init_txn = app_client.init()
                logger.info(f"Initialization transaction: {init_txn}")
                
                # Wait for transaction confirmation
                transaction.wait_for_confirmation(algod_client, init_txn.tx_id)
                
                # Refresh app info after initialization
                app_info = algod_client.application_info(app_id)
            except Exception as init_error:
                logger.error(f"Initialization error: {init_error}")
                raise

        # More verbose logging
        logger.info(f"Attempting to fetch smart card number for app ID: {app_id}")

        # Fetch the smart card number with additional error handling
        try:
            smart_card_number = app_client.fetch_smart_card_number()
            logger.info(f"Successfully fetched smart card number: {smart_card_number}")
        except Exception as fetch_error:
            logger.error(f"Error in fetch_smart_card_number: {fetch_error}")
            raise

        return {"smart_card_number": smart_card_number}
    
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Detailed error: {error_trace}")
        logger.error(f"Error fetching smart card number: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

import logging
import json
import os
import base64
import algokit_utils
import traceback
from typing import List
from fastapi import FastAPI, HTTPException, Query
from algosdk.v2client import algod
from algosdk.v2client.indexer import IndexerClient
from algosdk.transaction import Transaction, SignedTransaction
from dotenv import load_dotenv
from algosdk import mnemonic, transaction
from pydantic import BaseModel


@app.post("/set-smart-card-number")
async def set_smart_card_number(smart_card_number: str = Query(..., description="Smart Card Number to set")):
    try:
        # Get Algorand clients
        algod_client = get_algod_client()
        indexer_client = get_indexer_client()

        # Get deployer credentials from environment
        sender_address = os.getenv("DEPLOYER_ADDRESS")
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

        # Check if the application exists
        app_id = int(app_id_from_env)
        
        # Create a signer
        signer = create_signer(private_key)

        # Initialize the app client
        app_client = SmartCardContractClient(
            algod_client,
            app_id=app_id,
            signer=signer,
            indexer_client=indexer_client
        )

        # Log the input smart card number
        logger.info(f"Received smart card number: {smart_card_number}")

        # Validate smart card number (optional: add your validation logic)
        if not smart_card_number or len(smart_card_number) < 5:
            raise ValueError("Invalid smart card number")

        # Call the contract method to set smart card number
        # You'll need to adjust this based on how your contract client is generated
        set_txn = app_client.set_smart_card_number(smart_card_number=smart_card_number)
        
        logger.info(f"Smart card number set transaction: {set_txn}")

        # Wait for transaction confirmation
        transaction.wait_for_confirmation(algod_client, set_txn.tx_id)

        return {
            "status": "success", 
            "message": "Smart card number set successfully",
            "transaction_id": set_txn.tx_id
        }
    
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Detailed error: {error_trace}")
        logger.error(f"Error setting smart card number: {e}", exc_info=True)
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
        sender_address = os.getenv("DEPLOYER_ADDRESS")

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
    













# # Imports (add these at the top of your file)
# import logging
# from fastapi import FastAPI, HTTPException
# from smart_contracts.artifacts.pay_rent_smart_contract.pay_rent_smart_contract_client import PayRentSmartContractClient
# from algosdk.v2client.algod import AlgodClient
# from algosdk.v2client.indexer import IndexerClient
# from algokit_utils import get_algod_client, get_indexer_client, get_account
