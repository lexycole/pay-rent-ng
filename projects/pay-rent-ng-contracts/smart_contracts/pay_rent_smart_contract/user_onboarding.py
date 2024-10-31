from pyteal import *

def user_onboarding_app():
    """
    Smart contract for user onboarding on the Algorand blockchain.
    """

    # Global state
    is_user_onboarded = Bytes("is_user_onboarded")

    @Subroutine(TealType.none)
    def onboard_user():
        """
        Subroutine to onboard a new user.
        """
        return Seq(
            App.globalPut(is_user_onboarded, Bytes("true")),
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
        [Txn.application_id() == Int(0), onboard_user()],
        [Txn.application_id() != Int(0), is_user_onboarded_check()]
    )

    return program

if __name__ == "__main__":
    print(compileTeal(user_onboarding_app(), Mode.Application, version=6))