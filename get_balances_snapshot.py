import json
from web3 import Web3
import sys
import warnings
from waiting import wait

if not sys.warnoptions:
    warnings.simplefilter("ignore")

w3 = Web3(Web3.HTTPProvider('https://smartbch.fountainhead.cash/mainnet'))
wait(lambda: w3.isConnected(), timeout_seconds=10, waiting_for="Node to be ready")
if not w3.isConnected():
    w3 = Web3(Web3.HTTPProvider('https://global.uat.cash'))
    wait(lambda: w3.isConnected(), timeout_seconds=10, waiting_for="Node to be ready")
if not w3.isConnected():
    w3 = Web3(Web3.HTTPProvider('https://smartbch.grey.at'))
    wait(lambda: w3.isConnected(), timeout_seconds=10, waiting_for="Node to be ready")

target_token_address = w3.toChecksumAddress(
    "0xF05bD3d7709980f60CD5206BddFFA8553176dd29")  # SIDX smart contract address
ignored_addresses = [target_token_address, '0x0000000000000000000000000000000000000000', '0xd11bb6a7981780aADc722146a306f7104fD93E9c', '0xE1ae30Fbb31bE2FB59D1c44dBEf8649C386E26B3']  # Added admin and portfolio wallet
address_list = []
balances = {}
LP_CA_list = []  # Liquidity pools address list will be added by the app, you can add manually if anyone is missing.
lp_factories = {"benswap": {"address": "0x8d973bAD782c1FFfd8FcC9d7579542BA7Dd0998D", "start_block": 295042},
                "mist": {"address": "0x6008247F53395E7be698249770aa1D2bfE265Ca0", "start_block": 989302},
                "muesliswap": {"address": "0x72cd8c0B5169Ff1f337E2b8F5b121f8510b52117", "start_block": 770000},
                "tangoswap": {"address": "0x2F3f70d13223EDDCA9593fAC9fc010e912DF917a", "start_block": 1787259},
                "emberswap": {"address": "0xE62983a68679834eD884B9673Fb6aF13db740fF0", "start_block": 3157682},
                "blockng": {"address": "0x3A2643c00171b1EA6f6b6EaC77b1E0DdB02c3a62", "start_block": 3622020}} # Factories for every DEX

createPair_topic = ["0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9"]

farms = {"BEN": ["0xDEa721EFe7cBC0fCAb7C8d65c598b21B6373A2b6"], #Benswap
         "SUSHI": ["0x3A7B9D0ed49a90712da4E087b17eE4Ac1375a5D4", #Mistswap
                   "0x38cC060DF3a0498e978eB756e44BD43CC4958aD9", #Tangoswap
                   "0x8ecb32C33AB3f7ee3D6Ce9D4020bC53fecB36Be9"] #Emberswap
         } # Master contracts

'''BlockNG factory works as any UniswapV2 factory, but farms are quite different: every farm has a dedicated contract'''
BlockNG_SIDX_LAW_LP = "0x1CD36D9dEd958366d17DfEdD91b5F8e682D7f914"
BlockNG_SIDX_LAW_farm = "0x3384d970688f7B86a8D7aE6D8670CD5f9fd5fE1E"
def get_liquidity_pools():
    ABI = open("ABIs/UniswapV2Factory.json", "r")  # Standard ABI for LP factories
    abi = json.loads(ABI.read())
    for factory in lp_factories:
        factory_contract = w3.eth.contract(address=lp_factories[factory]["address"], abi=abi)
        logs = w3.eth.get_logs({'topic': createPair_topic, 'address': lp_factories[factory]["address"],
                                'fromBlock': lp_factories[factory]["start_block"]})
        for i in range(len(logs)):
            tx_hash = logs[i].transactionHash
            receipt = w3.eth.getTransactionReceipt(tx_hash)
            pair = factory_contract.events.PairCreated().processReceipt(receipt)
            if pair[0].args.token0 == target_token_address or pair[0].args.token1 == target_token_address:
                LP_CA_list.append(pair[0].args.pair)

def get_LPs_info(LP_CA_list, target_token_address):
    ABI = open("ABIs/UniswapV2Pair.json", "r")  # Standard ABI for LP tokens
    abi = json.loads(ABI.read())
    LPs_dict = {}

    for LP in LP_CA_list:
        contract = w3.eth.contract(address=w3.toChecksumAddress(LP), abi=abi)
        target_token_position = 0
        target_token_reserves = 0
        if contract.functions.token1().call() == target_token_address:
            target_token_position = 1
        if target_token_position == 0:
            target_token_reserves = contract.functions.getReserves().call()[0]
        if target_token_position == 1:
            target_token_reserves = contract.functions.getReserves().call()[1]
        LPs_dict[LP] = {
            "total_supply": contract.functions.totalSupply().call(),
            "decimals": contract.functions.decimals().call(),
            "target_token_position": target_token_position,
            "target_token_reserve": target_token_reserves
        }
    return LPs_dict

def address_tracker(data):
    for block_number in data["blocks"]:
        for txhash in data["blocks"][block_number]:
            for tx in data["blocks"][block_number][txhash]:
                if data["blocks"][block_number][txhash][tx]["to"] not in address_list:
                    address_list.append(data["blocks"][block_number][txhash][tx]["to"])
                if data["blocks"][block_number][txhash][tx]["from"] not in address_list and \
                        data["blocks"][block_number][txhash][tx]["from"] not in ignored_addresses:
                    address_list.append(data["blocks"][block_number][txhash][tx]["from"])

    for LP in LP_CA_list:
        if LP in address_list:
            address_list.remove(w3.toChecksumAddress(LP))  # We delete balances hold in LP tokens

    for address in ignored_addresses:
        if address in address_list:
            address_list.remove(address)

