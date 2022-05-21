import json
from web3 import Web3, exceptions
import requests
import matplotlib.pyplot as plt
import numpy as np
from time import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import FirefoxOptions
import logging


logger = logging.getLogger("app.engine")

w3 = Web3(Web3.HTTPProvider('https://smartbch.greyh.at'))
if not w3.isConnected():
    w3 = Web3(Web3.HTTPProvider('https://smartbch.fountainhead.cash/mainnet'))

portfolio_address = w3.toChecksumAddress("0xE1ae30Fbb31bE2FB59D1c44dBEf8649C386E26B3")
admin_wallet_address = w3.toChecksumAddress("0xd11bb6a7981780aADc722146a306f7104fD93E9c")
SIDX_CA = w3.toChecksumAddress("0xF05bD3d7709980f60CD5206BddFFA8553176dd29")
law_punks_CA = w3.toChecksumAddress("0xff48aAbDDACdc8A6263A2eBC6C1A68d8c46b1bf7")
law_punks_market = w3.toChecksumAddress("0xc062bf9FaBE930FF8061f72b908AB1b702b3FdD6")
law_level_address = w3.toChecksumAddress("0x9E9eACB7E5dCc374d3108598054787ccae967544")
law_rewards = w3.toChecksumAddress("0xbeAAe3E87Bf71C97e458e2b9C84467bdc3b871c6")
punk_wallets = [portfolio_address,  # Punks wallet 1
                "0x3484f575A3d3b4026B4708997317797925A236ae",  # Punks wallet 2
                "0x57BB80fdab3ca9FDBC690F4b133010d8615e77b3"]  # Punks wallet 3

voting_wallets = ["0xa3533751171786035fC440bFeF3F535093EAd686",
                  "0xe26B069480c24b195Cd48c8d61857B5Aaf610569",
                  "0x711CA8Da9bE7a3Ee698dD76C632A19cFB6F768Cb"]

with open("data/PUNKS_BALANCES.json", "r") as file:
    punks_owned = json.load(file)

cheque_CA = w3.toChecksumAddress("0xa36C479eEAa25C0CFC7e099D3bEbF7A7F1303F40")

assets_balances = {
    "MistToken": {"Initial": 226146.43, "Stacked": True, "CA": "0x5fA664f69c2A4A3ec94FaC3cBf7049BD9CA73129",
                  "BAR_CA": "0xC41C680c60309d4646379eD62020c534eB67b6f4",
                  "BCH pair": "0x674A71E69fe8D5cCff6fdcF9F1Fa4262Aa14b154", "Liquid": True,
                  "harvest_ABI": "SushiBar.json"},
    "Tango": {"Initial": 23897.252, "Stacked": True, "CA": "0x73BE9c8Edf5e951c9a0762EA2b1DE8c8F38B5e91",
              "BAR_CA": "0x98Ff640323C059d8C4CB846976973FEEB0E068aA",
              "BCH pair": "0x4b773a2ea30C6A77564E4FaE60204e7Bc0a81A90", "Liquid": True},
    "FlexUSD": {"Initial": 511.62, "Stacked": True, "CA": "0x7b2B3C5308ab5b2a1d9a94d20D35CCDf61e05b72",
                "BCH pair": "0x24f011f12Ea45AfaDb1D4245bA15dCAB38B43D13", "Liquid": True},
    "Green Ben": {"Initial": 1875.168, "Stacked": True, "CA": "0xDEa721EFe7cBC0fCAb7C8d65c598b21B6373A2b6",
                  "Liquid": True, "BCH pair": "0x0D4372aCc0503Fbcc7EB129e0De3283c348B82c3", "harvest_CA": "0xDEa721EFe7cBC0fCAb7C8d65c598b21B6373A2b6", "harvest_pool_id": 1,
                  "harvest_ABI": "BEN-Master-ABI.json"},
    "Celery": {"Initial": 1674817.26, "Stacked": True, "CA": "0x7642Df81b5BEAeEb331cc5A104bd13Ba68c34B91",
               "BCH pair": "0x5775D98022590dc60E9c4Ae0a1c56bF1fD8fcaDC", "Liquid": False},
    "FLEX Coin": {"Initial": 142.804, "Stacked": True, "CA": "0x98Dd7eC28FB43b3C4c770AE532417015fa939Dd3",
                  "Liquid": True},
    "LAW": {"Stacked": True, "CA": "0x0b00366fBF7037E9d75E4A569ab27dAB84759302",
            "BCH pair": "0xd55a9A41666108d10d31BAeEea5D6CdF3be6C5DD", "Liquid": True},
    "DAIQUIRI": {"Initial": 14281.791, "Stacked": True, "CA": "0xE4D74Af73114F72bD0172fc7904852Ee2E2b47B0",
                 "BCH pair": "0xF1Ac59acb449C8e2BA9D222cA1275b3f4f9a455C", "Liquid": True,
                 "harvest_CA": "0xE4D74Af73114F72bD0172fc7904852Ee2E2b47B0", "harvest_pool_id": 0,
                 "harvest_ABI": "Tropical-Master-ABI.json"},
    "LNS": {"Initial": 44.9947, "Stacked": True, "CA": "0x35b3Ee79E1A7775cE0c11Bd8cd416630E07B0d6f",
            "BAR_CA": "0xBE7E034c86AC2a302f69ef3975e3D14820cC7660",
            "BCH pair": "0x7f3F57C92681c9a132660c468f9cdff456fC3Fd7", "Liquid": True, "harvest_ABI": "SushiBar.json"},
    "GOB": {"Initial": 5.524333, "Stacked": True, "CA": "0x56381cB87C8990971f3e9d948939e1a95eA113a3",
            "BCH pair": "0x86B0fD64234a747681f0235B6Cc5FE04a4D95B31", "Liquid": True,
            "harvest_CA": "0x48B8aCe692ad8BD2E3139C65bFf7d28c048F8f00", "harvest_ABI": "GOB-StakingContract.json"},
    "BCH": {"Stacked": False, "Liquid": True}
}

