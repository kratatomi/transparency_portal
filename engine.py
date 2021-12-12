import json
from web3 import Web3
import requests

w3 = Web3(Web3.HTTPProvider('https://smartbch.squidswap.cash/'))
if not w3.isConnected():
    w3 = Web3(Web3.HTTPProvider('https://smartbch.fountainhead.cash/mainnet'))

portfolio_address = w3.toChecksumAddress("0xE1ae30Fbb31bE2FB59D1c44dBEf8649C386E26B3")
admin_wallet_address = w3.toChecksumAddress("0xd11bb6a7981780aADc722146a306f7104fD93E9c")
SIDX_CA = w3.toChecksumAddress("0xF05bD3d7709980f60CD5206BddFFA8553176dd29")
law_punks_CA = w3.toChecksumAddress("0xff48aAbDDACdc8A6263A2eBC6C1A68d8c46b1bf7")
law_punks_market = w3.toChecksumAddress("0xc062bf9FaBE930FF8061f72b908AB1b702b3FdD6")
law_level_address = w3.toChecksumAddress("0x9E9eACB7E5dCc374d3108598054787ccae967544")
law_rewards = w3.toChecksumAddress("0xbeAAe3E87Bf71C97e458e2b9C84467bdc3b871c6")
punk_wallets= [portfolio_address, #Punks wallet 1
               "0x3484f575A3d3b4026B4708997317797925A236ae", #Punks wallet 2
               "0x57BB80fdab3ca9FDBC690F4b133010d8615e77b3"] #Punks wallet 3

voting_wallets = ["0xa3533751171786035fC440bFeF3F535093EAd686",
                  "0xe26B069480c24b195Cd48c8d61857B5Aaf610569",
                  "0x711CA8Da9bE7a3Ee698dD76C632A19cFB6F768Cb"]

with open("data/PUNKS_BALANCES.json", "r") as file:
    punks_owned = json.load(file)

cheque_CA = w3.toChecksumAddress("0xa36C479eEAa25C0CFC7e099D3bEbF7A7F1303F40")

assets_balances = {
    "MistToken": {"Initial": 282334.493, "Stacked": True, "CA": "0x5fA664f69c2A4A3ec94FaC3cBf7049BD9CA73129",
                  "BAR_CA": "0xC41C680c60309d4646379eD62020c534eB67b6f4", "BCH pair": "0x674A71E69fe8D5cCff6fdcF9F1Fa4262Aa14b154"},
    "FlexUSD": {"Initial": 3968.683, "Stacked": True, "CA": "0x7b2B3C5308ab5b2a1d9a94d20D35CCDf61e05b72", "BCH pair": "0x24f011f12Ea45AfaDb1D4245bA15dCAB38B43D13"},
    "Green Ben": {"Initial": 2122.74, "Stacked": True, "CA": "0xDEa721EFe7cBC0fCAb7C8d65c598b21B6373A2b6"},
    "AxieBCH": {"Initial": 167752.146, "Stacked": False, "CA": "0x3d13DaFcCA3a188DB340c81414239Bc2be312Ec9", "BCH pair": "0xD6EcaDB40b35D17f739Ec27285759d0ca119e3A1"},
    "Celery": {"Initial": 1459636.533, "Stacked": True, "CA": "0x7642Df81b5BEAeEb331cc5A104bd13Ba68c34B91"},
    "BCHPAD": {"Initial": 48649.48, "Stacked": False, "CA": "0x9192940099fDB2338B928DE2cad9Cd1525fEa881", "BCH pair": "0x8221D04A71FcD0Dd3d096cB3B49E22918095933F"},
    "FLEX Coin": {"Initial": 142.804, "Stacked": False, "CA": "0x98Dd7eC28FB43b3C4c770AE532417015fa939Dd3"},
    "LAW": {"Stacked": True, "CA": "0x0b00366fBF7037E9d75E4A569ab27dAB84759302", "BCH pair": "0xd55a9A41666108d10d31BAeEea5D6CdF3be6C5DD"},
    "FIRE": {"Stacked": False, "CA": "0x225FCa2A940cd5B18DFb168cD9B7f921C63d7B6E", "BCH pair": "0x1F354956DE4A7Ed71308225De94a27b35A84EA57"}}

