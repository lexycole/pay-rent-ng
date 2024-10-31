from pyteal import *
from utils import transfer_algo, transfer_asa

def payment_process_app():
    """
    Smart contract to handle the payment process and service activation.
    """
    # Global state
    is_user_onboarded = Bytes("is_user_onboarded")
    iuc_to_ipfs_hash = Dict(TealType.bytes, TealType.bytes)
    iuc_to_wallet = Dict(TealType.bytes, TealType.bytes)
    subscription_packages = Array(TealType.bytes)
    subscription_status = Dict(TealType.bytes, TealType.uint64)

    # Event
    ServiceActivated = Bytes("ServiceActivated")

    @Subroutine(TealType.none)
    def onboard_user(iuc: Bytes, wallet_address: Bytes):
        """
        Subroutine to onboard a new user and register their IUC.
        """
        ipfs_hash = upload_to_ipfs({"IUC": iuc, "AlgorandAddress": wallet_address, "Timestamp": Bytes(IntToBytes(Global.latest_timestamp()))})
        return Seq(
            App.globalPut(is_user_onboarded, Bytes("true")),
            iuc_to_ipfs_hash.put(iuc, ipfs_hash),
            iuc_to_wallet.put(iuc, wallet_address),
            Approve()
        )

    @Subroutine(TealType.uint64)
    def is_user_onboarded_check(iuc: Bytes):
        """
        Subroutine to check if a user is onboarded and their IUC is linked to the wallet.
        """
        return Cond(
            [App.globalGet(is_user_onboarded) == Bytes("true") and iuc_to_wallet.get(iuc) == Txn.sender(), Int(1)],
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

    @Subroutine(TealType.none)
    def process_payment(iuc: Bytes, package_index: Int, is_algo: Int):
        """
        Subroutine to process the payment for a subscription package.
        """
        package_details = subscription_packages[package_index]
        payment_amount = extract_payment_amount(package_details)
        wallet_address = iuc_to_wallet.get(iuc)

        return Seq(
            If(is_algo == Int(1),
               transfer_algo(wallet_address, payment_amount),
               transfer_asa(wallet_address, payment_amount)),
            subscription_status.put(iuc, Int(1)),
            Log(ServiceActivated),
            Approve()
        )

    program = Cond(
        [Txn.application_id() == Int(0), onboard_user(Txn.application_args[0], Txn.sender())],
        [Txn.application_args[0] == Bytes("is_onboarded"), is_user_onboarded_check(Txn.application_args[1])],
        [Txn.application_args[0] == Bytes("add_package"), add_subscription_package(Txn.application_args[1])],
        [Txn.application_args[0] == Bytes("get_packages"), get_subscription_packages()],
        [Txn.application_args[0] == Bytes("process_payment"),
         process_payment(Txn.application_args[1], Btoi(Txn.application_args[2]), Btoi(Txn.application_args[3]))]
    )

    return program

if __name__ == "__main__":
    print(compileTeal(payment_process_app(), Mode.Application, version=6))