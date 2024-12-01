# pay_rent_smart_contract/contract.py

# from algopy.arc4 import ARC4Contract, Address, UInt512, BigUIntN
# from algopy import log, Txn, LocalState, subroutine, Bytes, Account, Bytes, UInt64, String

from algopy import ARC4Contract, arc4, Application, Account

class SmartCardContract(ARC4Contract):
    SMART_CARD_NUMBER: arc4.String

    @arc4.abimethod(allow_actions=["OptIn"])
    def init(self) -> None:
        """Initialize the smart card number during contract creation."""
        self.SMART_CARD_NUMBER = arc4.String("12345678901")

    @arc4.abimethod
    def get_smart_card_number(self) -> arc4.String:
        """Returns the hardcoded smart card number."""
        return self.SMART_CARD_NUMBER

    @arc4.abimethod
    def save_smart_card_number(self) -> arc4.String:
        """Saves the hardcoded smart card number."""
        self.SMART_CARD_NUMBER = arc4.String("12345678901")
        return arc4.String("Smart card number saved successfully.")

    # @arc4.abimethod
    # def get_app_id(self, app_a:Application) -> arc4.UInt64:
    #     return app_a.id
    
    # @arc4.abimethod
    # def get_app_address(self, app_a:Application) -> arc4.Address:
    #     return app_a.address
    
    # @arc4.abimethod
    # def get_creator_app(self, app_a: Application) -> arc4.Account
    #     return app_a.creator

            
# from algopy import ARC4Contract, String, arc4
# from  algopy.arc4 import abimethod

# explicit type annotation, algorand-python, @abimethod
# if method return explicitly define the returned type if non use None, ABI, ARC4 Stnadard, ARC4 Smart Contract, ARC Application
# ARC4 Smart Contract, router,  ARC32 ABI,




# Hardcoded values
# SMART_CARD_NUMBER = "0982761542"
# AC

# class SmartCardManagement(ARC4Contract):
#     @staticmethod
#     def format_card_number(card_number: str) -> Bytes:
#         formatted = card_number.replace(" ", "").strip()
#         return Bytes(formatted.encode())


# class SmartCardRegistryContract(ARC4Contract):
#     # Hardcoded Constants
#     SMART_CARD_NUMBER: Bytes = Bytes(b"0982761542")
    
#     # Use string for Address initialization
#     ACCOUNT_ADDRESS: Address = Address("YJI7KFSNWVJRAWW2Z7OB27PHU3AXD356YRDQVJSIZAWW32SWZ5VWRWAXZY")
    
#     # Use string for Admin Address
#     ADMIN_ADDRESS: Address = Address("FBA3RUWOUUEOCMECZF7SXSUDRMROT3BI4UPWLUQZ4OYGSFTI5TCKYSXDWA")

#     def __init__(self) -> None:
#         # Local state for storing smart card data
#         self.registered_cards = LocalState(Bytes, key="card_reg")
#         self.card_owners = LocalState(Address, key="card_owner")

#     @subroutine
#     def register_predefined_smart_card(self) -> None:
#         """
#         Register the predefined smart card with hardcoded details
#         """
#         # Ensure only admin can register
#         assert Txn.sender == self.ADMIN_ADDRESS, "Unauthorized registration"

#         # Register card with predefined details
#         self.registered_cards[Txn.sender] = self.SMART_CARD_NUMBER
#         self.card_owners[Txn.sender] = self.ACCOUNT_ADDRESS

#         # Log registration
#         log("Predefined Smart Card Registered")
#         log(f"Card Number: {self.SMART_CARD_NUMBER}")
#         log(f"Account Address: {self.ACCOUNT_ADDRESS}")

#     @subroutine
#     def validate_smart_card(self, card_number: Bytes) -> bool:
#         """
#         Validate if the provided card number matches the predefined card
        
#         Args:
#             card_number: Card number to validate
        
#         Returns:
#             Boolean indicating card validity
#         """
#         # Direct comparison with hardcoded card number
#         is_valid = card_number == self.SMART_CARD_NUMBER
        