initial_pool_balances = {
    "Mistswap": {"CA": "0x7E1B9F1e286160A80ab9B04D228C02583AeF90B5", "token0": 5, "token1": 23711.1}
    # Token0 is WBCH, Token1 is SIDX
}

extra_pool_balances = {
    "Mistswap": {"CA": "0x7E1B9F1e286160A80ab9B04D228C02583AeF90B5", "token0": 2.976577, "token1": 978.9463},
    "Tangoswap": {"CA": "0x4509Ff66a56cB1b80a6184DB268AD9dFBB79DD53", "token0": 3.9533, "token1": 1084.6799}
    }  # Token0 is WBCH, Token1 is SIDX

farms = {"Mistswap": {"factory": "0x3A7B9D0ed49a90712da4E087b17eE4Ac1375a5D4",
                      "factory_ABI": "MIST-Master-ABI.json",
                      "farms": [{"lp_CA": "0x4fF52e9D7824EC9b4e0189F11B5aA0F02b459b03",
                                 "pool_id": 2,
                                 "lp_token_amount": 344.686876049931219858 * 10 ** 18,
                                 "initial_token0_amount": 882.588,  # FlexUSD
                                 "token_0_bch_pair": "0x24f011f12Ea45AfaDb1D4245bA15dCAB38B43D13",
                                 "token_0_assets_position": (1, 0),
                                 "initial_token1_amount": 142.8045,  # FLEX
                                 "token_1_bch_pair": "0x8E647c88243A374E60eb644Afb13FfFd52278051",
                                 "token_1_assets_position": (1, 0),
                                 "reward coin": "MistToken"},
                                {"lp_CA": "0x1D5A7bea34EE984D54aF6Ff355A1Cb54c29eb546",
                                 "pool_id": 47,
                                 "lp_token_amount": 188.882290723925139574 * 10 ** 18,
                                 "initial_token0_amount": 237.61,  # LAW
                                 "token_0_bch_pair": "0xd55a9A41666108d10d31BAeEea5D6CdF3be6C5DD",
                                 "token_0_assets_position": (0, 1),
                                 "initial_token1_amount": 154.06,  # LawUSD
                                 "token_1_bch_pair": "0xFEdfE67b179b2247053797d3b49d167a845a933e",
                                 "token_1_assets_position": (1, 0),
                                 "reward coin": "MistToken"},
                                {"lp_CA": "0x20943aD7855bdE06Dd41BB89C9D2efE05DB329EC",
                                 "pool_id": 32,
                                 "lp_token_amount": 17618193073021479641,
                                 "initial_token0_amount": 0.498718,  # WBCH
                                 "token_0_bch_pair": "0x3743eC0673453E5009310C727Ba4eaF7b3a1cc04", #Get price from pool will jusr return BCH price
                                 "token_0_assets_position": (0, 1),
                                 "initial_token1_amount": 758.67058,  # JOY
                                 "token_1_bch_pair": "0x20943aD7855bdE06Dd41BB89C9D2efE05DB329EC",
                                 "token_1_assets_position": (1, 0),
                                 "reward coin": "MistToken"}
                                ]},
         "Tangoswap": {"factory": "0x38cC060DF3a0498e978eB756e44BD43CC4958aD9",
                       "factory_ABI": "MIST-Master-ABI.json",
                       "farms": [{"lp_CA": "0xcdb6081DCb9fd2b3d48927790DF7757E8d137fF4",
                                  "pool_id": 27,
                                  "lp_token_amount": 2602.810500549833989903 * 10 ** 18,
                                  "initial_token0_amount": 599.648,  # FlexUSD
                                  "token_0_bch_pair": "0x24f011f12Ea45AfaDb1D4245bA15dCAB38B43D13",
                                  "token_0_assets_position": (1, 0),
                                  "initial_token1_amount": 11910.1,  # XTANGO
                                  "token_1_bch_pair": "0x7FbcD4B5b7838F3C22151d492cB7E30B28dED77a",
                                  "token_1_assets_position": (1, 0),
                                  "reward coin": "Tango"}]
                       }
         }

pie_chart_data = {}


