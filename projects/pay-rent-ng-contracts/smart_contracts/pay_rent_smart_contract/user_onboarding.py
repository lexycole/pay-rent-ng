from pyteal import *
from utils import upload_to_ipfs

def user_onboarding_app():
    """
    Smart contract for user onboarding and IUC registration on the Algorand blockchain.
    """
    # Global state
    is_user_onboarded = Bytes("is_user_onboarded")
    iuc_to_ipfs_hash = Dict(TealType.bytes, TealType.bytes)

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

    program = Cond(
        [Txn.application_id() == Int(0), onboard_user(Txn.application_args[0], Txn.sender())],
        [Txn.application_id() != Int(0), is_user_onboarded_check()]
    )

    return program

if __name__ == "__main__":
    print(compileTeal(user_onboarding_app(), Mode.Application, version=6))