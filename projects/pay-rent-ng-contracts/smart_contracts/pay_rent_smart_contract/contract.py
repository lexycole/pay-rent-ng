from algopy.arc4 import ARC4Contract, Address, UInt512, BigUIntN
from algopy import log, Txn, LocalState, subroutine, Bytes, Account, Bytes, UInt64
# from typing import Literal

# Hardcoded values
SMART_CARD_NUMBER = "0982761542"
ACCOUNT_ADDRESS = "YJI7KFSNWVJRAWW2Z7OB27PHU3AXD356YRDQVJSIZAWW32SWZ5VWRWAXZY"

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


class StoreSmartCardContract(ARC4Contract):
    def __init__(self) -> None:
        self.local = LocalState(Bytes)
        self.local_with_metadata = LocalState(UInt64, key="lwm", description="Local with metadata")
        log("Initialized StoreSmartCardContract with local state variables.")

    @subroutine
    def get_guaranteed_data(self, for_account: Account) -> Bytes:
        data = self.local[for_account]
        log("Retrieved guaranteed data for account ", for_account, ": ", data)
        return data

    @subroutine
    def get_data_with_default(self, for_account: Account, default: Bytes) -> Bytes:
        data = self.local.get(for_account, default)
        log("Retrieved data for account ", for_account, " with default: ", data)
        return data

    @subroutine
    def get_data_or_assert(self, for_account: Account) -> Bytes:
        result, exists = self.local.maybe(for_account)
        assert exists, "no data for account"
        log("Data exists for account ", for_account, ": ", result)
        return result

    @subroutine
    def set_data(self, for_account: Account, value: Bytes) -> None:
        self.local[for_account] = value
        log("Set data for account ", for_account, " to: ", value)

    @subroutine
    def delete_data(self, for_account: Account) -> None:
        del self.local[for_account]
        log("Deleted data for account ", for_account)


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
# result = contract.store_smart_card_number()