def get_balances(bch_price):
    stacked_assets = {}
    SEP20_tokens = {}
    total_value_SEP20_tokens = 0
    total_value_stacked_assets = 0
    total_value_yield = 0
    global total_liquid_value
    global total_illiquid_value
    for asset in assets_balances:
        if not assets_balances[asset]["Stacked"]:
            if asset == "BCH":
                SEP20_tokens[asset] = {}
                SEP20_tokens[asset]["Current"] = round(
                    w3.eth.get_balance(portfolio_address) / 10 ** 18, 2)
                SEP20_tokens[asset]["Current value"] = round(SEP20_tokens[asset]["Current"] * bch_price, 2)
                total_value_SEP20_tokens += SEP20_tokens[asset]["Current value"]
                total_liquid_value += SEP20_tokens[asset]["Current value"]
                pie_chart_data[asset] = SEP20_tokens[asset]["Current value"]
            else:
                ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address=assets_balances[asset]["CA"], abi=abi)
                SEP20_tokens[asset] = {}
                SEP20_tokens[asset]["Current"] = round(
                    contract.functions.balanceOf(portfolio_address).call() / 10 ** contract.functions.decimals().call(),
                    2)
                if "BCH pair" in assets_balances[asset]:
                    asset_price = get_price_from_pool(asset, bch_price)
                    SEP20_tokens[asset]["Current value"] = round(SEP20_tokens[asset]["Current"] * asset_price, 2)
                    total_value_SEP20_tokens += SEP20_tokens[asset]["Current value"]
                    pie_chart_data[asset] = SEP20_tokens[asset]["Current value"]
                if assets_balances[asset]["Liquid"]:
                    total_liquid_value += SEP20_tokens[asset]["Current value"]
                else:
                    total_illiquid_value += SEP20_tokens[asset]["Current value"]
        if asset == "Celery":
            ABI = open("ABIs/CLY-ABI.json", "r")  # ABI for CLY token
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=assets_balances[asset]["CA"], abi=abi)
            wallet_balance = contract.functions.balanceOf(
                portfolio_address).call()  # CLY Neither in stacking nor payout mode
            status = contract.functions.getStatus(portfolio_address).call()  # Get Status of account
            if status == 0:  # Account in payout mode
                decimals = contract.functions.decimals().call()
                stacked_assets[asset] = {}
                stacked_assets[asset]["Initial"] = round((wallet_balance + contract.functions.getLastStakingBalance(
                    portfolio_address).call()) / 10 ** decimals, 2)
                # Now, let's determine the amount available for collection
                last_processed_time = contract.functions.getLastProcessedTime(portfolio_address).call()
                delta = int(time()) - last_processed_time
                year_percentage = delta / 31536000  # Seconds in a year
                payout_amount = round(stacked_assets[asset]["Initial"] * year_percentage, 2)
                stacked_assets[asset]["Current"] = round((stacked_assets[asset]["Initial"] + payout_amount), 2)
                stacked_assets[asset]["Yield"] = round(payout_amount, 2)
                stacked_assets[asset]["Mode"] = "Payout"
            else:
                last_processed_time = contract.functions.getLastProcessedTime(portfolio_address).call()
                delta = int(time()) - last_processed_time
                year_percentage = delta / 31536000  # Seconds in a year
                account_balance = 2 ** year_percentage * contract.functions.getAccountBalance(portfolio_address).call()
                stacked_assets[asset] = {}
                stacked_assets[asset]["Initial"] = round(assets_balances[asset]["Initial"], 2)
                stacked_assets[asset]["Current"] = round(
                    (wallet_balance + account_balance) / 10 ** contract.functions.decimals().call(), 2)
                stacked_assets[asset]["Yield"] = round(
                    stacked_assets[asset]["Current"] - stacked_assets[asset]["Initial"],
                    2)
                stacked_assets[asset]["Mode"] = "Stacking"
            if "BCH pair" in assets_balances[asset]:
                asset_price = get_price_from_pool(asset, bch_price)
                stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
                total_value_stacked_assets += stacked_assets[asset]["Current value"]
                stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
                total_value_yield += stacked_assets[asset]["Yield value"]
                pie_chart_data[asset] = stacked_assets[asset]["Current value"]
            total_illiquid_value += stacked_assets[asset]["Current value"] + stacked_assets[asset]["Yield value"]
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
            if "BCH pair" in assets_balances[asset]:
                asset_price = get_price_from_pool(asset, bch_price, assets_positions=(1, 0))
                stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
                total_value_stacked_assets += stacked_assets[asset]["Current value"]
                stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
                total_value_yield += stacked_assets[asset]["Yield value"]
                pie_chart_data[asset] = stacked_assets[asset]["Current value"]
            total_liquid_value += stacked_assets[asset]["Current value"] + stacked_assets[asset]["Yield value"]
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
            if "BCH pair" in assets_balances[asset]:
                asset_price = get_price_from_pool(asset, bch_price)
                stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
                total_value_stacked_assets += stacked_assets[asset]["Current value"]
                stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
                pie_chart_data[asset] = stacked_assets[asset]["Current value"]
            total_liquid_value += stacked_assets[asset]["Current value"] + stacked_assets[asset]["Yield value"]
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
            pie_chart_data[asset] = stacked_assets[asset]["Current value"]
            total_value_stacked_assets += stacked_assets[asset]["Current value"]
            total_value_yield += stacked_assets[asset]["Yield value"]
            total_liquid_value += stacked_assets[asset]["Current value"] + stacked_assets[asset]["Yield value"]
        if asset == "DAIQUIRI":
            ABI = open("ABIs/Tropical-Master-ABI.json", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=assets_balances[asset]["CA"], abi=abi)
            stacked_assets[asset] = {}
            stacked_assets[asset]["Initial"] = round(assets_balances[asset]["Initial"], 2)
            stacked_assets[asset]["Yield"] = round(
                contract.functions.pendingDaiquiri(0, portfolio_address).call() / 10 ** 18, 2)
            stacked_assets[asset]["Current"] = round(stacked_assets[asset]["Initial"] + stacked_assets[asset]["Yield"],
                                                     2)
            asset_price = get_price_from_pool(asset, bch_price)
            stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
            stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
            pie_chart_data[asset] = stacked_assets[asset]["Current value"]
            total_value_stacked_assets += stacked_assets[asset]["Current value"]
            total_value_yield += stacked_assets[asset]["Yield value"]
            total_liquid_value += stacked_assets[asset]["Current value"] + stacked_assets[asset]["Yield value"]
        if asset == "LNS":
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
            if "BCH pair" in assets_balances[asset]:
                asset_price = get_price_from_pool(asset, bch_price)
                stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
                total_value_stacked_assets += stacked_assets[asset]["Current value"]
                stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
                total_value_yield += stacked_assets[asset]["Yield value"]
                pie_chart_data[asset] = stacked_assets[asset]["Current value"]
        if asset == "GOB":
            # GOB has 9 decimals
            asset_price = get_price_from_pool(asset, bch_price) / 10 ** 9
            # We get current balance from the sGOB token contract
            ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address="0x47c61F29B1458d234409Ebbe4B6a70F3b16528EF", abi=abi)
            stacked_assets[asset] = {}
            stacked_assets[asset]["Initial"] = round(assets_balances[asset]["Initial"], 2)
            stacked_assets[asset]["Current"] = round(
                contract.functions.balanceOf(portfolio_address).call() / 10 ** contract.functions.decimals().call(), 2)
            stacked_assets[asset]["Yield"] = round(stacked_assets[asset]["Current"] - stacked_assets[asset]["Initial"],
                                                   2)
            stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
            stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
            pie_chart_data[asset] = stacked_assets[asset]["Current value"]
            total_value_stacked_assets += stacked_assets[asset]["Current value"]
            total_value_yield += stacked_assets[asset]["Yield value"]
            total_liquid_value += stacked_assets[asset]["Current value"] + stacked_assets[asset]["Yield value"]
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


