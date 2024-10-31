from pyteal import *

def subscription_packages_app():
    """
    Smart contract to manage subscription packages.
    """
    # Global state
    is_user_onboarded = Bytes("is_user_onboarded")
    iuc_to_ipfs_hash = Dict(TealType.bytes, TealType.bytes)
    subscription_packages = Array(TealType.bytes)

    @Subroutine(TealType.none)
    def onboard_user(iuc: Bytes, wallet_address: Bytes):
        """
        Subroutine to onboard a new user and register their IUC.
        """
        ipfs_hash = upload_to_ipfs({"IUC": iuc, "AlgorandAddress": wallet_address, "Timestamp": Bytes(IntToBytes(Global.latest_timestamp()))})
        return Seq(
            App.globalPut(is_user_onboarded, Bytes("true")),
            iuc_to_ipfs_hash.put(iuc, ipfs_hash),
            Approve()
        )

    @Subroutine(TealType.uint64)
    def is_user_onboarded_check():
        """
        Subroutine to check if a user is onboarded.
        """
        return Cond(
            [App.globalGet(is_user_onboarded) == Bytes("true"), Int(1)],
            [Int(1) == Int(1), Int(0)]
        )

    @Subroutine(TealType.none)
    def add_subscription_package(package_details: Bytes):
        """
        Subroutine to add a new subscription package.
        """
        return Seq(
            subscription_packages.append(package_details),
            Approve()
        )

    @Subroutine(TealType.bytes)
    def get_subscription_packages():
        """
        Subroutine to get all available subscription packages.
        """
        return subscription_packages.load()

    program = Cond(
        [Txn.application_id() == Int(0), onboard_user(Txn.application_args[0], Txn.sender())],
        [Txn.application_id() != Int(0), is_user_onboarded_check()],
        [Txn.application_args[0] == Bytes("add_package"), add_subscription_package(Txn.application_args[1])],
        [Txn.application_args[0] == Bytes("get_packages"), get_subscription_packages()]
    )

    return program

if __name__ == "__main__":
    print(compileTeal(subscription_packages_app(), Mode.Application, version=6))