#         log(f"Card Validation Result: {is_valid}")
#         return is_valid

#     @subroutine
#     def get_card_details(self) -> tuple[Bytes, Address]:
#         """
#         Retrieve predefined card details
        
#         Returns:
#             Tuple of (smart card number, account address)
#         """
#         return (
#             self.SMART_CARD_NUMBER, 
#             self.ACCOUNT_ADDRESS
#         )

#     @subroutine
#     def advanced_card_verification(
#         self, 
#         card_number: Bytes, 
#         account: Account
#     ) -> bool:
#         """
#         Advanced card verification with multiple checks
        
#         Args:
#             card_number: Card number to verify
#             account: Account performing verification
        
#         Returns:
#             Boolean indicating comprehensive verification
#         """
#         # Multiple verification steps
#         checks = [
#             # Check card number matches
#             self.validate_smart_card(card_number),
            
#             # Optional: Additional custom verification logic
#             # Use .length property for Bytes
#             card_number.length == self.SMART_CARD_NUMBER.length,
            
#             # Optional: Sender authorization check
#             Txn.sender == account
#         ]

#         # All checks must pass
#         verification_result = all(checks)
        
#         log(f"Advanced Verification Result: {verification_result}")
#         return verification_result

#     @subroutine
#     def generate_card_hash(self) -> Bytes:
#         """
#         Generate a unique hash for the smart card
        
#         Returns:
#             Bytes representing card hash
#         """
#         # Convert Address to raw bytes directly
#         account_bytes = self.ACCOUNT_ADDRESS.bytes
#         print(account_bytes, 'account_bytes')
        
#         # Concatenate using raw bytes
#         raw_data = self.SMART_CARD_NUMBER + Bytes(account_bytes)
        
#         # In real-world, use cryptographic hash function
#         # This is a simplified example
#         return raw_data[:32]  # Truncate to 32 bytes
        

# class SmartCardManagement:
#     @staticmethod
#     def format_card_number(card_number: str) -> Bytes:
#         """
#         Utility method to format card number
        
#         Args:
#             card_number: Raw card number string
        
#         Returns:
#             Formatted Bytes representation
#         """
#         # Remove spaces, standardize format
#         formatted = card_number.replace(" ", "").strip()
#         return Bytes(formatted.encode())




# # Example Usage Patterns
# def example_usage():
#     contract = SmartCardRegistryContract()
    
#     # Register Predefined Card
#     contract.register_predefined_smart_card()
    
#     # Validate Card
#     is_valid = contract.validate_smart_card(
#         SmartCardManagement.format_card_number("02323xxxxx")
#     )
    
#     # Advanced Verification
#     verification_result = contract.advanced_card_verification(
#         SmartCardManagement.format_card_number("02323xxxxx"),
#         Txn.sender
#     )






# class StoreSmartCardContract(ARC4Contract):
#     def __init__(self) -> None:
#         self.local = LocalState(Bytes)
#         self.local_with_metadata = LocalState(UInt64, key = "lwm", description = "Local with metadata")

#     @subroutine
#     def get_guaranteed_data(self, for_account: Account) -> Bytes:
#         return self.local[for_account]

#     @subroutine
#     def get_data_with_default(self, for_account: Account, default: Bytes) -> Bytes:
#         return self.local.get(for_account, default)

#     @subroutine
#     def get_data_or_assert(self, for_account: Account) -> Bytes:
#         result, exists = self.local.maybe(for_account)
#         assert exists, "no data for account"
#         return result

#     @subroutine
#     def set_data(self, for_account: Account, value: Bytes) -> None:
#         self.local[for_account] = value

#     @subroutine
#     def delete_data(self, for_account: Account) -> None:
#         del self.local[for_account]

#     def __init__(self) -> None:
#         # Define local state variables with `LocalState`
#         self.smart_card_key = LocalState(UInt512)
#         self.sender_key = LocalState(Address)
#         self.account_key = LocalState(Address)

#     @subroutine
#     def store_smart_card_number(self) -> bool:
#         log("Starting to Store Smart Card Number")
#         sender_address = Address(Txn.sender)
#         log("Transaction Sender Address: " + str(sender_address))

