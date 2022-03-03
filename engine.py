import json
from web3 import Web3
import requests
import matplotlib.pyplot as plt
import numpy as np
from time import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import FirefoxOptions

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
punk_wallets = [portfolio_address, #Punks wallet 1
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
                  "BAR_CA": "0xC41C680c60309d4646379eD62020c534eB67b6f4", "BCH pair": "0x674A71E69fe8D5cCff6fdcF9F1Fa4262Aa14b154", "Liquid": True},
    "Tango": {"Initial": 23897.252, "Stacked": True, "CA": "0x73BE9c8Edf5e951c9a0762EA2b1DE8c8F38B5e91",
                  "BAR_CA": "0x98Ff640323C059d8C4CB846976973FEEB0E068aA", "BCH pair": "0x4b773a2ea30C6A77564E4FaE60204e7Bc0a81A90", "Liquid": True},
    "FlexUSD": {"Initial": 2152.878, "Stacked": True, "CA": "0x7b2B3C5308ab5b2a1d9a94d20D35CCDf61e05b72", "BCH pair": "0x24f011f12Ea45AfaDb1D4245bA15dCAB38B43D13", "Liquid": True},
    "Green Ben": {"Initial": 2122.74, "Stacked": True, "CA": "0xDEa721EFe7cBC0fCAb7C8d65c598b21B6373A2b6", "Liquid": True},
    "Celery": {"Initial": 1674817.26, "Stacked": True, "CA": "0x7642Df81b5BEAeEb331cc5A104bd13Ba68c34B91", "BCH pair": "0x5775D98022590dc60E9c4Ae0a1c56bF1fD8fcaDC", "Liquid": False},
    "FLEX Coin": {"Initial": 142.804, "Stacked": True, "CA": "0x98Dd7eC28FB43b3C4c770AE532417015fa939Dd3", "Liquid": True},
    "LAW": {"Stacked": True, "CA": "0x0b00366fBF7037E9d75E4A569ab27dAB84759302", "BCH pair": "0xd55a9A41666108d10d31BAeEea5D6CdF3be6C5DD", "Liquid": True},
    "DAIQUIRI": {"Initial": 14281.791, "Stacked": True, "CA": "0xE4D74Af73114F72bD0172fc7904852Ee2E2b47B0", "BCH pair": "0xF1Ac59acb449C8e2BA9D222cA1275b3f4f9a455C", "Liquid": True}}

initial_pool_balances = {
    "Mistswap": {"CA": "0x7E1B9F1e286160A80ab9B04D228C02583AeF90B5", "token0": 5, "token1": 23711.1}
    # Token0 is WBCH, Token1 is SIDX
    }

extra_pool_balances = {"Mistswap": {"CA": "0x7E1B9F1e286160A80ab9B04D228C02583AeF90B5", "token0": 3.74556, "token1": 821.0572}}  # Token0 is WBCH, Token1 is SIDX


farms = {"Mistswap": {"factory": "0x3A7B9D0ed49a90712da4E087b17eE4Ac1375a5D4",
                      "factory_ABI": "MIST-Master-ABI.json",
                      "farms": [{"lp_CA": "0x4fF52e9D7824EC9b4e0189F11B5aA0F02b459b03",
                      "pool_id": 2,
                      "lp_token_amount": 344.686876049931219858 * 10 ** 18,
                      "initial_token0_amount": 882.588, #FlexUSD
                      "token_0_bch_pair": "0x24f011f12Ea45AfaDb1D4245bA15dCAB38B43D13",
                      "token_0_assets_position": (1,0),
                      "initial_token1_amount": 142.8045, #FLEX
                      "token_1_bch_pair": "0x8E647c88243A374E60eb644Afb13FfFd52278051",
                      "token_1_assets_position": (1,0),
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
                                 "reward coin": "MistToken"}
                                ]}
}

pie_chart_data = {}

