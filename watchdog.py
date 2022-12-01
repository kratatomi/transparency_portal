import json

from tendo.singleton import SingleInstanceException
from web3 import Web3
import logging
import requests
import os

import engine

logger = logging.getLogger("app.engine")

RPC_SERVER = 'https://global.uat.cash'
w3 = Web3(Web3.HTTPProvider(RPC_SERVER))
if not w3.isConnected():
    RPC_SERVER = 'https://smartbch.grey.at'
    w3 = Web3(Web3.HTTPProvider(RPC_SERVER))

ETF_watchdog_address = "0xd2edf72FE051571A85466F95b6Cab1C0a31601c6"
ETF_portfolio_address = engine.ETF_portfolio_address
ETF_SIDX_CA = "0x3c8caE0D65C75FAFdD75D5b5D0A75DFE73a9EEaa"

routers = {"Mistswap": "0x5d0bF8d8c8b054080E2131D8b260a5c6959411B8",
           "Tangoswap": "0xb93184fB3eEDb4d32150763578cA305488240c8e",
           "BlockNG-Kudos": "0xD301b5334912190493fa798Cf796440Cd9B33DB1",
           "BlockNG": "0xD301b5334912190493fa798Cf796440Cd9B33DB1",
           "Emberswap": "0x217057A8B0bDEb160829c19243A2E03bfe95555a"}

masters = {"Mistswap": "0x3A7B9D0ed49a90712da4E087b17eE4Ac1375a5D4",
           "Tangoswap": "0x38cC060DF3a0498e978eB756e44BD43CC4958aD9",
           "Emberswap": "0x8ecb32C33AB3f7ee3D6Ce9D4020bC53fecB36Be9"}

SIDX_liquidity_pools = {"Mistswap": {"lp_CA": "0x7E1B9F1e286160A80ab9B04D228C02583AeF90B5", "pool_id": 44},
        "BlockNG": {"lp_CA": "0x1CD36D9dEd958366d17DfEdD91b5F8e682D7f914"},
        "Tangoswap": {"lp_CA": "0x4509Ff66a56cB1b80a6184DB268AD9dFBB79DD53", "pool_id": 32},
        "Emberswap": {"lp_CA": "0x97dEAeB1A9A762d97Ac565cD3Ff7629CD6d55D09", "pool_id": 31}}

portfolio_fee = 1
admin_fee = 0.5
min_investment_amount = 0.2 #BCH
min_withdrawal_share = 0.005

class SBCH:
    ID = 0
    headers = {'Content-type': 'application/json'}
    payload = {"jsonrpc": "2.0",
               "method": "undefined",
               "params": [],
               "id": ID}
    session = requests.Session()
    topics = {"Transfer": Web3.keccak(text="Transfer(address,address,uint256)").hex(),
              "Approval": Web3.keccak(text="Approval(address,address,uint256)").hex(),
              "MinterAdded": Web3.keccak(text="MinterAdded(address)").hex(),
              "MinterRemoved": Web3.keccak(text="MinterRemoved(address)").hex()}

    def queryTxBySrc(self, address, start, end, txs_limit = 0):
        address = Web3.toChecksumAddress(address)
        if type(start) == int:
            start = hex(start)
        if type(end) == int:
            end = hex(end)
        if type(txs_limit) == int:
            txs_limit = hex(txs_limit)
        self.payload["method"] = "sbch_queryTxBySrc"
        self.payload["params"] = [address, start, end, txs_limit]
        self.get_response()

    def queryTxByDst(self, address, start, end = 'latest', txs_limit = 0):
        address = Web3.toChecksumAddress(address)
        if type(start) == int:
            start = hex(start)
        if type(end) == int:
            end = hex(end)
        if type(txs_limit) == int:
            txs_limit = hex(txs_limit)
        self.payload["method"] = "sbch_queryTxByDst"
        self.payload["params"] = [address, start, end, txs_limit]
        self.get_response()

    def queryTxByAddr(self, address, start, end = 'latest', txs_limit = 0):
        address = Web3.toChecksumAddress(address)
        if type(start) == int:
            start = hex(start)
        if type(end) == int:
            end = hex(end)
        if type(txs_limit) == int:
            txs_limit = hex(txs_limit)
        self.payload["method"] = "sbch_queryTxByAddr"
        self.payload["params"] = [address, start, end, txs_limit]
        self.get_response()

    def queryLogs(self, address, start, topics_array = [], end = 'latest', txs_limit = 0):
        address = Web3.toChecksumAddress(address)
        if type(start) == int:
            start = hex(start)
        if type(end) == int:
            end = hex(end)
        if type(txs_limit) == int:
            txs_limit = hex(txs_limit)
        if topics_array == []:
            topics_array = [SBCH.topics['Transfer']] # Get Transfer events logs by default
        self.payload["method"] = "sbch_queryLogs"
        self.payload["params"] = [address, topics_array, start, end, txs_limit]
        self.get_response()

    def getTxListByHeight(self, block_number):
        if type(block_number) == int:
            block_number = hex(block_number)
        self.payload["method"] = "sbch_getTxListByHeight"
        self.payload["params"] = [block_number]
        self.get_response()

    def getTxListByHeightWithRange(self, block_number, start_tx_index, end_tx_index = 0):
        if type(block_number) == int:
            block_number = hex(block_number)
        if type(start_tx_index) == int:
            start_tx_index = hex(start_tx_index)
        if type(end_tx_index) == int:
            end_tx_index = hex(end_tx_index)
        self.payload["method"] = "sbch_getTxListByHeightWithRange"
        self.payload["params"] = [block_number, start_tx_index, end_tx_index]
        self.get_response()

    def getAddressCount(self, query, address):
        # query must be "from", "to" or "both"
        address = Web3.toChecksumAddress(address)
        self.payload["method"] = "sbch_getAddressCount"
        self.payload["params"] = [query, address]
        self.get_response()

    def getSep20AddressCount(self, query, contract_address, address):
        # query must be "from", "to" or "both"
        address = Web3.toChecksumAddress(address)
        contract_address = Web3.toChecksumAddress(contract_address)
        self.payload["method"] = "sbch_getSep20AddressCount"
        self.payload["params"] = [query, contract_address, address]
        self.get_response()

    def get_response(self):
        self.response = self.session.post(RPC_SERVER, json=self.payload, headers=self.headers).json()

    def __init__(self):
        SBCH.ID += 1
        self.payload["id"] = self.ID
        self.payload["id"] = self.ID

