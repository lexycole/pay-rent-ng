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