def get_balances(ben_tokens, bch_price):
    stacked_assets = {}
    SEP20_tokens = {}
    total_value_SEP20_tokens = 0
    total_value_stacked_assets = 0
    total_value_yield = 0
    global total_liquid_value
    global total_illiquid_value
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
                pie_chart_data[asset] = SEP20_tokens[asset]["Current value"]
            elif "BCH pair" in assets_balances[asset]:
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
                stacked_assets[asset]["Initial"] = round((wallet_balance + contract.functions.getLastStakingBalance(portfolio_address).call()) / 10 ** decimals, 2)
                # Now, let's determine the amount available for collection
                last_processed_time = contract.functions.getLastProcessedTime(portfolio_address).call()
                delta = int(time()) - last_processed_time
                year_percentage = delta/31536000 #Seconds in a year
                payout_amount = round(stacked_assets[asset]["Initial"] * year_percentage, 2)
                stacked_assets[asset]["Current"] = round((stacked_assets[asset]["Initial"] + payout_amount), 2)
                stacked_assets[asset]["Yield"] = round(payout_amount, 2)
                stacked_assets[asset]["Mode"] = "Payout"
            else:
                last_processed_time = contract.functions.getLastProcessedTime(portfolio_address).call()
                delta = int(time()) - last_processed_time
                year_percentage = delta/31536000 #Seconds in a year
                account_balance = 2 ** year_percentage * contract.functions.getAccountBalance(portfolio_address).call()
                stacked_assets[asset] = {}
                stacked_assets[asset]["Initial"] = round(assets_balances[asset]["Initial"], 2)
                stacked_assets[asset]["Current"] = round(
                    (wallet_balance + account_balance) / 10 ** contract.functions.decimals().call(), 2)
                stacked_assets[asset]["Yield"] = round(stacked_assets[asset]["Current"] - stacked_assets[asset]["Initial"],
                                                       2)
                stacked_assets[asset]["Mode"] = "Stacking"
            if "BCH pair" in assets_balances[asset]:
                asset_price = get_price_from_pool(asset, bch_price)
                stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
                total_value_stacked_assets += stacked_assets[asset]["Current value"]
                stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
                pie_chart_data[asset] = stacked_assets[asset]["Current value"]
            elif asset in ben_tokens:
                asset_price = get_price(assets_balances[asset]["CA"])
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
            if asset in ben_tokens:
                asset_price = get_price(assets_balances[asset]["CA"])
                stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
                stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
                pie_chart_data[asset] = stacked_assets[asset]["Current value"]
                total_value_stacked_assets += stacked_assets[asset]["Current value"]
                total_value_yield += stacked_assets[asset]["Yield value"]
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
            elif asset in ben_tokens:
                asset_price = get_price(assets_balances[asset]["CA"])
                stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
                stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
                pie_chart_data[asset] = stacked_assets[asset]["Current value"]
                total_value_stacked_assets += stacked_assets[asset]["Current value"]
            total_liquid_value += stacked_assets[asset]["Current value"] + stacked_assets[asset]["Yield value"]
        if asset == "Tango":
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
            elif asset in ben_tokens:
                asset_price = get_price(assets_balances[asset]["CA"])
                stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
                stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
                pie_chart_data[asset] = stacked_assets[asset]["Current value"]
                total_value_stacked_assets += stacked_assets[asset]["Current value"]
                total_value_yield += stacked_assets[asset]["Yield value"]
            total_liquid_value += stacked_assets[asset]["Current value"] + stacked_assets[asset]["Yield value"]
        if asset == "1BCH":
            ABI = open("ABIs/PCK-Master-ABI.json", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=assets_balances[asset]["CA"], abi=abi)
            assets_balances[asset]["Yield"] = contract.functions.userInfo(0, portfolio_address).call()[1] / 10 ** 18
            assets_balances[asset]["Current"] = assets_balances[asset]["Initial"] + assets_balances[asset]["Yield"]
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
        if asset == "BCHPAD":
            asset_price = get_price_from_pool(asset, bch_price, assets_positions=(1,0))
            ABI = open("ABIs/BPADStaking-ABI.json", "r")  # ABI for BPAD stacking
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=assets_balances[asset]["CA"], abi=abi)
            stacked_assets[asset] = {}
            stacked_assets[asset]["Initial"] = round(assets_balances[asset]["Initial"], 2)
            stacked_assets[asset]["Current"] = round((contract.functions.balanceOf(portfolio_address).call() + contract.functions.earned(portfolio_address).call()) / 10 ** 18,2)
            stacked_assets[asset]["Yield"] = round(stacked_assets[asset]["Current"] - stacked_assets[asset]["Initial"],
                                                   2)
            stacked_assets[asset]["Current value"] = round(stacked_assets[asset]["Current"] * asset_price, 2)
            stacked_assets[asset]["Yield value"] = round(stacked_assets[asset]["Yield"] * asset_price, 2)
            pie_chart_data[asset] = stacked_assets[asset]["Current value"]
            total_value_stacked_assets += stacked_assets[asset]["Current value"]
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
    price = get_price_from_pool("0x7E1B9F1e286160A80ab9B04D228C02583AeF90B5", bch_price, assets_positions=(1,0)) #(Asset and BCH position on LP)
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
    #Modified for Mistswap farm
    LP_balances = {}
    for DEX in initial_pool_balances:
        LP_balances[DEX] = {}
        #First, get current LP balance and rewards
        ABI = open("ABIs/MIST-Master-ABI.json", 'r')
        abi = json.loads(ABI.read())
        contract = w3.eth.contract(address="0x3A7B9D0ed49a90712da4E087b17eE4Ac1375a5D4", abi=abi)
        pool_id = 44
        portfolio_LP_balance = contract.functions.userInfo(pool_id, wallet_address).call()[0]
        reward = contract.functions.pendingSushi(pool_id, wallet_address).call()
        asset_price = get_price_from_pool("MistToken", bch_price)
        #Get assets in liquidity pools
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
        LP_balances[DEX][token0_ticker]["Current value"] = round(LP_balances[DEX][token0_ticker]["Current"] * bch_price, 2)
        total_liquid_value += LP_balances[DEX][token0_ticker]["Current value"]
        LP_balances[DEX][token1_ticker]["Current"] = round(
            ((portfolio_LP_balance / LP_total_supply) * token1_reserves) / 10 ** token1_decimals, 2)
        LP_balances[DEX][token1_ticker]["Current value"] = round(LP_balances[DEX][token1_ticker]["Current"] * sidx_price, 2)
        total_liquid_value += LP_balances[DEX][token1_ticker]["Current value"]
        LP_balances[DEX][token0_ticker]["Difference"] = round(
            LP_balances[DEX][token0_ticker]["Current"] - LP_balances[DEX][token0_ticker]["Initial"], 2)
        LP_balances[DEX][token1_ticker]["Difference"] = round(LP_balances[DEX][token1_ticker]["Current"] - \
                                                              LP_balances[DEX][token1_ticker]["Initial"], 2)
        LP_balances[DEX]["Reward"] = round(reward/10**18, 2)
        LP_balances[DEX]["Reward value"] = round(LP_balances[DEX]["Reward"] * asset_price, 2)
        total_liquid_value += LP_balances[DEX]["Reward value"]
        total_rewards_value += LP_balances[DEX]["Reward value"]
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