def get_SIDX_stats(bch_price):
    SIDX_stats = {}
    ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=SIDX_CA, abi=abi)
    SIDX_stats["Total supply"] = round(contract.functions.totalSupply().call() / 10 ** 18, 3)
    SIDX_stats["Admin balance"] = round(contract.functions.balanceOf(admin_wallet_address).call() / 10 ** 18, 3)
    SIDX_stats["Quorum"] = round((SIDX_stats["Total supply"] - SIDX_stats["Admin balance"]) * 0.1, 3)
    price = get_price_from_pool("0x7E1B9F1e286160A80ab9B04D228C02583AeF90B5", bch_price,
                                assets_positions=(1, 0))  # (Asset and BCH position on LP)
    SIDX_stats["Price"] = str(round(price, 2)) + " USD"
    return SIDX_stats


def get_token_info(contract_address):
    ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=contract_address, abi=abi)
    return contract.functions.name().call(), contract.functions.decimals().call()


def get_LP_balances(initial_pool_balances, wallet_address, bch_price, sidx_price):
    global total_liquid_value
    global total_rewards_value
    global SIDX_LP_value
    # Modified for Mistswap farm
    LP_balances = {}
    for DEX in initial_pool_balances:
        LP_balances[DEX] = {}
        # First, get current LP balance and rewards
        if DEX == "Mistswap":
            ABI = open("ABIs/MIST-Master-ABI.json", 'r')
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address="0x3A7B9D0ed49a90712da4E087b17eE4Ac1375a5D4", abi=abi)
            pool_id = 44
            portfolio_LP_balance = contract.functions.userInfo(pool_id, wallet_address).call()[0]
            reward = contract.functions.pendingSushi(pool_id, wallet_address).call()
            asset_price = get_price_from_pool("MistToken", bch_price)
        if DEX == "Tangoswap":
            ABI = open("ABIs/MIST-Master-ABI.json", 'r')
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address="0x38cC060DF3a0498e978eB756e44BD43CC4958aD9", abi=abi)
            pool_id = 32
            portfolio_LP_balance = contract.functions.userInfo(pool_id, wallet_address).call()[0]
            reward = contract.functions.pendingSushi(pool_id, wallet_address).call()
            asset_price = get_price_from_pool("Tango", bch_price)
        # Get assets in liquidity pools
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
        LP_total_supply = contract.functions.totalSupply().call()
        LP_balances[DEX][token0_ticker]["Current"] = round(
            ((portfolio_LP_balance / LP_total_supply) * token0_reserves) / 10 ** token0_decimals, 2)
        LP_balances[DEX][token0_ticker]["Current value"] = round(LP_balances[DEX][token0_ticker]["Current"] * bch_price,
                                                                 2)
        total_liquid_value += LP_balances[DEX][token0_ticker]["Current value"]
        SIDX_LP_value += LP_balances[DEX][token0_ticker]["Current value"]
        LP_balances[DEX][token1_ticker]["Current"] = round(
            ((portfolio_LP_balance / LP_total_supply) * token1_reserves) / 10 ** token1_decimals, 2)
        LP_balances[DEX][token1_ticker]["Current value"] = round(
            LP_balances[DEX][token1_ticker]["Current"] * sidx_price, 2)
        total_liquid_value += LP_balances[DEX][token1_ticker]["Current value"]
        SIDX_LP_value += LP_balances[DEX][token1_ticker]["Current value"]
        LP_balances[DEX][token0_ticker]["Difference"] = round(
            LP_balances[DEX][token0_ticker]["Current"] - LP_balances[DEX][token0_ticker]["Initial"], 2)
        LP_balances[DEX][token1_ticker]["Difference"] = round(LP_balances[DEX][token1_ticker]["Current"] - \
                                                              LP_balances[DEX][token1_ticker]["Initial"], 2)
        LP_balances[DEX]["Reward"] = round(reward / 10 ** 18, 2)
        LP_balances[DEX]["Reward value"] = round(LP_balances[DEX]["Reward"] * asset_price, 2)
        total_rewards_value += LP_balances[DEX]["Reward value"]
    return LP_balances

def get_price(token_CA):
    if token_CA == "0xDEa721EFe7cBC0fCAb7C8d65c598b21B6373A2b6":
        API = "https://api.benswap.cash/api/eben/priceUsd"
        url = requests.get(API)
        return url.json()
    API = "https://api.benswap.cash/api/dex/token/"
    url = requests.get(API + token_CA)
    data = url.json()
    return float(data[0]["priceUsd"])


def get_price_from_pool(asset, BCH_price, assets_positions=(0, 1)):
    # assets_positions is a tuple with the format (asset_positions, BCH_position) used when passing BCH pair address
    asset_position, BCH_position = assets_positions
    ABI = open("ABIs/UniswapV2Pair.json", "r")  # Standard ABI for LP tokens
    abi = json.loads(ABI.read())
    if asset in assets_balances:
        contract = w3.eth.contract(address=assets_balances[asset]["BCH pair"], abi=abi)
        if contract.functions.token1().call() == assets_balances[asset]["CA"]:
            asset_position = 1
            BCH_position = 0
    else:  # Directly pass BCH pair address
        if asset == "0x3743eC0673453E5009310C727Ba4eaF7b3a1cc04":
            return BCH_price
        else:
            contract = w3.eth.contract(address=asset, abi=abi)
    pool_reserves = contract.functions.getReserves().call()
    BCH_reserves = pool_reserves[BCH_position]
    asset_reserves = pool_reserves[asset_position]
    return (BCH_reserves / asset_reserves) * BCH_price