def generate_update_initial_files():
    '''This function is ran once first to generate the files ETF_ASSETS_BALANCES and ETF_FARMS.json. It just set all balances to zero.'''
    '''If a change is made on SmartIndex portfolio assets, this need to be run again to port the changes to the ETF portfolio.'''
    ETF_farms = engine.farms
    ETF_assets_balances = engine.assets_balances

    # BlockNG-Beam farms are considered illiquid
    del ETF_farms["BlockNG-Beam"]
    for DEX in ETF_farms:
        for i in range(len(ETF_farms[DEX]["farms"])):
            ETF_farms[DEX]["farms"][i]["lp_token_amount"] = 0
            ETF_farms[DEX]["farms"][i]["initial_token0_amount"] = 0
            ETF_farms[DEX]["farms"][i]["initial_token1_amount"] = 0

    # Just liquid assets are incorporated
    for asset in ETF_assets_balances.copy():
        if ETF_assets_balances[asset]["Liquid"]:
            if "Initial" in ETF_assets_balances[asset]:
                ETF_assets_balances[asset]["Initial"] = 0
        else:
            del ETF_assets_balances[asset]

    with open('data/ETF_FARMS.json', 'w') as file:
        json.dump(ETF_farms, file, indent=4)
    with open('data/ETF_ASSETS_BALANCES.json', 'w') as file:
        json.dump(ETF_assets_balances, file, indent=4)


def take_fee(amount):
    from engine import wrap_BCH, transfer_asset, get_SEP20_balance
    wrap_BCH(amount, *(ETF_watchdog_address, "WATCHDOG_PRIV_KEY"))
    admin_fee_amount = amount * (admin_fee / 100)
    portfolio_fee_amount = amount * (portfolio_fee / 100)
    transfer_asset(engine.WBCH_CA, admin_fee_amount, engine.admin_wallet_address, *(ETF_watchdog_address, "WATCHDOG_PRIV_KEY"))
    transfer_asset(engine.WBCH_CA, portfolio_fee_amount, engine.portfolio_address, *(ETF_watchdog_address, "WATCHDOG_PRIV_KEY"))
    amount_left = get_SEP20_balance(engine.WBCH_CA, ETF_watchdog_address)
    transfer_asset(engine.WBCH_CA, amount_left, ETF_portfolio_address,
                   *(ETF_watchdog_address, "WATCHDOG_PRIV_KEY"))
    logger.info(f"Admin fee: {admin_fee_amount / 10**18} BCH. Portfolio fee: {portfolio_fee_amount / 10**18} BCH. Amount left for investment: {amount_left / 10**18} BCH.")
    import app.email as email
    email.send_email_to_admin(f"Admin fee: {admin_fee_amount / 10**18} BCH. Portfolio fee: {portfolio_fee_amount / 10**18} BCH. Amount left for investment: {amount_left / 10**18} BCH.")
    return amount_left

def get_ETF_global_stats():
    '''Deprecated function'''
    '''This function calculates the global stats of the ETF portfolio: total value and total value locked'''
    with open('data/ETF_FARMS.json') as ETF_farms_file:
        etf_farms = json.load(ETF_farms_file)
    with open('data/ETF_SEP20_BALANCES.json') as ETF_SEP20_balances_file:
        etf_SEP20_balances = json.load(ETF_SEP20_balances_file)
    with open('data/ETF_STAKED_ASSETS.json') as ETF_staked_assets_file:
        etf_staked_assets = json.load(ETF_staked_assets_file)
    total_usd_value = 0
    rewards_value = 0
    for DEX in etf_farms:
        for i in range(len(etf_farms[DEX]["farms"])):
            rewards_value += etf_farms[DEX]["farms"][i]["reward value"]
            for coin in etf_farms[DEX]["farms"][i]["Coins"]:
                total_usd_value += etf_farms[DEX]["farms"][i]["Coins"][coin]["Current value"]

    for asset in etf_SEP20_balances:
        if asset != "Total value":
            total_usd_value += etf_SEP20_balances[asset]["Current value"]

    for asset in etf_staked_assets:
        if asset not in ("Total value", "Total yield value"):
            total_usd_value += etf_staked_assets[asset]["Current value"]
            rewards_value += etf_staked_assets[asset]["Yield value"]

    global_ETF_portfolio_stats = {"total_portfolio_balance": round(total_usd_value, 2), "total_rewards_value": round(rewards_value, 2)}

    with open('data/ETF_GLOBAL_STATS.json', 'w') as file:
        json.dump(global_ETF_portfolio_stats, file, indent=4)

