
from solcx import compile_standard,install_solc
install_solc("0.6.0")
import json
from web3 import Web3
import os
from dotenv import load_dotenv
load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
   # print(simple_storage_file)

# Complie Our Solidity
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        },
    },
    solc_version = "0.6.0",
)
#print(compiled_sol)

with open("compiled_code.json","w") as file:
    json.dump(compiled_sol,file)

    #get bytecode
    bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

    #get abi
    abi =  compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

    # for connecting to ganache
    w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/48d51ed754294adc943b2cb901e9bbc0"))
    chain_id = 4
    my_address = "0xd1f34f741fB52df75A2f002DCEE94Fc2aBCf9597"
  #  private_key = os.getenv("PRIVATE_KEY")
    private_key = "0xa90a11a895e988dbc42c5253e609588900ef0c96abf278d37c1ad689898902af"
    print(private_key)
    #Create the contract in python
    SimpleStorage = w3.eth.contract(abi=abi,bytecode=bytecode)
   # print(SimpleStorage)
    #Get the latest test transactionn
    nonce = w3.eth.getTransactionCount(my_address)
   # print(nonce)
    #1. Build a transaction
    #2. Sign a transaction
    #3. Send a transaction
    transaction = SimpleStorage.constructor().buildTransaction(
        {   "gasPrice":w3.eth.gas_price,
            "chainId":w3.eth.chain_id,
            "from":my_address,
            "nonce":nonce
            }
        )
   # print(transaction)
    signed_txn = w3.eth.account.sign_transaction(transaction,private_key = private_key)
    
   #send this signed transaction
    print("Deploying contract...")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Deployed")
    #Working with the contract
    #Contract Address
    #Contract ABI
    simple_storage = w3.eth.contract(address=tx_receipt.contractAddress,abi=abi)
    #call -> Simulate making teh call and getting a return value (blue buttons,these dont make a state change)
    #transact -> Actually make a state change (orange button, these changes the state in blockchain)

    #initial value of favorite number
    print(simple_storage.functions.retrieve().call())
    print("Updating contract")
    store_transaction = simple_storage.functions.store(15).buildTransaction(
       { "gasPrice":w3.eth.gas_price,
        "chainId":chain_id,
        "from":my_address,
        "nonce":nonce+1
        }
   )    
    signed_store_txn = w3.eth.account.sign_transaction(store_transaction,private_key=private_key)
    send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
    print("Updated!!")
    print(simple_storage.functions.retrieve().call())