def get_BCH_price():
    prices = []
    API = "https://api.benswap.cash/api/bch/price"
    url = requests.get(API)
    if type(url.json()) == float:
        prices.append(url.json())
    API = 'https://coincodex.com/api/coincodex/get_coin/BCH'
    url = requests.get(API)
    if type(url.json()['last_price_usd']) == float:
        prices.append(url.json()['last_price_usd'])
    API = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin-cash&vs_currencies=USD'
    url = requests.get(API)
    if type(url.json()['bitcoin-cash']['usd']) == float:
        prices.append(url.json()['bitcoin-cash']['usd'])
    mean = sum(prices) / len(prices)
    return mean


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
    global total_liquid_value
    global total_illiquid_value
    global total_rewards_value
    law_pending = 0
    punks_number = 0
    ABI = open("ABIs/LAW_rewards-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=law_rewards, abi=abi)
    for wallet in punks_owned["Wallets"]:
        pending_reward = contract.functions.earned(wallet).call() / 10 ** 18
        punks_owned["Wallets"][wallet]["LAW rewards"] = round(pending_reward, 2)
        law_pending += pending_reward
        for punk in punks_owned["Wallets"][wallet]["Punks"]:
            punks_number += 1
    punks_owned["Total LAW pending"] = round(law_pending, 2)
    law_price = get_price_from_pool("LAW", bch_price)
    punks_owned["LAW pending in USD"] = round(punks_owned["Total LAW pending"] * law_price, 2)
    total_liquid_value += punks_owned["LAW pending in USD"]
    total_rewards_value += punks_owned["LAW pending in USD"]
    # Now get punk's floor price using selenium library
    url = "https://blockng.money/#/punks"
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    driver = webdriver.Firefox(options=opts)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    try:
        status = wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, "punks-market-info-item-num.BCH"), "."))
        element = driver.find_element(By.CLASS_NAME, 'punks-market-info-item-num.BCH')
        floor_price = float(element.text.split()[0])
        driver.quit()
        punks_owned["Floor price"] = floor_price  # In BCH
        punks_owned["Total floor value"] = round(floor_price * punks_number * bch_price, 2)  # In USD
        total_illiquid_value += punks_owned["Total floor value"]
    except Exception as e:
        element = driver.find_element(By.CLASS_NAME, 'punks-market-info-item-num.BCH')
        if element.text.split()[0].isnumeric():
            floor_price = float(element.text.split()[0])
            driver.quit()
            punks_owned["Floor price"] = floor_price  # In BCH
            punks_owned["Total floor value"] = round(floor_price * punks_number * bch_price, 2)  # In USD
            total_illiquid_value += punks_owned["Total floor value"]
            print('Done')
        else:
            driver.quit
            logger.info(f'Error found trying to get punks floor price: {e}')
            import app.email as email
            email.send_email_to_admin(f'Error found trying to get punks floor price: {e}')
            total_illiquid_value += punks_owned["Total floor value"]


def get_farms(bch_price):
    global total_liquid_value
    global total_illiquid_value
    global total_rewards_value
    for DEX in farms:
        for i in range(len(farms[DEX]["farms"])):
            # First, get LP balances
            ABI = open("ABIs/UniswapV2Pair.json", "r")  # Standard ABI for LP tokens
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=farms[DEX]["farms"][i]["lp_CA"], abi=abi)
            token0_CA = contract.functions.token0().call()
            token1_CA = contract.functions.token1().call()
            token0_ticker, token0_decimals = get_token_info(token0_CA)
            token1_ticker, token1_decimals = get_token_info(token1_CA)
            token0_reserves = contract.functions.getReserves().call()[0]
            token1_reserves = contract.functions.getReserves().call()[1]
            LP_total_supply = contract.functions.totalSupply().call()
            farms[DEX]["farms"][i]["Coins"] = {}
            farms[DEX]["farms"][i]["Coins"][token0_ticker] = {
                "Initial amount": round(farms[DEX]["farms"][i]["initial_token0_amount"], 2)}
            farms[DEX]["farms"][i]["Coins"][token1_ticker] = {
                "Initial amount": round(farms[DEX]["farms"][i]["initial_token1_amount"], 2)}
            farms[DEX]["farms"][i]["Coins"][token0_ticker]["Current"] = round(
                ((farms[DEX]["farms"][i][
                      "lp_token_amount"] / LP_total_supply) * token0_reserves) / 10 ** token0_decimals, 2)
            farms[DEX]["farms"][i]["Coins"][token0_ticker]["Current value"] = round(
                get_price_from_pool(farms[DEX]["farms"][i]["token_0_bch_pair"], bch_price,
                                    assets_positions=farms[DEX]["farms"][i]["token_0_assets_position"]) *
                farms[DEX]["farms"][i]["Coins"][token0_ticker]["Current"], 2)
            total_liquid_value += farms[DEX]["farms"][i]["Coins"][token0_ticker]["Current value"]
            farms[DEX]["farms"][i]["Coins"][token1_ticker]["Current"] = round(
                ((farms[DEX]["farms"][i][
                      "lp_token_amount"] / LP_total_supply) * token1_reserves) / 10 ** token1_decimals, 2)
            farms[DEX]["farms"][i]["Coins"][token1_ticker]["Current value"] = round(
                get_price_from_pool(farms[DEX]["farms"][i]["token_1_bch_pair"], bch_price,
                                    assets_positions=farms[DEX]["farms"][i]["token_1_assets_position"]) *
                farms[DEX]["farms"][i]["Coins"][token1_ticker]["Current"], 2)
            total_liquid_value += farms[DEX]["farms"][i]["Coins"][token1_ticker]["Current value"]
            farms[DEX]["farms"][i]["Coins"][token0_ticker]["Difference"] = round(
                farms[DEX]["farms"][i]["Coins"][token0_ticker]["Current"] -
                farms[DEX]["farms"][i]["Coins"][token0_ticker]["Initial amount"], 2)
            farms[DEX]["farms"][i]["Coins"][token1_ticker]["Difference"] = round(
                farms[DEX]["farms"][i]["Coins"][token1_ticker]["Current"] - \
                farms[DEX]["farms"][i]["Coins"][token1_ticker]["Initial amount"], 2)
            # Now, it's time to get the rewards
            ABI_path = "ABIs/" + farms[DEX]["factory_ABI"]
            ABI = open(ABI_path, "r")  # Factory contract ABI
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=farms[DEX]["factory"], abi=abi)
            reward = contract.functions.pendingSushi(farms[DEX]["farms"][i]["pool_id"], portfolio_address).call()
            farms[DEX]["farms"][i]["reward"] = round((reward / 10 ** 18), 2)
            if farms[DEX]["farms"][i]["reward coin"] in assets_balances:
                asset_price = get_price_from_pool(farms[DEX]["farms"][i]["reward coin"], bch_price)
                farms[DEX]["farms"][i]["reward value"] = round((farms[DEX]["farms"][i]["reward"] * asset_price), 2)
                total_rewards_value += farms[DEX]["farms"][i]["reward value"]