initial_pool_balances = {
    "Mistswap": {"CA": "0x7E1B9F1e286160A80ab9B04D228C02583AeF90B5", "token0": 4, "token1": 18711.1},
    # Token0 is WBCH, Token1 is SIDX
    "Tangoswap": {"CA": "0x4509Ff66a56cB1b80a6184DB268AD9dFBB79DD53", "token0": 1,
                  "token1": 5000}}  # Token0 is WBCH, Token1 is SIDX


def get_balances(ben_tokens, bch_price):
    stacked_assets = {}
    SEP20_tokens = {}
    total_value_SEP20_tokens = 0
    total_value_stacked_assets = 0
    total_value_yield = 0
    for asset in assets_balances:
        if not assets_balances[asset]["Stacked"]:
            ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=assets_balances[asset]["CA"], abi=abi)
            SEP20_tokens[asset] = {}
            SEP20_tokens[asset]["Current"] = round(
                contract.functions.balanceOf(portfolio_address).call() / 10 ** contract.functions.decimals().call(), 2)
            if asset in ben_tokens:
                asset_price = get_price(assets_balances[asset]["CA"])
                SEP20_tokens[asset]["Current value"] = round(SEP20_tokens[asset]["Current"] * asset_price, 2)
                total_value_SEP20_tokens += SEP20_tokens[asset]["Current value"]
            elif "BCH pair" in assets_balances[asset]:
                asset_price = get_price_from_pool(asset, bch_price)
                SEP20_tokens[asset]["Current value"] = round(SEP20_tokens[asset]["Current"] * asset_price, 2)
                total_value_SEP20_tokens += SEP20_tokens[asset]["Current value"]
        if asset == "Celery":
            ABI = open("ABIs/CLY-ABI.json", "r")  # ABI for CLY token
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=assets_balances[asset]["CA"], abi=abi)
            wallet_balance = contract.functions.balanceOf(
                portfolio_address).call()  # CLY Neither in stacking or payout mode
            account_balance = contract.functions.getAccountBalance(
                portfolio_address).call()  # CLY Either in staking or payout mode
            stacked_assets[asset] = {}
            stacked_assets[asset]["Initial"] = round(assets_balances[asset]["Initial"], 2)
            stacked_assets[asset]["Current"] = round(
                (wallet_balance + account_balance) / 10 ** contract.functions.decimals().call(), 2)
            stacked_assets[asset]["Yield"] = round(stacked_assets[asset]["Current"] - stacked_assets[asset]["Initial"],
                                                   2)
            if asset in ben_tokens:
                asset_price = get_price(assets_balances[asset]["CA"])
                stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
                total_value_stacked_assets += stacked_assets[asset]["Current value"]
                stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
                total_value_yield += stacked_assets[asset]["Yield value"]
        if asset == "Green Ben":
            ABI = open("ABIs/EBEN_Masterbreeder.json", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=assets_balances[asset]["CA"], abi=abi)
            stacked_assets[asset] = {}
            stacked_assets[asset]["Initial"] = round(assets_balances[asset]["Initial"], 2)
            stacked_assets[asset]["Yield"] = round(
                contract.functions.pendingGreenBen(1, portfolio_address).call() / 10 ** 18, 2)
            stacked_assets[asset]["Current"] = round(stacked_assets[asset]["Initial"] + stacked_assets[asset]["Yield"],
                                                     2)
            if asset in ben_tokens:
                asset_price = get_price(assets_balances[asset]["CA"])
                stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
                stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
                total_value_stacked_assets += stacked_assets[asset]["Current value"]
                total_value_yield += stacked_assets[asset]["Yield value"]
        if asset == "MistToken":
            ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
            abi = json.loads(ABI.read())
            bar_contract = w3.eth.contract(address=assets_balances[asset]["BAR_CA"], abi=abi)
            bar_balance = bar_contract.functions.balanceOf(portfolio_address).call()
            ratio = xsushi_ratio(assets_balances[asset]["CA"], assets_balances[asset]["BAR_CA"])
            stacked_assets[asset] = {}
            stacked_assets[asset]["Initial"] = round(assets_balances[asset]["Initial"], 2)
            stacked_assets[asset]["Current"] = round(
                (bar_balance * ratio) / 10 ** bar_contract.functions.decimals().call(), 2)
            stacked_assets[asset]["Yield"] = round(stacked_assets[asset]["Current"] - stacked_assets[asset]["Initial"],
                                                   2)
            if asset in ben_tokens:
                asset_price = get_price(assets_balances[asset]["CA"])
                stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
                stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
                total_value_stacked_assets += stacked_assets[asset]["Current value"]
                total_value_yield += stacked_assets[asset]["Yield value"]
        # if asset == "1BCH":
            # ABI = open("ABIs/PCK-Master-ABI.json", "r")
            # abi = json.loads(ABI.read())
            # contract = w3.eth.contract(address=assets_balances[asset]["CA"], abi=abi)
            # assets_balances[asset]["Yield"] = contract.functions.userInfo(0, portfolio_address).call()[1] / 10 ** 18
            # assets_balances[asset]["Current"] = assets_balances[asset]["Initial"] + assets_balances[asset]["Yield"]
        if asset == "FlexUSD":
            asset_price = get_price_from_pool(asset, bch_price)
            ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=assets_balances[asset]["CA"], abi=abi)
            stacked_assets[asset] = {}
            stacked_assets[asset]["Initial"] = round(assets_balances[asset]["Initial"], 2)
            stacked_assets[asset]["Current"] = round(
                contract.functions.balanceOf(portfolio_address).call() / 10 ** contract.functions.decimals().call(), 2)
            stacked_assets[asset]["Yield"] = round(stacked_assets[asset]["Current"] - stacked_assets[asset]["Initial"],
                                                   2)
            stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
            stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
            total_value_stacked_assets += stacked_assets[asset]["Current value"]
            total_value_yield += stacked_assets[asset]["Yield value"]
    SEP20_tokens["Total value"] = round(total_value_SEP20_tokens, 2)
    stacked_assets["Total value"] = round(total_value_stacked_assets, 2)
    stacked_assets["Total yield value"] = round(total_value_yield, 2)
    return SEP20_tokens, stacked_assets


