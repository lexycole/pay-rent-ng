from fastapi import FastAPI, HTTPException
from pyteal import compileTeal, Mode
from .user_onboarding_contract import user_onboarding_app

app = FastAPI()

@app.get("/onboard_user")
def onboard_user():
    """
    Endpoint to onboard a new user.
    """
    try:
        teal_code = compileTeal(user_onboarding_app(), Mode.Application, version=6)
        # Deploy the smart contract to the Algorand blockchain
        contract_address = deploy_contract(teal_code)
        return {"contract_address": contract_address}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/is_user_onboarded")
def is_user_onboarded(wallet_address: str):
    """
    Endpoint to check if a user is onboarded.
    """
    try:
        teal_code = compileTeal(user_onboarding_app(), Mode.Application, version=6)
        is_onboarded = check_user_onboarded(teal_code, wallet_address)
        return {"is_onboarded": is_onboarded}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def deploy_contract(teal_code):
    """
    Deploy the smart contract to the Algorand blockchain.
    """
    # Implementation details omitted for brevity
    return "contract_address"

def check_user_onboarded(teal_code, wallet_address):
    """
    Check if a user is onboarded.
    """
    # Implementation details omitted for brevity
    return True