def allocate_coins(amount_to_allocate):
    with open('data/ETF_portfolio.json') as etf_portfolio_file:
        ETF_portfolio = json.load(etf_portfolio_file)
    with open('data/ETF_SEP20_BALANCES.json') as etf_SEP20_balances_file:
        ETF_SEP20_balances = json.load(etf_SEP20_balances_file)
    with open('data/ETF_ASSETS_BALANCES.json') as etf_assets_balances_file:
        ETF_assets_balances = json.load(etf_assets_balances_file)
    with open('data/ETF_STAKED_ASSETS.json') as etf_staked_assets_file:
        ETF_staked_assets = json.load(etf_staked_assets_file)
    with open('data/ETF_FARMS.json') as etf_farms_file:
        ETF_farms = json.load(etf_farms_file)
    with open('data/ETF_LP_BALANCES.json') as etf_lp_balances_file:
        ETF_LP_balances = json.load(etf_lp_balances_file)

    # The first step is to calculate the BCH amount to allocate in every asset (tokens, staked tokens and farms)

    for asset in ETF_portfolio["Standalone assets"]:
        ETF_portfolio["Standalone assets"][asset] = (ETF_portfolio["Standalone assets"][asset] * amount_to_allocate) / 100
    for DEX in ETF_portfolio["Farms"]:
        for farm in ETF_portfolio["Farms"][DEX]:
            ETF_portfolio["Farms"][DEX][farm] = (ETF_portfolio["Farms"][DEX][farm] * amount_to_allocate) / 100
    for DEX in ETF_portfolio["SIDX pools"]:
        ETF_portfolio["SIDX pools"][DEX] = (ETF_portfolio["SIDX pools"][DEX] * amount_to_allocate) / 100

    import app.email as email
    email.send_email_to_admin(f'Assets list to allocate: {ETF_portfolio}')
    logger.info(f'Assets list to allocate: {ETF_portfolio}')

    ETF_portfolio_account = (ETF_portfolio_address, 'ETF_PORTFOLIO_PRIV_KEY')

    # The first thing to buy are SEP20 tokens
    for SEP20_token in ETF_SEP20_balances:
        if SEP20_token != "Total value":
            amount_to_buy = ETF_portfolio["Standalone assets"][SEP20_token]
            engine.swap_assets(engine.WBCH_CA, ETF_assets_balances[SEP20_token]["CA"], int(amount_to_buy), *ETF_portfolio_account)

    # Next, staked assets. Staking requires first approve the smart contracts to spend from the ETF_portfolio_wallet
    for staked_token in ETF_staked_assets:
        if staked_token not in ("Total value", "Total yield value"):
            amount_to_buy = ETF_portfolio["Standalone assets"][staked_token]
            engine.swap_assets(engine.WBCH_CA, ETF_assets_balances[staked_token]["CA"], int(amount_to_buy),
                               *ETF_portfolio_account)
            amount_to_stake = engine.get_SEP20_balance(ETF_assets_balances[staked_token]["CA"], ETF_portfolio_address)
            ETF_staked_assets[staked_token]["Initial"] += amount_to_stake / 10**18
            if staked_token in {"Green Ben", "DAIQUIRI"}:
                ABI = open(f"ABIs/{ETF_assets_balances[staked_token]['harvest_ABI']}", "r")
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address=ETF_assets_balances[staked_token]["harvest_CA"], abi=abi)
                engine.asset_allowance(ETF_assets_balances[staked_token]["CA"], ETF_assets_balances[staked_token]["harvest_CA"], *ETF_portfolio_account)
                stake_tx = contract.functions.deposit(ETF_assets_balances[staked_token]["harvest_pool_id"],
                                                         int(amount_to_stake)).buildTransaction(
                    {'chainId': 10000,
                     'from': ETF_portfolio_address,
                     'gasPrice': w3.toWei('1.05', 'gwei')
                     })
                engine.send_transaction(staked_token, stake_tx, *ETF_portfolio_account)
            if staked_token in {"MistToken", "LNS"}:
                ABI = open(f"ABIs/{ETF_assets_balances[staked_token]['harvest_ABI']}", "r")
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address=ETF_assets_balances[staked_token]["BAR_CA"], abi=abi)
                engine.asset_allowance(ETF_assets_balances[staked_token]["CA"],
                                       ETF_assets_balances[staked_token]["BAR_CA"], *ETF_portfolio_account)
                stake_tx = contract.functions.enter(int(amount_to_stake)).buildTransaction(
                    {'chainId': 10000,
                     'from': ETF_portfolio_address,
                     'gasPrice': w3.toWei('1.05', 'gwei')
                     })
                engine.send_transaction(staked_token, stake_tx, *ETF_portfolio_account)
            if staked_token == "GOB":
                ETF_staked_assets[staked_token]["Initial"] *= 10**9 #GOB has 9 decimals
                ABI = open(f"ABIs/{ETF_assets_balances[staked_token]['harvest_ABI']}", "r")
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address="0x9851c1175A26c8656441bc2cAE0Cd21AddB80dBa", abi=abi)
                engine.asset_allowance(ETF_assets_balances[staked_token]["CA"],
                                       "0x9851c1175A26c8656441bc2cAE0Cd21AddB80dBa", *ETF_portfolio_account)
                stake_tx = contract.functions.stake(int(amount_to_stake), ETF_portfolio_address).buildTransaction(
                    {'chainId': 10000,
                     'from': ETF_portfolio_address,
                     'gasPrice': w3.toWei('1.05', 'gwei')
                     })
                engine.send_transaction(staked_token, stake_tx, *ETF_portfolio_account)

    #Staked tokens data is saved
    with open('data/ETF_STAKED_ASSETS.json', 'w') as file:
        json.dump(ETF_staked_assets, file, indent=4)

    #Now, SIDX liquidity is allocated.
    for DEX in ETF_LP_balances:
        amount_to_buy = ETF_portfolio["SIDX pools"][DEX]
        LP_CA = SIDX_liquidity_pools[DEX]["lp_CA"]
        tokens_dictionary = engine.buy_assets_for_liquidty_addition(amount_to_buy, engine.WBCH_CA, LP_CA,
                                                                    *ETF_portfolio_account)
        try:
            engine.add_liquidity(tokens_dictionary, LP_CA, routers[DEX], *ETF_portfolio_account)
        except:
            engine.add_liquidity(tokens_dictionary, LP_CA, routers[DEX],
                                 *ETF_portfolio_account, min_amount_percentage=2)
        ABI = open("ABIs/UniswapV2Pair.json", "r")
        abi = json.loads(ABI.read())
        contract = w3.eth.contract(address=LP_CA, abi=abi)
        LP_balance = contract.functions.balanceOf(ETF_portfolio_address).call()
        if DEX in ("Mistswap", "Tangoswap"):
            # Before depositing, the master contract should be allowed to spend the LP token
            engine.asset_allowance(LP_CA, masters[DEX], *ETF_portfolio_account)
            ABI = open("ABIs/MIST-Master-ABI.json", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=masters[DEX], abi=abi)
            deposit_tx = contract.functions.deposit(SIDX_liquidity_pools[DEX]['pool_id'], LP_balance).buildTransaction(
                {'chainId': 10000,
                 'from': ETF_portfolio_address,
                 'gasPrice': w3.toWei('1.05', 'gwei')
                 })
            engine.send_transaction(
                f"Depositing {LP_balance} LP tokens to {DEX} SIDX farm", deposit_tx, *ETF_portfolio_account)
        if DEX == "Emberswap":
            # Before depositing, the master contract should be allowed to spend the LP token
            engine.asset_allowance(LP_CA, masters[DEX], *ETF_portfolio_account)
            ABI = open("ABIs/EMBER_Distributor-ABI.json", 'r')
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address="0x8ecb32C33AB3f7ee3D6Ce9D4020bC53fecB36Be9", abi=abi)
            deposit_tx = contract.functions.deposit(SIDX_liquidity_pools[DEX]['pool_id'], LP_balance).buildTransaction(
                {'chainId': 10000,
                 'from': ETF_portfolio_address,
                 'gasPrice': w3.toWei('1.05', 'gwei')
                 })
            engine.send_transaction(f"Depositing {LP_balance / 10 ** 18} SIDX/EMBER LP tokens to EmberSwap farm",
                                    deposit_tx, *ETF_portfolio_account)
        if DEX == "BlockNG":
            # Before depositing, the master contract should be allowed to spend the LP token
            engine.asset_allowance(LP_CA, "0x3384d970688f7B86a8D7aE6D8670CD5f9fd5fE1E", *ETF_portfolio_account)
            ABI = open("ABIs/BlockNG-farm.json", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address="0x3384d970688f7B86a8D7aE6D8670CD5f9fd5fE1E", abi=abi)
            tokenId = contract.functions.tokenIds(ETF_portfolio_address).call()
            deposit_tx = contract.functions.deposit(LP_balance, int(tokenId)).buildTransaction(
                {'chainId': 10000,
                 'from': ETF_portfolio_address,
                 'gasPrice': w3.toWei('1.05', 'gwei')
                 })
            engine.send_transaction(
                f"Depositing {LP_balance / 10 ** 18} LP tokens to BlockNG-Kudos SIDX/LAW farm", deposit_tx,
                *ETF_portfolio_account)

    #Finally, the farms. The last farm will just use all the funds (WBCH) left.
    last_DEX = False
    for dex_src, DEX in enumerate(ETF_farms):
        if len(ETF_farms) - 1 == dex_src:
            last_DEX = True
        if DEX in ("Mistswap", "Tangoswap"):
            for i in range(len(ETF_farms[DEX]['farms'])):
                if i == len(ETF_farms[DEX]['farms']) - 1 and last_DEX == True:
                    amount_to_buy = engine.get_SEP20_balance(engine.WBCH_CA, ETF_portfolio_address)
                else:
                    amount_to_buy = ETF_portfolio["Farms"][DEX][ETF_farms[DEX]['farms'][i]["lp_CA"]]
                LP_CA = ETF_farms[DEX]['farms'][i]['lp_CA']
                tokens_dictionary = engine.buy_assets_for_liquidty_addition(amount_to_buy, engine.WBCH_CA, LP_CA, *ETF_portfolio_account)
                try:
                    engine.add_liquidity(tokens_dictionary, LP_CA, routers[DEX], *ETF_portfolio_account)
                except:
                    engine.add_liquidity(tokens_dictionary, LP_CA, routers[DEX],
                                         *ETF_portfolio_account, min_amount_percentage=2)
                ABI = open("ABIs/UniswapV2Pair.json", "r")
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address=LP_CA, abi=abi)
                LP_balance = contract.functions.balanceOf(ETF_portfolio_address).call()
                ETF_farms[DEX]["farms"][i]["lp_token_amount"] += LP_balance
                # Before depositing, the master contract should be allowed to spend the LP token
                engine.asset_allowance(LP_CA, masters[DEX], *ETF_portfolio_account)
                # Now, the LP token can be deposited
                ABI = open("ABIs/MIST-Master-ABI.json", "r")
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address=masters[DEX], abi=abi)
                deposit_tx = contract.functions.deposit(ETF_farms[DEX]['farms'][i]['pool_id'], LP_balance).buildTransaction(
                    {'chainId': 10000,
                     'from': ETF_portfolio_address,
                     'gasPrice': w3.toWei('1.05', 'gwei')
                     })
                engine.send_transaction(f"Depositing {LP_balance} LP tokens to {DEX} farm {ETF_farms[DEX]['farms'][i]['lp_CA']}", deposit_tx, *ETF_portfolio_account)

        if DEX == "BlockNG-Kudos":
            for i in range(len(ETF_farms[DEX]['farms'])):
                if i == len(ETF_farms[DEX]['farms']) - 1 and last_DEX == True:
                    amount_to_buy = engine.get_SEP20_balance(engine.WBCH_CA, ETF_portfolio_address)
                else:
                    amount_to_buy = ETF_portfolio["Farms"][DEX][ETF_farms[DEX]['farms'][i]["lp_CA"]]
                LP_CA = ETF_farms[DEX]['farms'][i]['lp_CA']
                tokens_dictionary = engine.buy_assets_for_liquidty_addition(amount_to_buy, engine.WBCH_CA, LP_CA, *ETF_portfolio_account)
                try:
                    engine.add_liquidity(tokens_dictionary, LP_CA, routers[DEX], *ETF_portfolio_account)
                except:
                    engine.add_liquidity(tokens_dictionary, ETF_farms[DEX]['farms'][i]['lp_CA'], routers[DEX],
                                             *ETF_portfolio_account, min_amount_percentage=3)
                ABI = open("ABIs/UniswapV2Pair.json", "r")
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address=LP_CA, abi=abi)
                LP_balance = contract.functions.balanceOf(ETF_portfolio_address).call()
                ETF_farms[DEX]["farms"][i]["lp_token_amount"] += LP_balance
                # Before depositing, the master contract should be allowed to spend the LP token
                engine.asset_allowance(LP_CA, ETF_farms[DEX]["farms"][i]["CA"], *ETF_portfolio_account)
                ABI = open("ABIs/BlockNG-farm.json", "r")
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address=ETF_farms[DEX]["farms"][i]["CA"], abi=abi)
                tokenId = contract.functions.tokenIds(ETF_portfolio_address).call()
                deposit_tx = contract.functions.deposit(LP_balance, int(tokenId)).buildTransaction(
                    {'chainId': 10000,
                     'from': ETF_portfolio_address,
                     'gasPrice': w3.toWei('1.05', 'gwei')
                     })
                engine.send_transaction(
                    f"Depositing {LP_balance} LP tokens LP to {DEX} farm {ETF_farms[DEX]['farms'][i]['lp_CA']}",
                    deposit_tx, *ETF_portfolio_account)
    #Data from farms is saved
    with open('data/ETF_FARMS.json', 'w') as file:
        json.dump(ETF_farms, file, indent=4)

    return True

