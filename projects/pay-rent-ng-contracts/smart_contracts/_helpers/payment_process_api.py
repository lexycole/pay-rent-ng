from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pyteal import compileTeal, Mode
from .payment_process_contract import payment_process_app
from typing import Dict

app = FastAPI()

@app.post("/register_iuc")
def register_iuc(iuc: str, wallet_address: str):
    """
    Endpoint to register a user's IUC.
    """
    try:
        teal_code = compileTeal(payment_process_app(), Mode.Application, version=6)
        # Deploy the smart contract to the Algorand blockchain
        contract_address = deploy_contract(teal_code)
        # Call the onboard_user subroutine to register the IUC
        register_user(contract_address, iuc, wallet_address)
        return {"message": "IUC registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/is_user_onboarded")
def is_user_onboarded(iuc: str, wallet_address: str):
    """
    Endpoint to check if a user is onboarded and their IUC is linked to the wallet.
    """
    try:
        teal_code = compileTeal(payment_process_app(), Mode.Application, version=6)
        is_onboarded = check_user_onboarded(teal_code, iuc, wallet_address)
        return {"is_onboarded": is_onboarded}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subscription_packages")
def get_subscription_packages():
    """
    Endpoint to get all available subscription packages.
    """
    try:
        teal_code = compileTeal(payment_process_app(), Mode.Application, version=6)
        packages = get_available_packages(teal_code)
        return {"packages": packages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_payment")
def process_payment(iuc: str, package_index: int, is_algo: bool):
    """
    Endpoint to process the payment for a subscription package.
    """
    try:
        teal_code = compileTeal(payment_process_app(), Mode.Application, version=6)
        contract_address = deploy_contract(teal_code)
        process_subscription_payment(contract_address, iuc, package_index, is_algo)
        return {"message": "Payment processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/service_activation")
async def service_activation(websocket: WebSocket):
    """
    Websocket endpoint to handle service activation.
    """
    await websocket.accept()
    try:
        while True:
            event = await get_service_activation_event()
            if event:
                iuc = event["iuc"]
                await websocket.send_json({"message": f"Service activated for IUC: {iuc}"})
    except WebSocketDisconnect:
        print("WebSocket connection closed")

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

def check_user_onboarded(teal_code, iuc, wallet_address):
    """
    Call the is_user_onboarded_check subroutine to verify if a user is onboarded and their IUC is linked to the wallet.
    """
    # Implementation details omitted for brevity
    return True

def get_available_packages(teal_code):
    """
    Call the get_subscription_packages subroutine to fetch all available packages.
    """
    # Implementation details omitted for brevity
    return ["Package 1", "Package 2", "Package 3"]

def process_subscription_payment(contract_address, iuc, package_index, is_algo):
    """
    Call the process_payment subroutine to process the payment for a subscription package.
    """
    # Implementation details omitted for brevity
    pass

async def get_service_activation_event() -> Dict:
    """
    Listen for the ServiceActivated event and return the event data.
    """
    # Implementation details omitted for brevity
    return {"iuc": "123456"}