def xsushi_ratio(sushi_token, sushi_bar):
    ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
    abi = json.loads(ABI.read())
    sushi_token_contract = w3.eth.contract(address=sushi_token, abi=abi)
    bar_balance = sushi_token_contract.functions.balanceOf(sushi_bar).call()
    bar_contract = w3.eth.contract(address=sushi_bar, abi=abi)
    bar_supply = bar_contract.functions.totalSupply().call()
    ratio = bar_balance / bar_supply
    return ratio


def get_SIDX_stats(LP_balances, bch_price):
    SIDX_stats = {}
    ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=SIDX_CA, abi=abi)
    SIDX_stats["Total supply"] = round(contract.functions.totalSupply().call() / 10 ** 18, 3)
    SIDX_stats["Admin balance"] = round(contract.functions.balanceOf(admin_wallet_address).call() / 10 ** 18, 3)
    SIDX_stats["Quorum"] = round((SIDX_stats["Total supply"] - SIDX_stats["Admin balance"]) * 0.1, 3)
    SIDX_stats["Price"] = str(round((LP_balances["Mistswap"]["Wrapped BCH"]["Current"] / LP_balances["Mistswap"]["SmartIndex"]["Current"]) * bch_price, 2)) + " USD"
    return SIDX_stats


def get_token_info(contract_address):
    ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=contract_address, abi=abi)
    return contract.functions.name().call(), contract.functions.decimals().call()


def get_LP_balances():
    LP_balances = {}
    for DEX in initial_pool_balances:
        LP_balances[DEX] = {}
        ABI = open("ABIs/UniswapV2Pair.json", "r")  # Standard ABI for LP tokens
        abi = json.loads(ABI.read())
        contract = w3.eth.contract(address=initial_pool_balances[DEX]["CA"], abi=abi)
        token0_CA = contract.functions.token0().call()
        token1_CA = contract.functions.token1().call()
        token0_ticker, token0_decimals = get_token_info(token0_CA)
        token1_ticker, token1_decimals = get_token_info(token1_CA)
        token0_reserves = contract.functions.getReserves().call()[0]
        token1_reserves = contract.functions.getReserves().call()[1]
        LP_balances[DEX][token0_ticker] = {}
        LP_balances[DEX][token1_ticker] = {}
        LP_balances[DEX][token0_ticker]["Initial"] = round(initial_pool_balances[DEX]["token0"], 2)
        LP_balances[DEX][token1_ticker]["Initial"] = round(initial_pool_balances[DEX]["token1"], 2)
        portfolio_LP_balance = contract.functions.balanceOf(portfolio_address).call()
        LP_total_supply = contract.functions.totalSupply().call()
        LP_balances[DEX][token0_ticker]["Current"] = round(
            ((portfolio_LP_balance / LP_total_supply) * token0_reserves) / 10 ** token0_decimals, 2)
        LP_balances[DEX][token1_ticker]["Current"] = round(
            ((portfolio_LP_balance / LP_total_supply) * token1_reserves) / 10 ** token1_decimals, 2)
        LP_balances[DEX][token0_ticker]["Difference"] = round(
            LP_balances[DEX][token0_ticker]["Current"] - LP_balances[DEX][token0_ticker]["Initial"], 2)
        LP_balances[DEX][token1_ticker]["Difference"] = round(LP_balances[DEX][token1_ticker]["Current"] - \
                                                              LP_balances[DEX][token1_ticker]["Initial"], 2)
    return LP_balances