def make_pie_chart():
    labels = []
    values = []
    for asset in pie_chart_data:
        labels.append(asset)
        values.append(pie_chart_data[asset])

    y = np.array(values)

    plt.pie(y, labels=labels)
    plt.savefig("app/static/pie_chart.png")


def start_celery_stake():
    if not check_bch_balance(portfolio_address):
        import app.email as email
        email.send_email_to_admin("Not enough BCH to start CLY stake")
        return
    import os
    ABI = open("ABIs/CLY-ABI.json", "r")  # ABI for CLY token
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address="0x7642Df81b5BEAeEb331cc5A104bd13Ba68c34B91", abi=abi)
    nonce = w3.eth.get_transaction_count(portfolio_address)
    stake_cly_tx = contract.functions.startStake().buildTransaction(
        {'chainId': 10000,
         'gas': 123209,
         'gasPrice': w3.toWei('1.05', 'gwei'),
         'nonce': nonce})
    # We're gonna check if there's enough BCH for the tx
    private_key = os.environ.get('PORTFOLIO_PRIV_KEY')
    if private_key == None:
        import app.email as email
        email.send_email_to_admin("Portfolio private key not loaded on shell environment")
    signed_txn = w3.eth.account.sign_transaction(stake_cly_tx, private_key=private_key)
    w3.eth.send_raw_transaction(signed_txn.rawTransaction)


def start_celery_payout():
    # We're gonna check if there's enough BCH for the tx
    if not check_bch_balance(portfolio_address):
        import app.email as email
        email.send_email_to_admin("Not enough BCH to start CLY payout")
        return
    import os
    ABI = open("ABIs/CLY-ABI.json", "r")  # ABI for CLY token
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address="0x7642Df81b5BEAeEb331cc5A104bd13Ba68c34B91", abi=abi)
    nonce = w3.eth.get_transaction_count(portfolio_address)
    payout_cly_tx = contract.functions.startPayout().buildTransaction(
        {'chainId': 10000,
         'gas': 81716,
         'gasPrice': w3.toWei('1.05', 'gwei'),
         'nonce': nonce})
    private_key = os.environ.get('PORTFOLIO_PRIV_KEY')
    if private_key == None:
        import app.email as email
        email.send_email_to_admin("Portfolio private key not loaded on shell environment")
    signed_txn = w3.eth.account.sign_transaction(payout_cly_tx, private_key=private_key)
    w3.eth.send_raw_transaction(signed_txn.rawTransaction)