def get_price_from_pool(asset, BCH_price, assets_positions=(0,1)):
    # assets_positions is a tuple with the format (asset_positions, BCH_position) used when passing BCH pair address
    asset_position, BCH_position = assets_positions
    ABI = open("ABIs/UniswapV2Pair.json", "r")  # Standard ABI for LP tokens
    abi = json.loads(ABI.read())
    if asset in assets_balances:
        contract = w3.eth.contract(address=assets_balances[asset]["BCH pair"], abi=abi)
        if contract.functions.token1().call() == assets_balances[asset]["CA"]:
            asset_position = 1
            BCH_position = 0
    else: #Directly pass BCH pair address
        contract = w3.eth.contract(address=asset, abi=abi)
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
    #Now get punk's floor price using selenium library
    url = "https://blockng.money/#/punks"
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    driver = webdriver.Firefox(options=opts)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    status = wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, "punks-market-info-item-num.BCH"), "."))
    element = driver.find_element(By.CLASS_NAME, 'punks-market-info-item-num.BCH')
    floor_price = float(element.text.split()[0])
    driver.quit()
    punks_owned["Floor price"] = floor_price # In BCH
    punks_owned["Total floor value"] = round(floor_price * punks_number * bch_price, 2) # In USD
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
            farms[DEX]["farms"][i]["Coins"][token0_ticker] = {"Initial amount": round(farms[DEX]["farms"][i]["initial_token0_amount"], 2)}
            farms[DEX]["farms"][i]["Coins"][token1_ticker] = {"Initial amount": round(farms[DEX]["farms"][i]["initial_token1_amount"], 2)}
            farms[DEX]["farms"][i]["Coins"][token0_ticker]["Current"] = round(
                ((farms[DEX]["farms"][i]["lp_token_amount"] / LP_total_supply) * token0_reserves) / 10 ** token0_decimals, 2)
            farms[DEX]["farms"][i]["Coins"][token0_ticker]["Current value"] = round(get_price_from_pool(farms[DEX]["farms"][i]["token_0_bch_pair"], bch_price, assets_positions=farms[DEX]["farms"][i]["token_0_assets_position"]) * farms[DEX]["farms"][i]["Coins"][token0_ticker]["Current"], 2)
            total_liquid_value += farms[DEX]["farms"][i]["Coins"][token0_ticker]["Current value"]
            farms[DEX]["farms"][i]["Coins"][token1_ticker]["Current"] = round(
                ((farms[DEX]["farms"][i]["lp_token_amount"] / LP_total_supply) * token1_reserves) / 10 ** token1_decimals, 2)
            farms[DEX]["farms"][i]["Coins"][token1_ticker]["Current value"] = round(get_price_from_pool(farms[DEX]["farms"][i]["token_1_bch_pair"], bch_price, assets_positions=farms[DEX]["farms"][i]["token_1_assets_position"]) * farms[DEX]["farms"][i]["Coins"][token1_ticker]["Current"], 2)
            total_liquid_value += farms[DEX]["farms"][i]["Coins"][token1_ticker]["Current value"]
            farms[DEX]["farms"][i]["Coins"][token0_ticker]["Difference"] = round(
                farms[DEX]["farms"][i]["Coins"][token0_ticker]["Current"] - farms[DEX]["farms"][i]["Coins"][token0_ticker]["Initial amount"], 2)
            farms[DEX]["farms"][i]["Coins"][token1_ticker]["Difference"] = round(farms[DEX]["farms"][i]["Coins"][token1_ticker]["Current"] - \
                                                                  farms[DEX]["farms"][i]["Coins"][token1_ticker]["Initial amount"], 2)
            #Now, it's time to get the rewards
            ABI_path = "ABIs/" + farms[DEX]["factory_ABI"]
            ABI = open(ABI_path, "r")  # Factory contract ABI
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=farms[DEX]["factory"], abi=abi)
            reward = contract.functions.pendingSushi(farms[DEX]["farms"][i]["pool_id"], portfolio_address).call()
            farms[DEX]["farms"][i]["reward"] = round((reward / 10 ** 18), 2)
            if farms[DEX]["farms"][i]["reward coin"] in assets_balances:
                asset_price = get_price_from_pool(farms[DEX]["farms"][i]["reward coin"], bch_price)
                farms[DEX]["farms"][i]["reward value"] = round((farms[DEX]["farms"][i]["reward"] * asset_price), 2)
                total_liquid_value += farms[DEX]["farms"][i]["reward value"]
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
    import os
    ABI = open("ABIs/CLY-ABI.json", "r")  # ABI for CLY token
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address="0x7642Df81b5BEAeEb331cc5A104bd13Ba68c34B91", abi=abi)
    nonce = w3.eth.get_transaction_count(portfolio_address)
    stake_cly_tx = contract.functions.startStake().buildTransaction(
        {'chainId': 10000,
         'gas': 108287,
         'gasPrice': w3.toWei('1.05', 'gwei'),
         'nonce': nonce})
    private_key = os.environ.get('PORTFOLIO_PRIV_KEY')
    if private_key == None:
        import app.email as email
        email.send_email_to_admin("Portfolio private key not loaded on shell environment")
    signed_txn = w3.eth.account.sign_transaction(stake_cly_tx, private_key=private_key)
    w3.eth.send_raw_transaction(signed_txn.rawTransaction)

def start_celery_payout():
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

def main():
    global total_liquid_value
    global total_illiquid_value
    global total_rewards_value
    total_liquid_value = 0
    total_illiquid_value = 0
    bch_price = get_BCH_price()
    SIDX_stats = get_SIDX_stats(bch_price)
    sidx_price = float(SIDX_stats["Price"].split()[0])
    ben_tokens = ben_listed_tokens()
    SEP20_tokens, stacked_assets = get_balances(ben_tokens, bch_price)
    total_rewards_value = stacked_assets["Total yield value"]
    LP_balances = get_LP_balances(initial_pool_balances, portfolio_address, bch_price, sidx_price)
    extra_LP_balances = get_LP_balances(extra_pool_balances, punk_wallets[1], bch_price, sidx_price)
    get_law_rewards(bch_price)
    make_pie_chart()
    get_farms(bch_price)
    global_portfolio_stats = {"total_liquid_value": round(total_liquid_value, 2), "total_illiquid_value": round(total_illiquid_value, 2), "total_portfolio_balance": round(total_liquid_value + total_illiquid_value, 2), "total_rewards_value": round(total_rewards_value, 2)}
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

if __name__ == "__main__":
    main()