def ben_listed_tokens():
    ben_listed_tokens = []
    API = "https://api.benswap.cash/api/dex/tokens"
    url = requests.get(API)
    data = url.json()
    for coin in data:
        ben_listed_tokens.append(coin["name"])
    return ben_listed_tokens


def get_price(token_CA):
    if token_CA == "0xDEa721EFe7cBC0fCAb7C8d65c598b21B6373A2b6":
        API = "https://api.benswap.cash/api/eben/priceUsd"
        url = requests.get(API)
        return url.json()
    API = "https://api.benswap.cash/api/dex/token/"
    url = requests.get(API + token_CA)
    data = url.json()
    return float(data[0]["priceUsd"])

def get_price_from_pool(asset, BCH_price):
    asset_position = 0
    BCH_position = 1
    ABI = open("ABIs/UniswapV2Pair.json", "r")  # Standard ABI for LP tokens
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=assets_balances[asset]["BCH pair"], abi=abi)
    if contract.functions.token1().call() == assets_balances[asset]["CA"]:
        asset_position = 1
        BCH_position = 0
    pool_reserves = contract.functions.getReserves().call()
    BCH_reserves = pool_reserves[BCH_position]
    asset_reserves = pool_reserves[asset_position]
    return (BCH_reserves/asset_reserves) * BCH_price


def get_BCH_price():
    API = "https://api.benswap.cash/api/bch/price"
    url = requests.get(API)
    return url.json()

def update_punks_balance():
    punks_balance = {}
    punks_balance["Wallets"] = {k: {} for k in punk_wallets}
    for wallet in punk_wallets:
        punks_balance["Wallets"][wallet] = {"Punks": [], "LAW rewards": 0}
    # As all punks in SmartIndex are stacked, we need to scan the full punks supply in the punks DEX
    ABI = open("ABIs/LAW_punks_DEX-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=law_punks_market, abi=abi)
    # Get punks owned by SmartIndex by wallet
    for i in range(1, 10000):
        owner = contract.functions.getPunkSound(i).call()[0]
        print(i)
        if owner in punk_wallets:
            punks_balance["Wallets"][owner]["Punks"].append(i)
    with open("data/PUNKS_BALANCES.json", "w") as file:
        json.dump(punks_balance, file, indent=4)
    main()

def get_law_rewards(bch_price):
    law_pending = 0
    ABI = open("ABIs/LAW_rewards-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=law_rewards, abi=abi)
    for wallet in punks_owned["Wallets"]:
        pending_reward = contract.functions.earned(wallet).call() / 10 ** 18
        punks_owned["Wallets"][wallet]["LAW rewards"] = round(pending_reward, 2)
        law_pending += pending_reward
    punks_owned["Total LAW pending"] = round(law_pending, 2)
    law_price = get_price_from_pool("LAW", bch_price)
    punks_owned["LAW pending in USD"] = round(punks_owned["Total LAW pending"] * law_price, 2)


def main():
    bch_price = get_BCH_price()
    ben_tokens = ben_listed_tokens()
    SEP20_tokens, stacked_assets = get_balances(ben_tokens, bch_price)
    LP_balances = get_LP_balances()
    SIDX_stats = get_SIDX_stats(LP_balances, bch_price)
    get_law_rewards(bch_price)
    with open('data/SIDX_STATS.json', 'w') as file:
        json.dump(SIDX_stats, file, indent=4)
    with open('data/SEP20_BALANCES.json', 'w') as file:
        json.dump(SEP20_tokens, file, indent=4)
    with open('data/STACKED_ASSETS.json', 'w') as file:
        json.dump(stacked_assets, file, indent=4)
    with open('data/LP_BALANCES.json', 'w') as file:
        json.dump(LP_balances, file, indent=4)
    with open('data/PUNKS_BALANCES.json', 'w') as file:
        json.dump(punks_owned, file, indent=4)


if __name__ == "__main__":
    main()