def swapBCHtoSIDX(bch_balance):
    # Let's load Mistswap router contract
    ABI = open("ABIs/UniswapV2Router.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address="0x5d0bF8d8c8b054080E2131D8b260a5c6959411B8", abi=abi)
    WBCH_contract = contract.functions.WETH().call()
    # We will swap 98% of our BCH in the wallet
    bch_to_swap = bch_balance * 0.98
    BCH_amount_in, SIDX_amount_out = contract.functions.getAmountsOut(int(bch_to_swap), [WBCH_contract, SIDX_CA]).call()
    # Now let's construct the swap tx
    import os
    nonce = w3.eth.get_transaction_count(portfolio_address)
    deadline = round(time()) + 60  # Added 60 sec to the current time
    bch_sidx_swap_tx = contract.functions.swapExactETHForTokens(int(SIDX_amount_out * 0.95), [WBCH_contract, SIDX_CA],
                                                                portfolio_address, deadline).buildTransaction(
        {'value': BCH_amount_in,
         'chainId': 10000,
         'gas': 196524,
         'gasPrice': w3.toWei('1.05', 'gwei'),
         'nonce': nonce})
    private_key = os.environ.get('PORTFOLIO_PRIV_KEY')
    signed_txn = w3.eth.account.sign_transaction(bch_sidx_swap_tx, private_key=private_key)
    w3.eth.send_raw_transaction(signed_txn.rawTransaction)


def swapSIDXtoBCH():
    # First let's determine SIDX balance
    ABI = open("ABIs/ERC20-ABI.json")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=SIDX_CA, abi=abi)
    SIDX_balance = contract.functions.balanceOf(portfolio_address).call()
    if SIDX_balance == 0:
        return 'No SIDX to swap'
    # Let's load Mistswap router contract
    ABI = open("ABIs/UniswapV2Router.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address="0x5d0bF8d8c8b054080E2131D8b260a5c6959411B8", abi=abi)
    WBCH_contract = contract.functions.WETH().call()
    BCH_amount_out = contract.functions.getAmountsOut(int(SIDX_balance), [SIDX_CA, WBCH_contract]).call()[1]
    # Now let's construct the swap tx
    import os
    nonce = w3.eth.get_transaction_count(portfolio_address)
    deadline = round(time()) + 60  # Added 60 sec to the current time
    sidx_bch_swap_tx = contract.functions.swapExactTokensForETH(int(SIDX_balance), int(BCH_amount_out * 0.95),
                                                                [SIDX_CA, WBCH_contract], portfolio_address,
                                                                deadline).buildTransaction(
        {'chainId': 10000,
         'gas': 200761,
         'gasPrice': w3.toWei('1.05', 'gwei'),
         'nonce': nonce})
    private_key = os.environ.get('PORTFOLIO_PRIV_KEY')
    signed_txn = w3.eth.account.sign_transaction(sidx_bch_swap_tx, private_key=private_key)
    w3.eth.send_raw_transaction(signed_txn.rawTransaction)


def wash_trading_bot(min_usd_balance):
    import time
    i = 1
    # min_usd_balance is the minimum USD balance in the account in the form of BCH required
    # It depends on how much do you want to spend on fees
    bch_price = get_BCH_price()
    bch_balance = w3.eth.get_balance(portfolio_address)
    while min_usd_balance < bch_price * (bch_balance / 10 ** 18):
        swapBCHtoSIDX(bch_balance)
        time.sleep(25)
        swapSIDXtoBCH()
        print(f"Round {i} completed")
        i += 1
        time.sleep(25)
        bch_price = get_BCH_price()
        bch_balance = w3.eth.get_balance(portfolio_address)
    return "Threshold reached"


def check_bch_balance(account):
    bch_balance = w3.eth.get_balance(account)
    if bch_balance > 2000000000000000:
        return True
    else:
        return False


def harvest_pools_rewards(pool_name, amount=0):
    if pool_name in {"Green Ben", "DAIQUIRI"}:
        ABI = open(f"ABIs/{assets_balances[pool_name]['harvest_ABI']}", "r")
        abi = json.loads(ABI.read())
        contract = w3.eth.contract(address=assets_balances[pool_name]["harvest_CA"], abi=abi)
        harvest_tx = contract.functions.withdraw(assets_balances[pool_name]["harvest_pool_id"], 0).buildTransaction(
            {'chainId': 10000,
             'from': portfolio_address,
             'gasPrice': w3.toWei('1.046739556', 'gwei')
             })
        send_transaction(pool_name, harvest_tx)
    if pool_name in {"MistToken", "LNS"}:
        ABI = open(f"ABIs/{assets_balances[pool_name]['harvest_ABI']}", "r")
        abi = json.loads(ABI.read())
        ratio = xsushi_ratio(assets_balances[pool_name]["CA"], assets_balances[pool_name]["BAR_CA"])
        amount_to_harvest = amount / ratio
        contract = w3.eth.contract(address=assets_balances[pool_name]["BAR_CA"], abi=abi)
        harvest_tx = contract.functions.leave(int(amount_to_harvest)).buildTransaction(
            {'chainId': 10000,
             'from': portfolio_address,
             'gasPrice': w3.toWei('1.046739556', 'gwei')
             })
        send_transaction(pool_name, harvest_tx)
    if pool_name == "GOB":
        ABI = open(f"ABIs/{assets_balances[pool_name]['harvest_ABI']}", "r")
        abi = json.loads(ABI.read())
        contract = w3.eth.contract(address=assets_balances[pool_name]["harvest_CA"], abi=abi)
        harvest_amount = amount / 10 ** 9  # GOB has 9 decimals
        harvest_tx = contract.functions.unstake(int(harvest_amount), True).buildTransaction(
            {'chainId': 10000,
             'from': portfolio_address,
             'gasPrice': w3.toWei('1.046739556', 'gwei')
             })
        send_transaction(pool_name, harvest_tx)
    if pool_name == "FlexUSD":
        swap_assets("0x7b2B3C5308ab5b2a1d9a94d20D35CCDf61e05b72", "0x0000000000000000000000000000000000000000", amount)

def send_transaction(identifier, tx):
    # identifier is just a string to help the admin to identify the tx if it fails.
    # First, check is there enough BCH to pay the gas fee
    if not check_bch_balance(portfolio_address):
        import app.email as email
        email.send_email_to_admin("Not enough BCH to send a tx.")
        return
    import os
    tx['gas'] *= 1.5
    tx['gas'] = int(tx['gas']) # Decimals removed
    nonce = w3.eth.get_transaction_count(portfolio_address)
    tx['nonce'] = nonce
    private_key = os.environ.get('PORTFOLIO_PRIV_KEY')
    if private_key == None:
        import app.email as email
        email.send_email_to_admin("Portfolio private key not loaded on shell environment")
        return
    signed_txn = w3.eth.account.sign_transaction(tx, private_key=private_key)
    try:
        TXID = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    except exceptions.SolidityError as error:
        logger.info(f'TX reverted. Identifier is {identifier}, error: {error}')
        import app.email as email
        email.send_email_to_admin(f'TX reverted. Identifier is {identifier}, error: {error}')
    except Exception as e:
        logger.info(f'TX failed to sent, error is {e}. Identifier is {identifier}')
        import app.email as email
        email.send_email_to_admin(f'TX failed to sent, error is {e}. Identifier is {identifier}')
    else:
        logger.info(f'TXID {TXID} sent, identifier is {identifier}')
        try:
            receipt = w3.eth.wait_for_transaction_receipt(TXID)
            if receipt.status == 0:
                import app.email as email
                email.send_email_to_admin(f"Harvesting failed for {identifier}, TXID is {TXID}")
                logger.info(f'TXID {TXID} failed, identifier is {identifier}')
        except exceptions.TimeExhausted:
            logger.info(f'Failed to get TX status, TXID is {TXID}, identifier is {identifier}')
            import app.email as email
            email.send_email_to_admin(f'Failed to get TX status, TXID is {TXID}, identifier is {identifier}')
        except Exception as e:
            logger.info(f'Failed to get TX status, error is {e}, TXID is {TXID}, identifier is {identifier}')
            import app.email as email
            email.send_email_to_admin(f'Failed to get TX status, error is {e}, TXID is {TXID}, identifier is {identifier}')

def harvest_farms_rewards():
    # Harvest all the rewards for every farm
    for DEX in farms:
        ABI = open(f"ABIs/{farms[DEX]['factory_ABI']}", "r")
        abi = json.loads(ABI.read())
        contract = w3.eth.contract(address=farms[DEX]['factory'], abi=abi)
        for i in range(len(farms[DEX]['farms'])):
            harvest_tx = contract.functions.deposit(farms[DEX]['farms'][i]['pool_id'], 0).buildTransaction(
                {'chainId': 10000,
                 'from': portfolio_address,
                 'gasPrice': w3.toWei('1.046739556', 'gwei')
                 })
            send_transaction(farms[DEX]['farms'][i]["lp_CA"], harvest_tx)

def get_ETF_assets_allocation(farms):
    portfolio = {"Standalone assets": {}, "Farms": {}}
    total_percentage = 0
    total_value = 0
    for asset in pie_chart_data:
        portfolio["Standalone assets"][asset] = pie_chart_data[asset]
        total_value += portfolio["Standalone assets"][asset]
    for DEX in farms:
        portfolio["Farms"][DEX] = {}
        for i in range(len(farms[DEX]['farms'])):
            lp_CA = farms[DEX]['farms'][i]['lp_CA']
            portfolio["Farms"][DEX][lp_CA] = 0
            for coin in farms[DEX]['farms'][i]['Coins']:
                portfolio["Farms"][DEX][lp_CA] += farms[DEX]['farms'][i]['Coins'][coin]['Current value']
            total_value += portfolio["Farms"][DEX][lp_CA]
    #It's time to compute the allocation of each asset
    for asset in portfolio["Standalone assets"]:
        portfolio["Standalone assets"][asset] = (portfolio["Standalone assets"][asset] / total_value) * 100
        total_percentage += portfolio["Standalone assets"][asset]
    for DEX in portfolio["Farms"]:
        for lp_CA in portfolio["Farms"][DEX]:
            portfolio["Farms"][DEX][lp_CA] = (portfolio["Farms"][DEX][lp_CA] / total_value) * 100
            total_percentage += portfolio["Farms"][DEX][lp_CA]
    if total_percentage < 99.9 or total_percentage > 100.1:
        logger.info(f'Warning: total percentage of ETF portfolio is {total_percentage}')
        import app.email as email
        email.send_email_to_admin(f'Warning: total percentage of ETF portfolio is {total_percentage}')
    return portfolio

def swap_assets(asset_in, asset_out, amount):
    # asset_in and asset_out are the respective contract address of each token. Amount is the amount to swap.
    # First, we need to make sure that the portfolio holds the required amount of asset_in
    ABI = open("ABIs/ERC20-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=asset_in, abi=abi)
    asset_in_amount = contract.functions.balanceOf(portfolio_address).call()
    if asset_in_amount < amount:
        logger.info(f'Warning: not enough {asset_in} balance, needed {amount}.')
        import app.email as email
        email.send_email_to_admin(f'Warning: not enough {asset_in} balance, needed {amount}.')
        return
    # Second, we need to know if SmartSwap router is allowed to swap asset_in
    router = "0xEd2E356C00A555DDdd7663BDA822C6acB34Ce614"
    allowance = contract.functions.allowance(portfolio_address, router).call()
    if allowance == 0:
        amount = contract.functions.totalSupply().call()
        allowance_tx = contract.functions.approve(router, amount).buildTransaction(
            {'chainId': 10000,
             'from': portfolio_address,
             'gasPrice': w3.toWei('1.05', 'gwei')
             })
        send_transaction(f"Approving {asset_in} for SmartSwap router", allowance_tx)
    ABI = open("ABIs/SmartSwap-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=router, abi=abi)
    parts = 10 # Number of DEXs to used, set to 10 by default
    # Third, we'll get the expected return and DEXs distribution
    expected_return, distribution = contract.functions.getExpectedReturn(asset_in, asset_out, int(amount), parts, 0).call()
    # Last, we'll construct the swap TX
    deadline = round(time()) + 60  # Added 60 sec to the current time
    minAmount = int(expected_return * 0.975) #Slippage tolerance 2.5%
    swap_tx = contract.functions.swap(asset_in, asset_out, int(amount), minAmount, distribution, 0, deadline, 500000000000000).buildTransaction(
        {'chainId': 10000,
         'from': portfolio_address,
         'gasPrice': w3.toWei('1.05', 'gwei')
         })
    identifier = f"Swap {amount} {asset_in} for {asset_out}"
    send_transaction(identifier, swap_tx)


def main():
    global total_liquid_value
    global total_illiquid_value
    global total_rewards_value
    global SIDX_LP_value
    total_liquid_value = 0
    total_illiquid_value = 0
    SIDX_LP_value = 0
    bch_price = get_BCH_price()
    SIDX_stats = get_SIDX_stats(bch_price)
    sidx_price = float(SIDX_stats["Price"].split()[0])
    SEP20_tokens, stacked_assets = get_balances(bch_price)
    total_rewards_value = stacked_assets["Total yield value"]
    LP_balances = get_LP_balances(initial_pool_balances, portfolio_address, bch_price, sidx_price)
    extra_LP_balances = get_LP_balances(extra_pool_balances, punk_wallets[1], bch_price, sidx_price)
    get_law_rewards(bch_price)
    make_pie_chart()
    get_farms(bch_price)
    ETF_portfolio = get_ETF_assets_allocation(farms)
    global_portfolio_stats = {"total_liquid_value": round(total_liquid_value, 2),
                              "total_illiquid_value": round(total_illiquid_value, 2),
                              "total_portfolio_balance": round(total_liquid_value + total_illiquid_value, 2),
                              "total_rewards_value": round(total_rewards_value, 2), "value_per_sidx": round(
            round(total_liquid_value + total_illiquid_value, 2) / SIDX_stats["Total supply"], 2)}
    with open('data/SIDX_STATS.json', 'w') as file:
        json.dump(SIDX_stats, file, indent=4)
    with open('data/SEP20_BALANCES.json', 'w') as file:
        json.dump(SEP20_tokens, file, indent=4)
    with open('data/STACKED_ASSETS.json', 'w') as file:
        json.dump(stacked_assets, file, indent=4)
    with open('data/LP_BALANCES.json', 'w') as file:
        json.dump(LP_balances, file, indent=4)
    with open('data/EXTRA_LP_BALANCES.json', 'w') as file:
        json.dump(extra_LP_balances, file, indent=4)
    with open('data/PUNKS_BALANCES.json', 'w') as file:
        json.dump(punks_owned, file, indent=4)
    with open('data/FARMS.json', 'w') as file:
        json.dump(farms, file, indent=4)
    with open('data/GLOBAL_STATS.json', 'w') as file:
        json.dump(global_portfolio_stats, file, indent=4)
    with open('data/ETF_portfolio.json', 'w') as file:
        json.dump(ETF_portfolio, file, indent=4)

if __name__ == "__main__":
    main()
