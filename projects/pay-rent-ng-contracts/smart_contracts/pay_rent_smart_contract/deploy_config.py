import logging
import os
from dotenv import load_dotenv
import algokit_utils
from algosdk import account, mnemonic
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
    from smart_contracts.artifacts.pay_rent_smart_contract.pay_rent_smart_contract_client import (
        PayRentSmartContractClient,
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
    app_client = PayRentSmartContractClient(
        algod_client,
        creator=deployer,
        indexer_client=indexer_client,
    )

    # Deploy the contract
    app_client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
    )

    # Test the StoreSmartCardContract method
    contract = StoreSmartCardContract()
    
    # Dummy smart card number (512-bit unsigned integer)
    dummy_smart_card_number = UInt512(123456789012345678901234567890)
    
    # Dummy account address (Algorand addresses are 58 characters long)
    dummy_account_address = Address("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

    # Call the function with dummy values
    result = contract.store_smart_card_number(dummy_smart_card_number, dummy_account_address)
    print(f"Storage successful: {result}")