#         # Convert hardcoded values to appropriate types
#         smart_card_number = UInt512(int(SMART_CARD_NUMBER))
#         account_address = Address(ACCOUNT_ADDRESS)

#         # Store the sender address
#         self.sender_key[sender_address] = sender_address
#         log("Sender Address Stored in Local State")

#         # Store the account address in local state
#         self.account_key[sender_address] = account_address
#         log("Account Address Stored in Local State: " + str(account_address))

#         # Store the smart card number in local state
#         self.smart_card_key[sender_address] = smart_card_number
#         log("Smart Card Number Stored in Local State: " + str(smart_card_number))

#         log("Storage of Smart Card Number Completed")
#         return True

# # Example usage
# contract = StoreSmartCardContract()
# result = contract.store_smart_card_number()COUNT_ADDRESS = "YJI7KFSNWVJRAWW2Z7OB27PHU3AXD356YRDQVJSIZAWW32SWZ5VWRWAXZY"
# self.SMART_CARD_NUMBER: Bytes = Bytes(b"0982761542")
# self.ACCOUNT_ADDRESS: Address = Address("YJI7KFSNWVJRAWW2Z7OB27PHU3AXD356YRDQVJSIZAWW32SWZ5VWRWAXZY")
# self.ADMIN_ADDRESS: Address = Address("FBA3RUWOUUEOCMECZF7SXSUDRMROT3BI4UPWLUQZ4OYGSFTI5TCKYSXDWA")




# class SmartCardRegistryContract(ARC4Contract):
#     def __init__(self) -> None:
#         self.SMART_CARD_NUMBER: Bytes = Bytes(b"0982761542")
#         self.ACCOUNT_ADDRESS: Address = Address("YJI7KFSNWVJRAWW2Z7OB27PHU3AXD356YRDQVJSIZAWW32SWZ5VWRWAXZY")
#         self.ADMIN_ADDRESS: Address = Address("FBA3RUWOUUEOCMECZF7SXSUDRMROT3BI4UPWLUQZ4OYGSFTI5TCKYSXDWA")

#         self.registered_cards = LocalState(Bytes, key="card_reg")
#         self.card_owners = LocalState(Address, key="card_owner")

#     @subroutine
#     def register_predefined_smart_card(self) -> None:
#         assert Txn.sender == self.ADMIN_ADDRESS, "Unauthorized registration"
#         self.registered_cards[Txn.sender] = self.SMART_CARD_NUMBER
#         self.card_owners[Txn.sender] = self.ACCOUNT_ADDRESS

#         # log("Predefined Smart Card Registered")
#         # log("Card Number: " + bytes(self.SMART_CARD_NUMBER).hex())  # Updated line
#         # log("Account Address: " + str(self.ACCOUNT_ADDRESS))

#     @subroutine
#     def validate_smart_card(self, card_number: Bytes) -> bool:
#         is_valid = card_number == self.SMART_CARD_NUMBER
#         # log("Card Validation Result: " + str(is_valid))
#         return is_valid

#     @subroutine
#     def get_card_details(self) -> Tuple[Bytes, Address]:
#         return (self.SMART_CARD_NUMBER, self.ACCOUNT_ADDRESS)

#     @subroutine
#     def advanced_card_verification(
#         self,
#         card_number: Bytes,
#         account: Address  # Changed from Account to Address
#     ) -> bool:
#         checks = (
#             self.validate_smart_card(card_number),
#             card_number.length == self.SMART_CARD_NUMBER.length,
#             Txn.sender == account
#         )
#         verification_result = all(checks)
        
#         log("Advanced Verification Result: " + str(verification_result))
#         return verification_result

#     @subroutine
#     def generate_card_hash(self) -> Bytes:
#         account_bytes = self.ACCOUNT_ADDRESS.bytes
#         raw_data = self.SMART_CARD_NUMBER + account_bytes
        
#         # Here you would typically use a hashing function instead of truncation.
#         return raw_data[:32]  # Truncate to 32 bytes