def assets_withdrawal(share_to_withdraw, recipient_address):
    # Share to withdraw is a float passed from the main function, with values from 0 to 1.
    with open('data/ETF_SEP20_BALANCES.json') as etf_SEP20_balances_file:
        ETF_SEP20_balances = json.load(etf_SEP20_balances_file)
    with open('data/ETF_ASSETS_BALANCES.json') as etf_assets_balances_file:
        ETF_assets_balances = json.load(etf_assets_balances_file)
    with open('data/ETF_STAKED_ASSETS.json') as etf_staked_assets_file:
        ETF_staked_assets = json.load(etf_staked_assets_file)
    with open('data/ETF_FARMS.json') as etf_farms_file:
        ETF_farms = json.load(etf_farms_file)
    with open('data/ETF_LP_BALANCES.json') as etf_lp_balances_file:
        ETF_LP_balances = json.load(etf_lp_balances_file)

    ETF_portfolio_account = (ETF_portfolio_address, 'ETF_PORTFOLIO_PRIV_KEY')

    # This hack is for avoiding rounding problems in case the ETF has just one investor and wants to withdraw all

    if share_to_withdraw == 1:
        share_to_withdraw = int(share_to_withdraw)

    # We start selling every SEP20 token share to WBCH
    for SEP20_token in ETF_SEP20_balances:
        if SEP20_token != "Total value":
            ETF_portfolio_balance = engine.get_SEP20_balance(ETF_assets_balances[SEP20_token]["CA"], ETF_portfolio_address)
            amount_to_sell = int(ETF_portfolio_balance * share_to_withdraw)
            engine.swap_assets(ETF_assets_balances[SEP20_token]["CA"], engine.WBCH_CA, int(amount_to_sell), *ETF_portfolio_account)

    # Now staked assets
    for staked_token in ETF_staked_assets:
        if staked_token in {"Green Ben", "DAIQUIRI"}:
            ABI = open(f"ABIs/{ETF_assets_balances[staked_token]['harvest_ABI']}", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=ETF_assets_balances[staked_token]["harvest_CA"], abi=abi)
            staked_balance = contract.functions.userInfo(ETF_assets_balances[staked_token]["harvest_pool_id"], ETF_portfolio_address).call()[0]
            amount_to_sell = int(staked_balance * share_to_withdraw)
            withdrawal_tx = contract.functions.withdraw(ETF_assets_balances[staked_token]["harvest_pool_id"], amount_to_sell).buildTransaction(
                {'chainId': 10000,
                 'from': ETF_portfolio_address,
                 'gasPrice': w3.toWei('1.05', 'gwei')
                 })
            engine.send_transaction(f"Withdrawing {amount_to_sell} from {staked_token}", withdrawal_tx, *ETF_portfolio_account)
            ETF_staked_assets[staked_token]["Initial"] -= (amount_to_sell / 10 ** 18)
            engine.swap_assets(ETF_assets_balances[staked_token]["CA"], engine.WBCH_CA, amount_to_sell, *ETF_portfolio_account)

        if staked_token in {"MistToken", "LNS"}:
            ABI = open(f"ABIs/{ETF_assets_balances[staked_token]['harvest_ABI']}", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=ETF_assets_balances[staked_token]["BAR_CA"], abi=abi)
            staked_balance = contract.functions.balanceOf(ETF_portfolio_address).call()
            amount_to_sell = int(staked_balance * share_to_withdraw) # This amount is xMIST or xLNS
            withdrawal_tx = contract.functions.leave(int(amount_to_sell)).buildTransaction(
                {'chainId': 10000,
                 'from': ETF_portfolio_address,
                 'gasPrice': w3.toWei('1.05', 'gwei')
                 })
            engine.send_transaction(f"Withdrawing {amount_to_sell} from {staked_token}", withdrawal_tx, *ETF_portfolio_account)
            ratio = engine.xsushi_ratio(ETF_assets_balances[staked_token]["CA"], ETF_assets_balances[staked_token]["BAR_CA"])
            amount_to_swap = int(amount_to_sell * ratio) # This amount is Mist or LNS
            ETF_staked_assets[staked_token]["Initial"] -= (amount_to_swap / 10 ** 18)
            unstaked_token_balance = int(engine.get_SEP20_balance(ETF_assets_balances[staked_token]["CA"], ETF_portfolio_address))
            # Just if there's some rounding error
            if amount_to_swap > unstaked_token_balance:
                amount_to_swap = unstaked_token_balance
            engine.swap_assets(ETF_assets_balances[staked_token]["CA"], engine.WBCH_CA, amount_to_swap,
                               *ETF_portfolio_account)

        if staked_token == "GOB":
            ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address="0x47c61F29B1458d234409Ebbe4B6a70F3b16528EF", abi=abi)
            staked_balance = contract.functions.balanceOf(ETF_portfolio_address).call()
            amount_to_sell = int(staked_balance * share_to_withdraw)
            ABI = open(f"ABIs/{ETF_assets_balances[staked_token]['harvest_ABI']}", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address="0x48B8aCe692ad8BD2E3139C65bFf7d28c048F8f00", abi=abi)
            withdrawal_tx = contract.functions.unstake(amount_to_sell, True).buildTransaction(
                {'chainId': 10000,
                 'from': ETF_portfolio_address,
                 'gasPrice': w3.toWei('1.05', 'gwei')
                 })
            engine.send_transaction(f"Withdrawing {amount_to_sell / 10**9} from {staked_token}", withdrawal_tx, *ETF_portfolio_account)
            ETF_staked_assets[staked_token]["Initial"] -= (amount_to_sell / 10 ** 9)
            engine.swap_assets(ETF_assets_balances[staked_token]["CA"], engine.WBCH_CA, amount_to_sell,
                               *ETF_portfolio_account)
    # Staked tokens data is saved
    with open('data/ETF_STAKED_ASSETS.json', 'w') as file:
        json.dump(ETF_staked_assets, file, indent=4)
    #Next, SIDX liquidity pools
    for DEX in ETF_LP_balances:
        if DEX in ("Mistswap", "Tangoswap"):
            ABI = open("ABIs/MIST-Master-ABI.json", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=masters[DEX], abi=abi)
            pool_balance = contract.functions.userInfo(SIDX_liquidity_pools[DEX]["pool_id"], ETF_portfolio_address).call()[0]
            amount_to_sell = int(pool_balance * share_to_withdraw)
            withdrawal_tx = contract.functions.withdraw(SIDX_liquidity_pools[DEX]["pool_id"], amount_to_sell).buildTransaction(
                {'chainId': 10000,
                 'from': ETF_portfolio_address,
                 'gasPrice': w3.toWei('1.05', 'gwei')
                 })
            engine.send_transaction(
                f"Withdrawing {amount_to_sell} SIDX LP from DEX {DEX}", withdrawal_tx, *ETF_portfolio_account)
            # Now it's time to remove the liquidity
            token0_address, token0_amount, token1_address, token1_amount = engine.remove_liquidity(100, SIDX_liquidity_pools[DEX]['lp_CA'], routers[DEX], *ETF_portfolio_account)
            # And sell the tokens for WBCH
            engine.swap_assets(token0_address, engine.WBCH_CA, token0_amount, *ETF_portfolio_account)
            engine.swap_assets(token1_address, engine.WBCH_CA, token1_amount, *ETF_portfolio_account)
        if DEX == "BlockNG":
            ABI = open("ABIs/BlockNG-farm.json", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address="0x3384d970688f7B86a8D7aE6D8670CD5f9fd5fE1E", abi=abi)
            pool_balance = contract.functions.balanceOf(ETF_portfolio_address).call()
            amount_to_sell = int(pool_balance * share_to_withdraw)
            #As this is a Kudos farms, the reward must be farmed before withdrawal or it will be lost
            harvest_tx = contract.functions.getReward(ETF_portfolio_address,
                                                      [ETF_assets_balances["LAW"]["CA"]]).buildTransaction(
                {'chainId': 10000,
                 'from': ETF_portfolio_address,
                 'gasPrice': w3.toWei('1.05', 'gwei')
                 })
            engine.send_transaction("Harvesting BlockNG Kudos farm before withdrawal", harvest_tx, *ETF_portfolio_account)
            withdrawal_tx = contract.functions.withdraw(amount_to_sell).buildTransaction(
                {'chainId': 10000,
                 'from': ETF_portfolio_address,
                 'gasPrice': w3.toWei('1.05', 'gwei')
                 })
            engine.send_transaction(
                f"Withdrawing {amount_to_sell} SIDX LP from DEX {DEX}", withdrawal_tx, *ETF_portfolio_account)
            # Now it's time to remove the liquidity
            token0_address, token0_amount, token1_address, token1_amount = engine.remove_liquidity(99.99, SIDX_liquidity_pools[DEX]['lp_CA'], routers[DEX], *ETF_portfolio_account)
            # And sell the tokens for WBCH
            engine.swap_assets(token0_address, engine.WBCH_CA, token0_amount, *ETF_portfolio_account)
            engine.swap_assets(token1_address, engine.WBCH_CA, token1_amount, *ETF_portfolio_account)
        if DEX == "Emberswap":
            ABI = open("ABIs/EMBER_Distributor-ABI.json", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address="0x8ecb32C33AB3f7ee3D6Ce9D4020bC53fecB36Be9", abi=abi)
            pool_balance = \
            contract.functions.userInfo(SIDX_liquidity_pools[DEX]['pool_id'], ETF_portfolio_address).call()[0]
            amount_to_sell = int(pool_balance * share_to_withdraw)
            withdrawal_tx = contract.functions.withdraw(SIDX_liquidity_pools[DEX]['pool_id'],
                                                        amount_to_sell).buildTransaction(
                {'chainId': 10000,
                 'from': ETF_portfolio_address,
                 'gasPrice': w3.toWei('1.05', 'gwei')
                 })
            engine.send_transaction(f"Withdrawing {amount_to_sell} SIDX LP from DEX {DEX}", withdrawal_tx, *ETF_portfolio_account)
            token0_address, token0_amount, token1_address, token1_amount = engine.remove_liquidity(100, SIDX_liquidity_pools[DEX]['lp_CA'], routers[DEX], *ETF_portfolio_account)
            # And sell the tokens for WBCH
            engine.swap_assets(token0_address, engine.WBCH_CA, token0_amount, *ETF_portfolio_account)
            engine.swap_assets(token1_address, engine.WBCH_CA, token1_amount, *ETF_portfolio_account)
            
    #Finally, the farms
    for DEX in ETF_farms:
        if DEX in ("Mistswap", "Tangoswap"):
            for i in range(len(ETF_farms[DEX]['farms'])):
                ABI = open("ABIs/MIST-Master-ABI.json", "r")
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address=masters[DEX], abi=abi)
                pool_balance = contract.functions.userInfo(ETF_farms[DEX]['farms'][i]['pool_id'], ETF_portfolio_address).call()[0]
                amount_to_sell = int(pool_balance * share_to_withdraw)
                withdrawal_tx = contract.functions.withdraw(ETF_farms[DEX]['farms'][i]['pool_id'], amount_to_sell).buildTransaction(
                    {'chainId': 10000,
                     'from': ETF_portfolio_address,
                     'gasPrice': w3.toWei('1.05', 'gwei')
                     })
                engine.send_transaction(f"Withdrawing {amount_to_sell} from DEX {DEX} and farm {ETF_farms[DEX]['farms'][i]['pool_id']}", withdrawal_tx,
                                        *ETF_portfolio_account)
                ETF_farms[DEX]['farms'][i]["lp_token_amount"] -= amount_to_sell
                # Now it's time to remove the liquidity
                token0_address, token0_amount, token1_address, token1_amount = engine.remove_liquidity(100, ETF_farms[DEX]['farms'][i]['lp_CA'], routers[DEX], *ETF_portfolio_account)
                # And sell the tokens for WBCH
                engine.swap_assets(token0_address, engine.WBCH_CA, token0_amount, *ETF_portfolio_account)
                engine.swap_assets(token1_address, engine.WBCH_CA, token1_amount, *ETF_portfolio_account)

        if DEX == "BlockNG-Kudos":
            for i in range(len(ETF_farms[DEX]['farms'])):
                ABI = open("ABIs/BlockNG-farm.json", "r")
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address=ETF_farms[DEX]["farms"][i]["CA"], abi=abi)
                pool_balance = contract.functions.balanceOf(ETF_portfolio_address).call()
                amount_to_sell = int(pool_balance * share_to_withdraw)
                # In the case of Kudos farms, the reward must be farmed before withdrawal or it will be lost
                harvest_tx = contract.functions.getReward(ETF_portfolio_address,
                                                          [ETF_assets_balances["LAW"]["CA"]]).buildTransaction(
                    {'chainId': 10000,
                     'from': ETF_portfolio_address,
                     'gasPrice': w3.toWei('1.05', 'gwei')
                     })
                engine.send_transaction("Harvesting BlockNG Kudos farm before withdrawal", harvest_tx, *ETF_portfolio_account)
                withdrawal_tx = contract.functions.withdraw(amount_to_sell).buildTransaction(
                    {'chainId': 10000,
                     'from': ETF_portfolio_address,
                     'gasPrice': w3.toWei('1.05', 'gwei')
                     })
                engine.send_transaction(
                    f"Withdrawing {amount_to_sell} from DEX {DEX} and farm {ETF_farms[DEX]['farms'][i]['lp_CA']}",
                    withdrawal_tx,
                    *ETF_portfolio_account)
                # Now it's time to remove the liquidity
                token0_address, token0_amount, token1_address, token1_amount = engine.remove_liquidity(99.99, ETF_farms[DEX]['farms'][i]['lp_CA'], routers[DEX], *ETF_portfolio_account)
                # And sell the tokens for WBCH
                engine.swap_assets(token0_address, engine.WBCH_CA, token0_amount, *ETF_portfolio_account)
                engine.swap_assets(token1_address, engine.WBCH_CA, token1_amount, *ETF_portfolio_account)

    #Data from farms is saved
    with open('data/ETF_FARMS.json', 'w') as file:
        json.dump(ETF_farms, file, indent=4)

    WBCH_balance = engine.get_SEP20_balance(engine.WBCH_CA, ETF_portfolio_address)
    engine.transfer_asset(engine.WBCH_CA, WBCH_balance, recipient_address, *ETF_portfolio_account)
    logger.info(f'Withdrawal: {WBCH_balance / 10**18} WBCH withdraw, sent to {recipient_address}')
    return True

