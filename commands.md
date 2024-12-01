uvicorn smart_contracts._helper.api:app --reload --port 8000

python -m smart_contracts serve

python -m smart_contracts build pay_rent_smart_contract

python -m smart_contracts deploy pay_rent_smart_contract

<!-- CONTRACT CLASS -->
class HelloWorld (ARC4Contract):
    @abimethod
    def hello(self) -> String:
        return



algokit localnet console
goal account list

 


(pay-rent-ng-contracts-py3.13) mac@MACs-MacBook-Pro pay-rent-ng-contracts % python -m smart_contracts deploy  pay_rent_smart_contract
2024-11-24 23:02:51,110 INFO      : Loading .env
2024-11-24 23:02:51,111 INFO      : Deploying app pay_rent_smart_contract
2024-11-24 23:02:51,193 DEBUG     : SmartCardContract found in FBA3RUWOUUEOCMECZF7SXSUDRMROT3BI4UPWLUQZ4OYGSFTI5TCKYSXDWA account, with app id 1004, version=v1.0.
2024-11-24 23:02:51,196 INFO      : No detected changes in app, nothing to do.
Application ID: 1004
Application Address: SW4BTZGCCNMSDYSANRLKFQOZNYRKH4B7J6DNSEUAYPSRGOYZRGKQEAW5EY
(pay-rent-ng-contracts-py3.13) mac@MACs-MacBook-Pro pay-rent-ng-contracts % 


uvicorn smart_contracts._helper.api:app --reload


from pay_rent_ng.smart_contracts.__main__ import main


uvicorn smart_contracts._helpers.api:app --reload

import sys
sys.path.append('/Users/mac/Algorand, native features and Using algokit utils to interact with the chain/PayRentNG/real/pay-rent-ng/projects/pay-rent-ng-contracts')


uvicorn smart_contracts._helpers.api:app --reload

goal node status
goal  account list
goal clerk send \
  -f R5LYLFGLJTWZFRTADCK6TQ67QKOWYVSSNBPLJGBS6EWILVMAWKCVW743PM \
  -t R5LYLFGLJTWZFRTADCK6TQ67QKOWYVSSNBPLJGBS6EWILVMAWKCVW743PM \
  -a 1000000  # This sends 1 Algo (1,000,000 microAlgos)

# Check balance directly in Docker
docker exec algokit_sandbox_algod goal account list

docker logs algokit_sandbox_algod | grep -i "a"

docker logs algokit_sandbox_algod | grep -C 2 "a"
    


goal account export -a FBA3RUWOUUEOCMECZF7SXSUDRMROT3BI4UPWLUQZ4OYGSFTI5TCKYSXDWA


algokit project run build
the upload the arc32.json


Error fetching smart card number: TransactionPool.Remember: transaction CIVAQYOHNEF3GEPSFLLZIOBKBNYDSPB2ZI553KCLS5WH5GM7VQZA: only ClearState is supported for an application (1004) that does not exist

{
    "detail": "TransactionPool.Remember: transaction BP4UGTYUAHMMBFCNS5AVVVLOOZTYWDNVS6VIZ4IU7E37KKGWVK3A: only ClearState is supported for an application (1004) that does not exist"
}


{
    "status": "Success",
    "message": "Account brought online",
    "transaction_id": "63PRC2A3ZBEDOXEGAQZDZ6W5ZNP2OAGJSFHIMIX6DR5DF4OQCGSA"
}

solution 
build again
to get the arc32.json 
upload to lora and follow the youtube to deploy.
 