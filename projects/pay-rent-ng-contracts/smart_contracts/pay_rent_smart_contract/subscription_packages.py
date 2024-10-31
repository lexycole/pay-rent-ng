from fastapi import FastAPI, HTTPException
from pyteal import compileTeal, Mode
from .subscription_packages_contract import subscription_packages_app

app = FastAPI()

@app.post("/register_iuc")
def register_iuc(iuc: str, wallet_address: str):
    """
    Endpoint to register a user's IUC.
    """
    try:
        teal_code = compileTeal(subscription_packages_app(), Mode.Application, version=6)
        # Deploy the smart contract to the Algorand blockchain
        contract_address = deploy_contract(teal_code)
        # Call the onboard_user subroutine to register the IUC
        register_user(contract_address, iuc, wallet_address)
        return {"message": "IUC registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/is_user_onboarded")
def is_user_onboarded(wallet_address: str):
    """
    Endpoint to check if a user is onboarded.
    """
    try:
        teal_code = compileTeal(subscription_packages_app(), Mode.Application, version=6)
        is_onboarded = check_user_onboarded(teal_code, wallet_address)
        return {"is_onboarded": is_onboarded}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subscription_packages")
def get_subscription_packages():
    """
    Endpoint to get all available subscription packages.
    """
    try:
        teal_code = compileTeal(subscription_packages_app(), Mode.Application, version=6)
        packages = get_available_packages(teal_code)
        return {"packages": packages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def deploy_contract(teal_code):
    """
    Deploy the smart contract to the Algorand blockchain.
    """
    # Implementation details omitted for brevity
    return "contract_address"

def register_user(contract_address, iuc, wallet_address):
    """
    Call the onboard_user subroutine to register a user's IUC.
    """
    # Implementation details omitted for brevity
    pass

def check_user_onboarded(teal_code, wallet_address):
    """
    Check if a user is onboarded.
    """
    # Implementation details omitted for brevity
    return True

def get_available_packages(teal_code):
    """
    Call the get_subscription_packages subroutine to fetch all available packages.
    """
    # Implementation details omitted for brevity
    return ["Premium", "Premium + Xtraview", "Premium + Showmax", "Confam + Xtraview"]