def rescan_farms():
    '''This function is used to re-scan farms and update the LP balance. It will be called every time a new farm is added.'''
    with open('data/ETF_FARMS.json') as etf_farms_file:
        ETF_farms = json.load(etf_farms_file)

    for DEX in ETF_farms:
        if DEX in ("Mistswap", "Tangoswap"):
            for i in range(len(ETF_farms[DEX]['farms'])):
                ABI = open("ABIs/MIST-Master-ABI.json", "r")
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address=masters[DEX], abi=abi)
                pool_balance = contract.functions.userInfo(ETF_farms[DEX]['farms'][i]['pool_id'], ETF_portfolio_address).call()[0]
                ETF_farms[DEX]['farms'][i]["lp_token_amount"] = pool_balance
        if DEX == "BlockNG-Kudos":
            for i in range(len(ETF_farms[DEX]['farms'])):
                ABI = open("ABIs/BlockNG-farm.json", "r")
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address=ETF_farms[DEX]["farms"][i]["CA"], abi=abi)
                pool_balance = contract.functions.balanceOf(ETF_portfolio_address).call()
                ETF_farms[DEX]['farms'][i]["lp_token_amount"] = pool_balance

    #Data from farms is saved
    with open('data/ETF_FARMS.json', 'w') as file:
        json.dump(ETF_farms, file, indent=4)

