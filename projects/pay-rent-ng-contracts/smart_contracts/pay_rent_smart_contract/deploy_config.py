#  pay_rent_smart_contract/deploy_config.py

import logging
import os
from dotenv import load_dotenv
import algokit_utils
from algosdk import account, mnemonic, logic
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    app_spec: algokit_utils.ApplicationSpecification,
    deployer: algokit_utils.Account,
) -> None:
    # Import the client
    from smart_contracts.artifacts.pay_rent_smart_contract.smart_card_contract_client import (
    SmartCardContractClient,
    )

    # Get credentials from environment variables
    sender_address = os.getenv("DEPLOYER_ADDRESS")
    sender_mnemonic = os.getenv("DEPLOYER_MNEMONIC")
    
    if not sender_address or not sender_mnemonic:
        raise ValueError("Missing DEPLOYER_ADDRESS or DEPLOYER_MNEMONIC in .env file")

    # Create deployer account from mnemonic
    private_key = mnemonic.to_private_key(sender_mnemonic)
    
    # Create deployer account configuration
    deployer = algokit_utils.Account(
        address=sender_address,
        private_key=private_key
    )

    # Initialize the app client
    app_client = SmartCardContractClient(
        algod_client,
        creator=deployer,
        indexer_client=indexer_client,
    )

    # Deploy the contract
    app_client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
    )

    # After deploying the contract
    app_id = app_client.app_id  # Assuming app_client has this attribute
    app_address = logic.get_application_address(app_id)

    print(f"Application ID: {app_id}")
    print(f"Application Address: {app_address}")
    # # Test the StoreSmartCardContract method
    # contract = StoreSmartCardContract()
    
    # # Dummy smart card number (512-bit unsigned integer)
    # dummy_smart_card_number = UInt512(123456789012345678901234567890)
    
    # # Dummy account address (Algorand addresses are 58 characters long)
    # dummy_account_address = Address("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

    # # Call the function with dummy values
    # result = contract.store_smart_card_number(dummy_smart_card_number, dummy_account_address)
    # print(f"Storage successful: {result}")