def get_farms(LP_CA_list):
    LPs_in_farms = {} # LP_address: [(user_address1: LP_amount1), (user_address2: LP_amount2)...]
    PCK_ABI_FILE = open("ABIs/PCK-Master-ABI.json", "r")
    PCK_abi = json.loads(PCK_ABI_FILE.read())
    BEN_ABI_FILE = open("ABIs/BEN-Master-ABI.json", "r")
    BEN_abi = json.loads(BEN_ABI_FILE.read())
    SUSHI_ABI_FILE = open("ABIs/SUSHI-Master-ABI.json", "r")
    SUSHI_abi = json.loads(SUSHI_ABI_FILE.read())
    for dex_base in farms:
        if dex_base == "BEN":
            abi = BEN_abi
        if dex_base == "PANCAKE":
            abi = PCK_abi
        if dex_base == "SUSHI":
            abi = SUSHI_abi
        for master_contract in farms[dex_base]:
            contract = w3.eth.contract(address=w3.toChecksumAddress(master_contract), abi=abi)
            pool_length = contract.functions.poolLength().call()
            for i in range(pool_length):
                if contract.functions.poolInfo(i).call()[0] in LP_CA_list:
                    LPs_in_farms[contract.functions.poolInfo(i).call()[0]] = []
                    for address in address_list:
                        LP_amount = contract.functions.userInfo(i, address).call()[0]
                        if LP_amount != 0:
                            LPs_in_farms[contract.functions.poolInfo(i).call()[0]].append((address, LP_amount))
                if contract.functions.poolInfo(i).call()[0] == target_token_address: # This is a single token pool
                    for address in address_list:
                        token_balance = contract.functions.userInfo(i, address).call()[0]
                        if token_balance != 0:
                            balances[address] = token_balance

    # Now it's time to get SIDX/LAW farmed in blockNG
    LPs_in_farms[BlockNG_SIDX_LAW_LP] = []
    ABI = open("ABIs/BlockNG-farm.json")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=BlockNG_SIDX_LAW_farm, abi=abi)
    for address in address_list:
        LP_amount = contract.functions.balanceOf(address).call()
        if LP_amount != 0:
            LPs_in_farms[BlockNG_SIDX_LAW_LP].append((address, LP_amount))

    return LPs_in_farms

def get_LP_balances(LPs_dict, LPs_in_farms):
    for LP_address in LP_CA_list:
        ABI = open("ABIs/UniswapV2Pair.json", "r")  # Standard ABI for LP tokens
        abi = json.loads(ABI.read())
        contract = w3.eth.contract(address=LP_address, abi=abi)
        for address in address_list:
            address_LP_balance = contract.functions.balanceOf(w3.toChecksumAddress(address)).call()
            if address_LP_balance != 0 and address in balances: # This means this wallet holds single stacking pool
                balances[address] += (address_LP_balance / LPs_dict[LP_address]["total_supply"]) * LPs_dict[LP_address][
                    "target_token_reserve"]
            if address_LP_balance != 0 and address not in balances:
                balances[address] = (address_LP_balance / LPs_dict[LP_address]["total_supply"]) * LPs_dict[LP_address][
                    "target_token_reserve"]
        if LP_address in LPs_in_farms:
            for i in range(len(LPs_in_farms[LP_address])):
                owner = LPs_in_farms[LP_address][i][0]
                balance = (LPs_in_farms[LP_address][i][1] / LPs_dict[LP_address]["total_supply"]) * LPs_dict[LP_address]["target_token_reserve"]
                if owner in balances: # In this case, the owner holds LP in his/her wallet
                    balances[owner] += balance
                else:
                    balances[owner] = balance


def get_balances(proposal_id):
    total_token_amount = 0
    ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=target_token_address, abi=abi)
    decimals = contract.functions.decimals().call()
    for address in address_list:
        balance = contract.functions.balanceOf(address).call()
        if address in balances: # In this case, the address holds tokens in LP contract
            balances[address] += balance  # Add balance from the LP tokens
        else:
            if balance > 0:
                balances[address] = balance

    for address in balances:
        if balances[address] > 0:
            balances[address] = balances[address] / 10 ** decimals
            total_token_amount += balances[address]

    if total_token_amount <= 179000:
        print(f"Total token amount available for voting is {total_token_amount}")
    else:
        print(f"Warning, total token amount available for voting is {total_token_amount} but it's expected to be lower.")

    with open(f'data/balances/{proposal_id}.json', 'w') as file:
        json.dump(balances, file)

def main(proposal_id):
    try:
        file = open("data/balances/transfer_events.json", "r")
        transfer_data = json.load(file)
    except FileNotFoundError:
        print("File with contract events doesn't exist")
    print("Getting liquidity pools for your token, this may take a while")
    get_liquidity_pools()
    print(f"Just for your information, these are the {len(LP_CA_list)} liquidity pools detected for your token:")
    print(LP_CA_list)
    LPs_dict = get_LPs_info(LP_CA_list, target_token_address)
    address_tracker(transfer_data)
    print("Scanning for farms...")
    LPs_in_farms = get_farms(LP_CA_list)
    get_LP_balances(LPs_dict, LPs_in_farms)
    print("Now getting all balances, please be patient")
    get_balances(proposal_id)
    print("Done")