def start_watchdog(start_block):
    if os.path.exists('data/ETF_investors_transfers.json'):
        with open('data/ETF_investors_transfers.json') as etf_investors_transfers_file:
            ETF_investors_transfers = json.load(etf_investors_transfers_file)
    else:
        ETF_investors_transfers = {"latest_scanned_block": start_block, "investors": [], "running": False,
                                   "withdrawals": []}
    if ETF_investors_transfers["running"] == True:
        print("Watchdog already running")
        return
    else:
        ETF_investors_transfers["running"] = True
        ETF_investors_transfers["latest_scanned_block"] = start_block
    with open('data/ETF_investors_transfers.json', 'w') as file:
        json.dump(ETF_investors_transfers, file, indent=4)

def stop_watchdog():
    with open('data/ETF_investors_transfers.json') as etf_investors_transfers_file:
        ETF_investors_transfers = json.load(etf_investors_transfers_file)
    if ETF_investors_transfers["running"] == False:
        print("Watchdog already stopped")
        return
    else:
        ETF_investors_transfers["running"] = False
    with open('data/ETF_investors_transfers.json', 'w') as file:
        json.dump(ETF_investors_transfers, file, indent=4)

def main():
    # ETF_investors_transfers is a file created by start_watchdog() given a start block, which structure is:
    # ETF_investors_transfers = {"latest_scanned_block": start_block, "investors": [], "running": True, "withdrawals": []}
    # Started live on block 7052831
    # Investors/withdrawals list contains the TXID of every investment.
    if os.path.exists('data/ETF_investors_transfers.json'):
        with open('data/ETF_investors_transfers.json') as etf_investors_transfers_file:
            ETF_investors_transfers = json.load(etf_investors_transfers_file)

    else:
        return

    # Private keys must be loaded on the environment for the watchdog to work.
    ETF_portfolio_priv_key = os.environ.get("ETF_PORTFOLIO_PRIV_KEY")
    watchdog_priv_key = os.environ.get("WATCHDOG_PRIV_KEY")
    if watchdog_priv_key == None or ETF_portfolio_priv_key == None:
        logger.error("Required private keys not loaded in the environment. Stopping the watchdog.")
        import app.email as email
        email.send_email_to_admin("Required private keys not loaded in the environment. Stopping the watchdog.")
        stop_watchdog()
        return

    latest_block_number = w3.eth.blockNumber
    new_incoming_txs = SBCH()
    new_incoming_txs.queryTxByDst(ETF_watchdog_address, ETF_investors_transfers["latest_scanned_block"], end=latest_block_number)
    if len(new_incoming_txs.response['result']) != 0:
        try:
            for i in range(len(new_incoming_txs.response["result"])):
                investor_address = new_incoming_txs.response["result"][i]["from"]
                investment_amount = int(new_incoming_txs.response["result"][i]["value"], 16)
                TXID = new_incoming_txs.response["result"][i]["hash"]
                with open('data/ETF_GLOBAL_STATS.json') as etf_global_stats_file:
                    ETF_global_stats = json.load(etf_global_stats_file)
                ETF_portfolio_USD_value = float(ETF_global_stats["total_portfolio_balance"])
                if (investment_amount / 10**18) < min_investment_amount:
                    logger.info(
                        f'Insufficient investment from address {investor_address}: amount sent is {(int(new_incoming_txs.response["result"][i]["value"], 16) / 10**18)} and TXID is {new_incoming_txs.response["result"][i]["hash"]}')
                    import app.email as email
                    email.send_email_to_admin(
                        f'Insufficient investment from address {investor_address}: amount sent is {(int(new_incoming_txs.response["result"][i]["value"], 16) / 10**18)} and TXID is {new_incoming_txs.response["result"][i]["hash"]}')
                else:
                    if TXID not in ETF_investors_transfers["investors"]:
                        ETF_investors_transfers["investors"].append(TXID)
                        logger.info(f'New investment from address {investor_address}: amount sent is {int(new_incoming_txs.response["result"][i]["value"], 16) / 10**18} and TXID is {TXID}. Portfolio value is {ETF_portfolio_USD_value}.')
                        import app.email as email
                        email.send_email_to_admin(f'New investment from address {investor_address}: amount sent is {int(new_incoming_txs.response["result"][i]["value"], 16) / 10**18} and TXID is {TXID}. Portfolio value is {ETF_portfolio_USD_value}.')
                    else:
                        logger.error(f'Double deposit detected with hash {TXID}, please check.')
                        import app.email as email
                        email.send_email_to_admin(f'Double deposit detected with hash {TXID}, please check')
                        stop_watchdog()
                        return
                    try:
                        amount_left = take_fee(investment_amount)
                    except Exception as e:
                        logger.error(f'Failed to take fees, error is {e}')
                    try:
                        # Send the amount left from the watchdog address to the ETF portfolio address
                        engine.transfer_asset(engine.WBCH_CA, amount_left, ETF_portfolio_address, (ETF_watchdog_address, 'WATCHDOG_PRIV_KEY'))
                    except Exception as e:
                        logger.error(f'Failed to transfer {amount_left / 10**18} WBCH left to ETF portfolio address, error is {e}')
                    try:
                        successful_allocation = allocate_coins(amount_left)
                    except Exception as e:
                        logger.error(f'Failed to allocate coins, error is {e}')
                    if successful_allocation == True:
                        try:
                            rescan_farms()
                            engine.main(complete_scan=False)
                        except Exception as e:
                            logger.error(f'Exception found while the watchdog ran the engine, trying after 120 seconds. Exception is {e}.')
                            from time import sleep
                            sleep(120)
                            engine.main(complete_scan=False)
                        finally:
                            bch_price = engine.get_BCH_price()
                            investment_usd_amount = (amount_left / 10**18) * bch_price
                            # SIDX_ETF coins are minted
                            # ETF_SIDX_minted = investment_usd_amount * ETF_SIDX_supply / ETF_portfolio_USD_value
                            ABI = open("ABIs/ERC20-ABI.json", "r")
                            abi = json.loads(ABI.read())
                            contract = w3.eth.contract(address=ETF_SIDX_CA, abi=abi)
                            ETF_SIDX_supply = int(contract.functions.totalSupply().call())
                            if ETF_SIDX_supply == 0 or ETF_portfolio_USD_value == 0:
                                ETF_SIDX_minted = 1 * 10**18
                            else:
                                ETF_SIDX_minted = investment_usd_amount * ETF_SIDX_supply / ETF_portfolio_USD_value
                            minting_tx = contract.functions.mint(w3.toChecksumAddress(investor_address), int(ETF_SIDX_minted)).buildTransaction(
                            {'chainId': 10000,
                             'from': ETF_watchdog_address,
                             'gasPrice': w3.toWei('1.05', 'gwei')
                             })
                            engine.send_transaction(
                                f"Minting {ETF_SIDX_minted} SIDX_ETF tokens for {investor_address}",
                                minting_tx, *(ETF_watchdog_address, "WATCHDOG_PRIV_KEY"))
                    else:
                        logger.error("Allocate_coins() didn't return True")
                        import app.email as email
                        email.send_email_to_admin("Allocate_coins() didn't return True")
                        stop_watchdog()
                        return

        except Exception as e:
            logger.error(f'Watchdog failed with exception {e}')
            import app.email as email
            email.send_email_to_admin(f'Watchdog failed with exception {e}')
            stop_watchdog()
            return

    # Time to scan for SIDX-ETF tokens incoming txs, which means an ETF portfolio withdrawal
    logs = w3.eth.get_logs({'topic': SBCH.topics["Transfer"], 'address': ETF_SIDX_CA,
                            'fromBlock': ETF_investors_transfers["latest_scanned_block"]})
    ABI = open("ABIs/ERC20-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=ETF_SIDX_CA, abi=abi)
    for i in range(len(logs)):
        tx_hash = logs[i].transactionHash
        receipt = w3.eth.getTransactionReceipt(tx_hash)
        transfer = contract.events.Transfer().processReceipt(receipt)
        if transfer[0].args.to == ETF_watchdog_address:
            if tx_hash not in ETF_investors_transfers["withdrawals"]:
                ETF_investors_transfers["withdrawals"].append(tx_hash)
                investor_address = transfer[0].args["from"]
                token_amount = transfer[0].args.value
            else:
                logger.error(f'Double withdrawal request with TXID {tx_hash} detected, please check.')
                import app.email as email
                email.send_email_to_admin(f'Double withdrawal request with TXID {tx_hash} detected, please check.')
                stop_watchdog()
                return
            # Now we need to calculate the share of the portfolio to withdrawal, from 0 to 1, being 1 all
            ABI = open("ABIs/ERC20-ABI.json", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=ETF_SIDX_CA, abi=abi)
            ETF_SIDX_supply = int(contract.functions.totalSupply().call())
            share_to_withdraw = token_amount/ETF_SIDX_supply
            if share_to_withdraw < min_withdrawal_share:
                logger.error(f'Withdrawal threshold not reached. Investor address  is {investor_address}, amount sent is {token_amount / 10**18} and TXID is {w3.toHex(tx_hash)}. Share to wtidrawal is {share_to_withdraw}.')
                import app.email as email
                email.send_email_to_admin(f'Withdrawal threshold not reached. Investor address  is {investor_address}, amount sent is {token_amount / 10**18} and TXID is {w3.toHex(tx_hash)}. Share to wtidrawal is {share_to_withdraw}.')
                return
            else:
                logger.info(
                    f'New withdrawal from address {investor_address}: amount sent is {token_amount} and TXID is {w3.toHex(tx_hash)}. Share to wtidrawal is {share_to_withdraw}.')
                import app.email as email
                email.send_email_to_admin(
                    f'New withdrawal from address {investor_address}: amount sent is {token_amount} and TXID is {w3.toHex(tx_hash)}. Share to wtidrawal is {share_to_withdraw}.')
                try:
                    withdrawal_successful = assets_withdrawal(share_to_withdraw, investor_address)
                except Exception as e:
                    logger.error(
                        f'Problem when withdrawing assets. Investor address  is {investor_address}, amount sent is {token_amount / 10 ** 18} and TXID is {w3.toHex(tx_hash)}. Share to wtidrawal is {share_to_withdraw}. Exception is {e}.')
                    import app.email as email
                    email.send_email_to_admin(
                        f'Problem when withdrawing assets. Investor address  is {investor_address}, amount sent is {token_amount / 10 ** 18} and TXID is {w3.toHex(tx_hash)}. Share to wtidrawal is {share_to_withdraw}. Exception is {e}.')
                    stop_watchdog()
                    return

                if withdrawal_successful == True:
                    ABI = open("ABIs/ERC20-ABI.json", "r")
                    abi = json.loads(ABI.read())
                    contract = w3.eth.contract(address=ETF_SIDX_CA, abi=abi)
                    burning_tx = contract.functions.burn(int(token_amount)).buildTransaction(
                        {'chainId': 10000,
                         'from': ETF_watchdog_address,
                         'gasPrice': w3.toWei('1.05', 'gwei')
                         })
                    engine.send_transaction(
                        f"{token_amount / 10**18} SIDX_ETF tokens burned, investor address is {investor_address}",
                        burning_tx, *(ETF_watchdog_address, "WATCHDOG_PRIV_KEY"))
                try:
                    rescan_farms()
                    engine.main()
                except SingleInstanceException:
                    # This happens if the cron task is running engine.main()
                    logger.error('Single class exception found while running the engine, trying after 90 seconds.')
                    from time import sleep
                    sleep(90)
                    engine.main()
                except Exception as e:
                    logger.error('Exception found while the watchdog ran the engine, trying after 90 seconds.')
                    from time import sleep
                    sleep(90)
                    engine.main()

    ETF_investors_transfers["latest_scanned_block"] = latest_block_number
    with open('data/ETF_investors_transfers.json', 'w') as file:
        json.dump(ETF_investors_transfers, file, indent=4)

if __name__ == "__main__":
    main()