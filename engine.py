import json
from web3 import Web3, exceptions
import requests
from time import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import FirefoxOptions
from datetime import datetime
import logging
import math


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
law_salary = "0xe0ACACCFf2cDa66C8cFcA3bf86e7310748c70727"
law_rights = {"453": {}, "457": {}, "459": {}, "460": {}} # TokenID: {LAW locked, salary}
punk_wallets = [portfolio_address,  # Punks wallet 1
                "0x3484f575A3d3b4026B4708997317797925A236ae",  # Punks wallet 2
                "0x57BB80fdab3ca9FDBC690F4b133010d8615e77b3"]  # Punks wallet 3

WBCH_CA = "0x3743eC0673453E5009310C727Ba4eaF7b3a1cc04"

with open("data/NFTs.json", "r") as file:
    NFTs = json.load(file)
with open("data/ETF_FARMS.json", "r") as file:
    ETF_farms = json.load(file)

ETF_portfolio_address = "0x91fbdB995D05BBdCb3C7D21180794877A93d87e0"

assets_balances = {
    "MistToken": {"Initial": 226146.43, "Stacked": True, "CA": "0x5fA664f69c2A4A3ec94FaC3cBf7049BD9CA73129",
                  "BAR_CA": "0xC41C680c60309d4646379eD62020c534eB67b6f4",
                  "BCH pair": "0x674A71E69fe8D5cCff6fdcF9F1Fa4262Aa14b154", "Liquid": True,
                  "harvest_ABI": "SushiBar.json"},
    "Tango": {"Initial": 23897.252, "Stacked": True, "CA": "0x73BE9c8Edf5e951c9a0762EA2b1DE8c8F38B5e91",
              "BAR_CA": "0x98Ff640323C059d8C4CB846976973FEEB0E068aA",
              "BCH pair": "0x4b773a2ea30C6A77564E4FaE60204e7Bc0a81A90", "Liquid": True},
    "Green Ben": {"Initial": 1875.168, "Stacked": True, "CA": "0xDEa721EFe7cBC0fCAb7C8d65c598b21B6373A2b6",
                  "Liquid": True, "BCH pair": "0x0D4372aCc0503Fbcc7EB129e0De3283c348B82c3", "harvest_CA": "0xDEa721EFe7cBC0fCAb7C8d65c598b21B6373A2b6", "harvest_pool_id": 1,
                  "harvest_ABI": "BEN-Master-ABI.json"},
    "Celery": {"Initial": 1674817.26, "Stacked": True, "CA": "0x7642Df81b5BEAeEb331cc5A104bd13Ba68c34B91",
               "BCH pair": "0x5775D98022590dc60E9c4Ae0a1c56bF1fD8fcaDC", "Liquid": False},
    "FLEX Coin": {"Initial": 142.804, "Stacked": False, "CA": "0x98Dd7eC28FB43b3C4c770AE532417015fa939Dd3",
                  "Liquid": True, "BCH pair": "0x1A2bdFF5bA942bF20f0db7218cdE28D19aC8dD20"},
    "LNS": {"Initial": 44.9947, "Stacked": True, "CA": "0x35b3Ee79E1A7775cE0c11Bd8cd416630E07B0d6f",
            "BAR_CA": "0xBE7E034c86AC2a302f69ef3975e3D14820cC7660",
            "BCH pair": "0x7f3F57C92681c9a132660c468f9cdff456fC3Fd7", "Liquid": True, "harvest_ABI": "SushiBar.json"},
    "GOB": {"Initial": 5.524333, "Stacked": True, "CA": "0x56381cB87C8990971f3e9d948939e1a95eA113a3",
            "BCH pair": "0x86B0fD64234a747681f0235B6Cc5FE04a4D95B31", "Liquid": True,
            "harvest_CA": "0x48B8aCe692ad8BD2E3139C65bFf7d28c048F8f00", "harvest_ABI": "GOB-StakingContract.json"},
    "BCH": {"Stacked": True, "Liquid": True}, # Staked set to true as BCH hold by now is just for fees
    "bcUSDT": {"Stacked": False, "Liquid": True, "CA": "0xBc2F884680c95A02cea099dA2F524b366d9028Ba", "BCH pair": "0x27580618797a2CE02FDFBbee948388a50a823611"},
    "LAW": {"Stacked": True, "Liquid": True, "CA": "0x0b00366fBF7037E9d75E4A569ab27dAB84759302", "BCH pair": "0x54AA3B2250A0e1f9852b4a489Fe1C20e7C71fd88"},
    "Joy": {"Stacked": False, "Liquid": True, "CA": "0x6732E55Ac3ECa734F54C26Bd8DF4eED52Fb79a6E", "BCH pair": "0xEe08584956020Ea9D4211A239030ad49Eb5f886D"},
    "FlexUSD": {"Stacked": False, "Liquid": True, "CA": "0x7b2B3C5308ab5b2a1d9a94d20D35CCDf61e05b72", "BCH pair": "0x24f011f12Ea45AfaDb1D4245bA15dCAB38B43D13"}
}

initial_pool_balances = {
    "Mistswap": {"CA": "0x7E1B9F1e286160A80ab9B04D228C02583AeF90B5", "token0": 3.333, "token1": 15807.4},
    "BlockNG": {"CA": "0x1CD36D9dEd958366d17DfEdD91b5F8e682D7f914", "token0": 2223, "token1": 3049.02}
    # Token0 is WBCH/LAW, Token1 is SIDX
}

extra_pool_balances = {
    "Mistswap": {"CA": "0x7E1B9F1e286160A80ab9B04D228C02583AeF90B5", "token0": 5.0781, "token1": 2240.11},
    "Tangoswap": {"CA": "0x4509Ff66a56cB1b80a6184DB268AD9dFBB79DD53", "token0": 4.6109, "token1": 1681.21},
    "Emberswap": {"CA": "0x97dEAeB1A9A762d97Ac565cD3Ff7629CD6d55D09", "token0": 216629, "token1": 650.63}
    }  # Token0 is WBCH/EMBER, Token1 is SIDX

farms = {"Mistswap": {"factory": "0x3A7B9D0ed49a90712da4E087b17eE4Ac1375a5D4",
                      "factory_ABI": "MIST-Master-ABI.json",
                      "farms": [{"lp_CA": "0xde5D57B31cB67d5Aed93c26940394796953961cb",
                                 "pool_id": 60,
                                 "lp_token_amount": 1322867557150664581,
                                 "initial_token0_amount": 1.419,  # WBCH
                                 "token_0_bch_pair": "0x3743eC0673453E5009310C727Ba4eaF7b3a1cc04", #Get price from pool will just return BCH price
                                 "token_0_assets_position": (0, 1),
                                 "initial_token1_amount": 1.405,  # bcBCH
                                 "token_1_bch_pair": "0xde5D57B31cB67d5Aed93c26940394796953961cb",
                                 "token_1_assets_position": (1, 0),
                                 "reward coin": "MistToken"},
                                ]},
        "Tangoswap": {"factory": "0x38cC060DF3a0498e978eB756e44BD43CC4958aD9",
                      "factory_ABI": "MIST-Master-ABI.json",
                      "farms": [{"lp_CA": "0xC849ccDA62Af9f638B849f6116e3B0c9A17a637c",
                                 "pool_id": 37,
                                 "lp_token_amount": 20.04828 * 10 ** 18,
                                 "initial_token0_amount": 10913.8, #TANGO
                                 "token_0_bch_pair": "0x4b773a2ea30C6A77564E4FaE60204e7Bc0a81A90",
                                 "token_0_assets_position": (1, 0),
                                 "initial_token1_amount": 0.0369945, #bcETH
                                 "token_1_bch_pair": "0xE8Dd3C0E136Ed71A00b104C21656aE5a642D3369",
                                 "token_1_assets_position": (1, 0),
                                 "reward coin": "Tango"}]
         },
         "BlockNG-Kudos": {"farms": [{"lp_CA": "0x6239142dB6980e2663d49F67E99B1625Ee0A9c54",
                                      "lp_token_amount": 3.024777 * 10 ** 18,
                                      "initial_token0_amount": 98.7302,  #LAW
                                      "token_0_bch_pair": "0x54AA3B2250A0e1f9852b4a489Fe1C20e7C71fd88",
                                      "token_0_assets_position": (0, 1),
                                      "initial_token1_amount": 0.09596, #bcBNB
                                      "token_1_bch_pair": "0x7Cf25179b4968dd7Da5A2f35689361f6555C76b6",
                                      "token_1_assets_position": (1, 0),
                                      "reward coin": "LAW",
                                      "CA": "0xB571042A440838e2D794ce54992D7b6c4cFFAfE1"},
                                    {"lp_CA": "0x58B006A8380Cc4807b1d58C5a339A0E6f2338F1A",
                                      "lp_token_amount": 191.8265 * 10 ** 18,
                                      "initial_token0_amount": 355.715,  #LAW
                                      "token_0_bch_pair": "0x54AA3B2250A0e1f9852b4a489Fe1C20e7C71fd88",
                                      "token_0_assets_position": (0, 1),
                                      "initial_token1_amount": 109.112, #LawUSD
                                      "token_1_bch_pair": "0xFEdfE67b179b2247053797d3b49d167a845a933e",
                                      "token_1_assets_position": (1, 0),
                                      "reward coin": "LAW",
                                      "CA": "0x44E64014BDAFbcb4542Ed9fE8Dfcf4320071B192"}
                                     ]},
         "BlockNG-Beam": {"farms": [{"lp_CA": "0xB82FF56E3E91c102a5dAf9Aa31BaE4c8c63F53A5",
                                      "lp_token_amount": 2.49976779 * 10 ** 18,
                                      "initial_token0_amount": 0.218,  #bcBCH
                                      "token_0_bch_pair": "0xde5D57B31cB67d5Aed93c26940394796953961cb",
                                      "token_0_assets_position": (0, 1),
                                      "initial_token1_amount": 30.43, #LawUSD
                                      "token_1_bch_pair": "0xFEdfE67b179b2247053797d3b49d167a845a933e",
                                      "token_1_assets_position": (1, 0),
                                      "reward coin": "LAW",
                                      "CA": "0x5a6b3a1B16794D492Fa9B72092C94468ae74901D"},
                                    {"lp_CA": "0x43205613aD09aeF94fE0396F34c2C93eBc6D1b7E",
                                     "lp_token_amount": 28.2342 * 10 ** 18,
                                     "initial_token0_amount": 28.29,  # bcUSDT
                                     "token_0_bch_pair": "0x27580618797a2CE02FDFBbee948388a50a823611",
                                     "token_0_assets_position": (1, 0),
                                     "initial_token1_amount": 30.21,  # LawUSD
                                     "token_1_bch_pair": "0xFEdfE67b179b2247053797d3b49d167a845a933e",
                                     "token_1_assets_position": (1, 0),
                                     "reward coin": "LAW",
                                     "CA": "0xAfAca05002412b6200B2e24e3044E63713c9bcD3"}
                                    ]}
}

pie_chart_data = {}
farms_pie_chart_data = {}
sidx_liquidity_pie_chart_data = {}
global_stats_pie_chart_data = {}


def get_balances(bch_price, portfolio_address=portfolio_address):
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
        else:
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
    global_stats_pie_chart_data["Liquid Assets"] = total_liquid_value
    global_stats_pie_chart_data["Illiquid Assets"] = total_illiquid_value
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
    total_supply = round(contract.functions.totalSupply().call() / 10 ** 18, 3)
    SIDX_stats["Total supply"] = total_supply
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
        liquid_value = 0
        if DEX not in sidx_liquidity_pie_chart_data:
            sidx_liquidity_pie_chart_data[DEX] = 0
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
        if DEX == "Emberswap":
            ABI = open("ABIs/EMBER_Distributor-ABI.json", 'r')
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address="0x8ecb32C33AB3f7ee3D6Ce9D4020bC53fecB36Be9", abi=abi)
            pool_id = 31
            portfolio_LP_balance = contract.functions.userInfo(pool_id, wallet_address).call()[0]
            reward = contract.functions.pendingTokens(pool_id, wallet_address).call()[3][0]
            asset_price = get_price_from_pool("0x52c656FaF57DCbDdDd47BCbA7b2ab79e4c232C28", bch_price, assets_positions=(1, 0))
        if DEX == "BlockNG":
            ABI = open("ABIs/BlockNG-farm.json", 'r')
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address="0x3384d970688f7B86a8D7aE6D8670CD5f9fd5fE1E", abi=abi)
            portfolio_LP_balance = contract.functions.balanceOf(wallet_address).call()
            contract = w3.eth.contract(address="0xdB8Fc051ec6956f1c8D018F033E6788f959313d1", abi=abi)
            reward = contract.caller().gaugeStakedDetailNonView("0x3384d970688f7B86a8D7aE6D8670CD5f9fd5fE1E", wallet_address, assets_balances["LAW"]["CA"])[5]
            asset_price = get_price_from_pool("LAW", bch_price)
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
        if DEX == "Emberswap" or DEX == "BlockNG":
            LP_balances[DEX][token0_ticker]["Current value"] = round(LP_balances[DEX][token0_ticker]["Current"] * asset_price,
                                                                     2)
        else:
            LP_balances[DEX][token0_ticker]["Current value"] = round(LP_balances[DEX][token0_ticker]["Current"] * bch_price,
                                                                     2)
        total_liquid_value += LP_balances[DEX][token0_ticker]["Current value"]
        liquid_value += LP_balances[DEX][token0_ticker]["Current value"]
        SIDX_LP_value += LP_balances[DEX][token0_ticker]["Current value"]
        LP_balances[DEX][token1_ticker]["Current"] = round(
            ((portfolio_LP_balance / LP_total_supply) * token1_reserves) / 10 ** token1_decimals, 2)
        LP_balances[DEX][token1_ticker]["Current value"] = round(
            LP_balances[DEX][token1_ticker]["Current"] * sidx_price, 2)
        total_liquid_value += LP_balances[DEX][token1_ticker]["Current value"]
        liquid_value += LP_balances[DEX][token1_ticker]["Current value"]
        SIDX_LP_value += LP_balances[DEX][token1_ticker]["Current value"]
        sidx_liquidity_pie_chart_data[DEX] += LP_balances[DEX][token0_ticker]["Current value"]
        sidx_liquidity_pie_chart_data[DEX] += LP_balances[DEX][token1_ticker]["Current value"]
        LP_balances[DEX][token0_ticker]["Difference"] = round(
            LP_balances[DEX][token0_ticker]["Current"] - LP_balances[DEX][token0_ticker]["Initial"], 2)
        LP_balances[DEX][token1_ticker]["Difference"] = round(LP_balances[DEX][token1_ticker]["Current"] - \
                                                              LP_balances[DEX][token1_ticker]["Initial"], 2)
        LP_balances[DEX]["Total LP Value"] =  round(liquid_value, 2)
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
        punks_balance["Wallets"][wallet] = {"Punks": {}, "LAW rewards": 0}
    # As all punks in SmartIndex are staked, we need to scan the full punks supply in the punks DEX
    ABI = open("ABIs/LAW_punks_DEX-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=law_punks_market, abi=abi)
    # Get punks owned by SmartIndex by wallet
    for i in range(1, 10000):
        owner = contract.functions.getPunkSound(i).call()[0]
        print(i)
        if owner in punk_wallets:
            punks_balance["Wallets"][owner]["Punks"][i] = {}
    with open("data/NFTs.json", "w") as file:
        json.dump(punks_balance, file, indent=4)
    main()


def get_law_rewards(bch_price):
    global total_liquid_value
    global total_illiquid_value
    global total_rewards_value
    # First, let's get Punks rewards
    law_pending = 0
    punks_number = 0
    for wallet in NFTs["PUNKS"]["Wallets"]:
        ABI = open("ABIs/LAW_rewards-ABI.json", "r")
        abi = json.loads(ABI.read())
        contract = w3.eth.contract(address=law_rewards, abi=abi)
        pending_reward = contract.functions.earned(wallet).call() / 10 ** 18
        NFTs["PUNKS"]["Wallets"][wallet]["LAW rewards"] = round(pending_reward, 2)
        law_pending += pending_reward
        for punk in NFTs["PUNKS"]["Wallets"][wallet]["Punks"]:
            punks_number += 1
            # Punk stats
            ABI = open("ABIs/LAW_punks_level-ABI.json", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=law_level_address, abi=abi)
            stats = contract.functions.tokensOfMetaByIds([int(punk)]).call()[0]
            NFTs["PUNKS"]["Wallets"][wallet]["Punks"][punk] = {"Level": stats[1], "Bloodline": stats[2] / 10 ** 8, "Popularity": stats[3] / 10 ** 8, "Growth": stats[4] / 10 ** 8, "Power": stats[5] / 10 ** 8, "Hashrate": math.sqrt(stats[5] / 10 ** 8)};
    NFTs["PUNKS"]["Total LAW pending"] = round(law_pending, 2)
    law_price = get_price_from_pool("LAW", bch_price)
    NFTs["PUNKS"]["LAW pending in USD"] = round(NFTs["PUNKS"]["Total LAW pending"] * law_price, 2)
    total_liquid_value += NFTs["PUNKS"]["LAW pending in USD"]
    total_rewards_value += NFTs["PUNKS"]["LAW pending in USD"]
    # Now get punk's floor price using selenium library
    url = "https://blockng.money/#/punks"
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    driver = webdriver.Firefox(options=opts)
    driver.get(url)
    wait = WebDriverWait(driver, 15)
    try:
        status = wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, "punks-market-info-item-num.BCH"), "."))
        element = driver.find_element(By.CLASS_NAME, 'punks-market-info-item-num.BCH')
        floor_price = float(element.text.split()[0])
        NFTs["PUNKS"]["Floor price"] = floor_price  # In BCH
        NFTs["PUNKS"]["Total floor value"] = round(floor_price * punks_number * bch_price, 2)  # In USD
        total_illiquid_value += NFTs["PUNKS"]["Total floor value"]
    except Exception as e:
        element = driver.find_element(By.CLASS_NAME, 'punks-market-info-item-num.BCH')
        if element.text.split()[0].isnumeric():
            floor_price = float(element.text.split()[0])
            NFTs["PUNKS"]["Floor price"] = floor_price  # In BCH
            NFTs["PUNKS"]["Total floor value"] = round(floor_price * punks_number * bch_price, 2)  # In USD
            total_illiquid_value += NFTs["PUNKS"]["Total floor value"]
        else:
            logger.info(f'Error found trying to get punks floor price: {e}')
            import app.email as email
            email.send_email_to_admin(f'Error found trying to get punks floor price: {e}')
            total_illiquid_value += NFTs["PUNKS"]["Total floor value"]
    finally:
        driver.quit()
    # Next step is to get LAW locked in LawRights and salaries
    NFTs["LAW Rights"]["tokens"] = law_rights
    law_pending = 0
    law_locked = 0
    vote_power = 0
    veLAWRights_ABI = open("ABIs/veLawRightsProxyed.json", "r")
    veLAWRights_abi = json.loads(veLAWRights_ABI.read())
    LAW_rights_contract = w3.eth.contract(address="0xe24Ed1C92feab3Bb87cE7c97Df030f83E28d9667", abi=veLAWRights_abi)
    LAW_rewards_ABI = open("ABIs/LAW_rewards-ABI.json", "r")
    LAW_rewards_abi = json.loads(LAW_rewards_ABI.read())
    salary_contract = w3.eth.contract(address=law_salary, abi=LAW_rewards_abi)
    current_block = w3.eth.get_block_number()
    for tokenID in NFTs["LAW Rights"]["tokens"]:
        NFTs["LAW Rights"]["tokens"][tokenID]["LAW"] = round(LAW_rights_contract.functions.locked(int(tokenID)).call()[3] / 10 ** 18, 2)
        # get the end date of LawRight in seconds and convert to datetime then format to string
        NFTs["LAW Rights"]["tokens"][tokenID]["Unlock Date"] = str(datetime.fromtimestamp(LAW_rights_contract.functions.locked(int(tokenID)).call()[4]).strftime('%b %d, %Y'))
        NFTs["LAW Rights"]["tokens"][tokenID]["Vote Power"] = round(LAW_rights_contract.functions.balanceOfAtNFT(int(tokenID), current_block).call() / 10 ** 18, 2)
        pending_reward = salary_contract.functions.claimable(int(tokenID)).call() / 10 ** 18
        NFTs["LAW Rights"]["tokens"][tokenID]["LAW rewards"] = round(pending_reward, 2)
        vote_power += NFTs["LAW Rights"]["tokens"][tokenID]["Vote Power"]
        law_pending += NFTs["LAW Rights"]["tokens"][tokenID]["LAW rewards"]
        law_locked += NFTs["LAW Rights"]["tokens"][tokenID]["LAW"]
    NFTs["LAW Rights"]["Total LAW pending"] = round(law_pending, 2)
    NFTs["LAW Rights"]["Total Vote Power"] = round(vote_power, 2)
    law_price = get_price_from_pool("LAW", bch_price)
    NFTs["LAW Rights"]["LAW pending in USD"] = round(NFTs["LAW Rights"]["Total LAW pending"] * law_price, 2)
    NFTs["LAW Rights"]["Total LAW locked"] = round(law_locked, 2)
    NFTs["LAW Rights"]["LAW locked in USD"] = round(NFTs["LAW Rights"]["Total LAW locked"] * law_price, 2)
    total_liquid_value += NFTs["LAW Rights"]["LAW pending in USD"]
    total_rewards_value += NFTs["LAW Rights"]["LAW pending in USD"]
    total_illiquid_value += NFTs["LAW Rights"]["LAW locked in USD"]

def get_farms(bch_price, farms=farms):
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
            farm_name = f"{DEX}-{token0_ticker}-{token1_ticker}"
            total_USD_value = farms[DEX]["farms"][i]["Coins"][token0_ticker]["Current value"] + \
                              farms[DEX]["farms"][i]["Coins"][token1_ticker]["Current value"]
            farms[DEX]["farms"][i]["Total LP Value"] = round(total_USD_value, 2)
            farms_pie_chart_data[farm_name] = total_USD_value
            # Now, it's time to get the rewards
            if DEX == "BlockNG-Kudos":
                ABI = open("ABIs/BlockNG-farm.json", 'r')
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address="0xdB8Fc051ec6956f1c8D018F033E6788f959313d1", abi=abi)
                reward = contract.caller().gaugeStakedDetailNonView(farms[DEX]["farms"][i]["CA"], portfolio_address, assets_balances["LAW"]["CA"])[5]
                farms[DEX]["farms"][i]["reward"] = round((reward / 10 ** 18), 2)
            elif DEX == "BlockNG-Beam":
                ABI = open("ABIs/BlockNG-Beam-farm.json", 'r')
                abi = json.loads(ABI.read())
                contract = w3.eth.contract(address=farms[DEX]["farms"][i]["CA"], abi=abi)
                reward = contract.functions.earned(portfolio_address).call() #earnedEasily for LAW earned using referral codes
                farms[DEX]["farms"][i]["reward"] = round((reward / 10 ** 18), 2)
            else:
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

def make_pie_chart(data, chart_name):
    import matplotlib.pyplot as plt

    labels = []
    percentages = []
    total_USD_value = 0

    # Get accumulated USD value
    for asset in data:
        total_USD_value += data[asset]

    # Get list of percentages

    for asset in data:
        # Temporarily shortening the labels, should probably look into shortening further back, like MLP-BCH/bcBCH
        #   and BNG-K-LawUSD/Law, etc. Maybe settingup enums would be a valid choice?
        truncate = asset
        if len(truncate) > 15:
            truncate = truncate[:12]+"..."
        labels.append(truncate)
        percentages.append((data[asset]/total_USD_value) * 100)

    fig1, ax1 = plt.subplots()
    plt.rcParams.update({'font.size': 8})
    ax1.pie(percentages, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()
    plt.savefig(f"app/static/{chart_name}.png", transparent=True)

def start_celery_stake():
    if not check_bch_balance(portfolio_address):
        import app.email as email
        email.send_email_to_admin("Not enough BCH to start CLY stake")
        return
    ABI = open("ABIs/CLY-ABI.json", "r")  # ABI for CLY token
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address="0x7642Df81b5BEAeEb331cc5A104bd13Ba68c34B91", abi=abi)
    stake_cly_tx = contract.functions.startStake().buildTransaction(
        {'chainId': 10000,
         'from': portfolio_address,
         'gasPrice': w3.toWei('1.05', 'gwei')
        })
    send_transaction("Celery stacking", stake_cly_tx)


def start_celery_payout():
    ABI = open("ABIs/CLY-ABI.json", "r")  # ABI for CLY token
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address="0x7642Df81b5BEAeEb331cc5A104bd13Ba68c34B91", abi=abi)
    payout_cly_tx = contract.functions.startPayout().buildTransaction(
        {'chainId': 10000,
         'from': portfolio_address,
         'gasPrice': w3.toWei('1.05', 'gwei')
         })
    send_transaction("Celery payout", payout_cly_tx)


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


def check_bch_balance(account, tx=None):
    bch_balance = w3.eth.get_balance(account)
    if tx != None:
        fee = tx['gas'] * tx['gasPrice']
        if bch_balance >= fee:
            return True
        else:
            return False
    else:
        if bch_balance > 200000000000000:
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
             'gasPrice': w3.toWei('1.05', 'gwei')
             })
        send_transaction(pool_name, harvest_tx)
        if pool_name == "Green Ben":
            try:
                swap_assets("0x77CB87b57F54667978Eb1B199b28a0db8C8E1c0B", "0x0000000000000000000000000000000000000000",
                            "all")
            except Exception as e:
                logger.error(f'Failed to swap EBEN rewards to BCH. Exception: {e}')
                import app.email as email
                email.send_email_to_admin(f'Failed to swap EBEN rewards to BCH. Exception: {e}')
    if pool_name in {"MistToken", "LNS"}:
        ABI = open(f"ABIs/{assets_balances[pool_name]['harvest_ABI']}", "r")
        abi = json.loads(ABI.read())
        ratio = xsushi_ratio(assets_balances[pool_name]["CA"], assets_balances[pool_name]["BAR_CA"])
        amount_to_harvest = amount / ratio
        contract = w3.eth.contract(address=assets_balances[pool_name]["BAR_CA"], abi=abi)
        harvest_tx = contract.functions.leave(int(amount_to_harvest)).buildTransaction(
            {'chainId': 10000,
             'from': portfolio_address,
             'gasPrice': w3.toWei('1.05', 'gwei')
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
             'gasPrice': w3.toWei('1.05', 'gwei')
             })
        send_transaction(pool_name, harvest_tx)
        try:
            swap_assets("0x56381cB87C8990971f3e9d948939e1a95eA113a3", "0x0000000000000000000000000000000000000000", harvest_amount)
        except Exception as e:
            logger.error(f'Failed to swap GOB rewards to BCH. Exception: {e}')
            import app.email as email
            email.send_email_to_admin(f'Failed to swap GOB rewards to BCH. Exception: {e}')
    if pool_name == "FlexUSD":
        swap_assets("0x7b2B3C5308ab5b2a1d9a94d20D35CCDf61e05b72", "0x0000000000000000000000000000000000000000", amount)

def send_transaction(identifier, tx,*account):
    # identifier is just a string to help the admin to identify the tx if it fails.
    # account contains the address and the private key env location
    if not account:
        address = portfolio_address
        priv_key_env = 'PORTFOLIO_PRIV_KEY'
    else:
        address, priv_key_env = account
    import os
    tx['gas'] *= 1.5
    tx['gas'] = int(tx['gas']) # Decimals removed
    nonce = w3.eth.get_transaction_count(address)
    tx['nonce'] = nonce
    private_key = os.environ.get(priv_key_env)
    if private_key == None:
        import app.email as email
        email.send_email_to_admin(f"Private key for account {address} not loaded on shell environment")
        return
    # Check is there enough BCH to pay the gas fee
    if not check_bch_balance(address, tx=tx):
        import app.email as email
        fee = tx['gas'] * tx['gasPrice']
        email.send_email_to_admin(f"Not enough BCH to send a tx in account {address}. Fee is {fee}.")
        #TX will be sent anyways
    signed_txn = w3.eth.account.sign_transaction(tx, private_key=private_key)
    try:
        TXID = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    except exceptions.SolidityError as error:
        logger.error(f'TX reverted. Identifier is {identifier}, error: {error}')
        import app.email as email
        email.send_email_to_admin(f'TX reverted. Identifier is {identifier}, error: {error}')
    except Exception as e:
        print("Broad exception triggered")
        logger.error(f'TX failed to sent, error is {e}. Identifier is {identifier}')
        import app.email as email
        email.send_email_to_admin(f'TX failed to sent, error is {e}. Identifier is {identifier}')
    else:
        hex_TXID = w3.toHex(TXID)
        logger.info(f'TXID {hex_TXID} sent, identifier is {identifier}')
        try:
            receipt = w3.eth.wait_for_transaction_receipt(TXID)
            if receipt.status == 0:
                import app.email as email
                email.send_email_to_admin(f"Harvesting failed for {identifier}, TXID is {TXID}")
                logger.error(f'TXID {hex_TXID} failed, identifier is {identifier}')
        except exceptions.TimeExhausted:
            logger.error(f'Failed to get TX status, TXID is {hex_TXID}, identifier is {identifier}')
            import app.email as email
            email.send_email_to_admin(f'Failed to get TX status, TXID is {hex_TXID}, identifier is {identifier}')
        except Exception as e:
            logger.error(f'Failed to get TX status, error is {e}, TXID is {hex_TXID}, identifier is {identifier}')
            import app.email as email
            email.send_email_to_admin(f'Failed to get TX status, error is {e}, TXID is {hex_TXID}, identifier is {identifier}')
    return receipt

def harvest_farms_rewards():
    # Harvest all the rewards for every farm except BlockNG Beam, which are considered illiquid.
    for DEX in farms:
        if DEX in ("Mistswap", "Tangoswap"):
            ABI = open(f"ABIs/{farms[DEX]['factory_ABI']}", "r")
            abi = json.loads(ABI.read())
            contract = w3.eth.contract(address=farms[DEX]['factory'], abi=abi)
            for i in range(len(farms[DEX]['farms'])):
                harvest_tx = contract.functions.deposit(farms[DEX]['farms'][i]['pool_id'], 0).buildTransaction(
                    {'chainId': 10000,
                     'from': portfolio_address,
                     'gasPrice': w3.toWei('1.05', 'gwei')
                     })
                send_transaction(farms[DEX]['farms'][i]["lp_CA"], harvest_tx)
        if DEX == "BlockNG-Kudos":
            ABI = open("ABIs/BlockNG-farm.json", "r")
            abi = json.loads(ABI.read())
            for i in range(len(farms[DEX]['farms'])):
                contract = w3.eth.contract(address=farms[DEX]["farms"][i]["CA"], abi=abi)
                harvest_tx = contract.functions.getReward(portfolio_address, [assets_balances["LAW"]["CA"]]).buildTransaction(
                    {'chainId': 10000,
                     'from': portfolio_address,
                     'gasPrice': w3.toWei('1.05', 'gwei')
                     })
                send_transaction(f"Harvesting BlockNG Kudos farm {farms[DEX]['farms'][i]['lp_CA']}", harvest_tx)

def harvest_tango_sidx_farm(*account):
    address, priv_key_env = account
    # Harvest SIDX/BCH farm on Tangoswap, in the second wallet
    ABI = open("ABIs/MIST-Master-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address="0x38cC060DF3a0498e978eB756e44BD43CC4958aD9", abi=abi)
    harvest_tx = contract.functions.deposit(32, 0).buildTransaction(
        {'chainId': 10000,
         'from': address,
         'gasPrice': w3.toWei('1.05', 'gwei')
         })
    send_transaction("Harvesting SIDX/BCH farm on Tango", harvest_tx, *account)
    # Then, get the Tango amount harvested
    tango_CA = "0x73BE9c8Edf5e951c9a0762EA2b1DE8c8F38B5e91"
    tango_amount = int(round(get_SEP20_balance(tango_CA, address) / 2))
    # Swap half of the amount for SIDX
    swap_assets(tango_CA, SIDX_CA, tango_amount, *account)
    # Swap the rest to WBCH
    tango_amount = int(round(get_SEP20_balance(tango_CA, address)))
    swap_assets(tango_CA, WBCH_CA, tango_amount, *account)
    # Add liquidity to the SIDX/WBCH pool
    tokens_dictionary = {"token0": {"CA": WBCH_CA, "amount": 0},
                         "token1": {"CA": SIDX_CA, "amount": "all"}}
    LP_CA = "0x4509Ff66a56cB1b80a6184DB268AD9dFBB79DD53"
    tango_router = "0xb93184fB3eEDb4d32150763578cA305488240c8e"
    add_liquidity(tokens_dictionary, LP_CA, tango_router, *account)
    # Time to check the LP tokens balance
    ABI = open("ABIs/UniswapV2Pair.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=LP_CA, abi=abi)
    LP_balance = int(contract.functions.balanceOf(address).call())
    if LP_balance == 0:
        logger.error(f'No liquidity to add to SIDX/BCH Tango farm. LP balance is 0.')
        import app.email as email
        email.send_email_to_admin(f'No liquidity to add to SIDX/BCH Tango farm. LP balance is 0.')
        return
    # Finally, LP tokens are deposited on the farm
    ABI = open("ABIs/MIST-Master-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address="0x38cC060DF3a0498e978eB756e44BD43CC4958aD9", abi=abi)
    deposit_tx = contract.functions.deposit(32, LP_balance).buildTransaction(
        {'chainId': 10000,
         'from': address,
         'gasPrice': w3.toWei('1.05', 'gwei')
         })
    send_transaction(f"Depositing {LP_balance} SIDX/WBCH LP tokens to TangoSwap farm", deposit_tx, *account)

def harvest_sidx_ember_farm(*account):
    address, priv_key_env = account
    # Harvest SIDX/EMBER farm on Emberswap, in the second wallet
    ABI = open("ABIs/EMBER_Distributor-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address="0x8ecb32C33AB3f7ee3D6Ce9D4020bC53fecB36Be9", abi=abi)
    harvest_tx = contract.functions.deposit(31, 0).buildTransaction(
        {'chainId': 10000,
         'from': address,
         'gasPrice': w3.toWei('1.05', 'gwei')
         })
    send_transaction("Harvesting SIDX/EMBER farm on Emberswap", harvest_tx, *account)
    # Then, get the Ember amount harvested
    ember_CA = "0x6BAbf5277849265b6738e75AEC43AEfdde0Ce88D"
    ember_amount = int(round(get_SEP20_balance(ember_CA, address) / 2))
    # Swap half of the amount for SIDX
    swap_assets(ember_CA, SIDX_CA, ember_amount, *account)
    # Add liquidity to the SIDX/EMBER pool
    LP_CA = "0x97dEAeB1A9A762d97Ac565cD3Ff7629CD6d55D09"
    ember_router = "0x217057A8B0bDEb160829c19243A2E03bfe95555a"
    try:
        tokens_dictionary = {"token0": {"CA": ember_CA, "amount": "all"},
                             "token1": {"CA": SIDX_CA, "amount": 0}}
        add_liquidity(tokens_dictionary, LP_CA, ember_router, *account, min_amount_percentage=2)
    except Exception as e:
        logger.error(f'Failed to add liquidity to SIDX/EMBER farm, trying to modify the amounts. Error is {e}.')
        import app.email as email
        email.send_email_to_admin(f'Failed to add liquidity to SIDX/EMBER farm, trying to modify the amounts. Error is {e}.')
        tokens_dictionary = {"token0": {"CA": ember_CA, "amount": 0},
                             "token1": {"CA": SIDX_CA, "amount": "all"}}
        add_liquidity(tokens_dictionary, LP_CA, ember_router, *account, min_amount_percentage=2)
    # Time to check the LP tokens balance
    ABI = open("ABIs/UniswapV2Pair.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=LP_CA, abi=abi)
    LP_balance = int(contract.functions.balanceOf(address).call())
    if LP_balance == 0:
        logger.error(f'No liquidity to add to SIDX/EMBER farm. Error is {e}.')
        import app.email as email
        email.send_email_to_admin(f'No liquidity to add to SIDX/EMBER farm. Error is {e}.')
        return
    # Finally, LP tokens are deposited on the farm
    ABI = open("ABIs/EMBER_Distributor-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address="0x8ecb32C33AB3f7ee3D6Ce9D4020bC53fecB36Be9", abi=abi)
    deposit_tx = contract.functions.deposit(31, LP_balance).buildTransaction(
        {'chainId': 10000,
         'from': address,
         'gasPrice': w3.toWei('1.05', 'gwei')
         })
    send_transaction(f"Depositing {LP_balance} SIDX/EMBER LP tokens to EmberSwap farm", deposit_tx, *account)

def get_ETF_assets_allocation(farms):
    portfolio = {"Standalone assets": {}, "Farms": {}}
    total_percentage = 0
    total_value = 0
    for asset in pie_chart_data:
        if assets_balances[asset]["Liquid"]:
            portfolio["Standalone assets"][asset] = pie_chart_data[asset]
            total_value += portfolio["Standalone assets"][asset]
    for DEX in farms:
        # BlockNG Beam farms are removed because they're considered illiquid
        if DEX != "BlockNG-Beam":
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

def swap_assets(asset_in, asset_out, amount, *account):
    # asset_in and asset_out are the respective contract address of each token. Amount is the amount to swap.
    # First, we need to make sure that the portfolio holds the required amount of asset_in
    if not account:
        address = portfolio_address
        priv_key_env = 'PORTFOLIO_PRIV_KEY'
    else:
        address, priv_key_env = account
    asset_in_amount = get_SEP20_balance(asset_in, address)
    if amount == "all":
        if asset_in_amount != 0:
            amount = asset_in_amount
        else:
            logger.info(f'Warning: no balance of {asset_in} in account {address}.')
            import app.email as email
            email.send_email_to_admin(f'Warning: no balance of {asset_in} in account {address}.')
            return
    if asset_in_amount < amount:
        logger.info(f'Warning: not enough {asset_in} balance in account {address}, needed {amount}.')
        import app.email as email
        email.send_email_to_admin(f'Warning: not enough {asset_in} balance, needed {amount}.')
        return
    # Second, we need to know if SmartSwap router is allowed to swap asset_in
    router = "0xEd2E356C00A555DDdd7663BDA822C6acB34Ce614"
    asset_allowance(asset_in, router, amount="all", *account)
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
         'from': address,
         'gasPrice': w3.toWei('1.05', 'gwei')
         })
    identifier = f"Swap {amount} {asset_in} for {asset_out} in account {address}"
    send_transaction(identifier, swap_tx, *account)

def asset_allowance(token_CA, spender, *account, amount="all"):
    if not account:
        address = portfolio_address
        priv_key_env = 'PORTFOLIO_PRIV_KEY'
    else:
        address, priv_key_env = account
    ABI = open("ABIs/ERC20-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=token_CA, abi=abi)
    allowance = contract.functions.allowance(address, spender).call()
    if allowance != 0:
        return
    else:
        if amount == "all":
            amount = contract.functions.totalSupply().call()
        allowance_tx = contract.functions.approve(spender, amount).buildTransaction(
            {'chainId': 10000,
             'from': address,
             'gasPrice': w3.toWei('1.05', 'gwei')
             })
        send_transaction(f"Approving {token_CA} to be spent by {spender} in account {address}", allowance_tx, *account)

def add_liquidity(tokens_dictionary, LP_CA, router, *account, min_amount_percentage=1):
    '''tokens_dictionary has the following structure:
    tokens_dictionary = {"token0": {"CA": CA, "amount": "all" | amount | 0},
                        "token1": {"CA": CA, "amount": "all" | amount | 0}}
    where tries to match all token balance with the other, amount is an int number and 0 means that the other token will decide the matching amount.'''
    if not account:
        address = portfolio_address
        priv_key_env = 'PORTFOLIO_PRIV_KEY'
    else:
        address, priv_key_env = account
    chosen_token = "token0"
    if tokens_dictionary["token1"]["amount"] != 0:
        chosen_token = "token1"
    # Let's get the amount to swap of the chosen token
    if tokens_dictionary[chosen_token]["amount"] == "all":
        tokens_dictionary[chosen_token]["amount"] = get_SEP20_balance(tokens_dictionary[chosen_token]["CA"], address)
    # Now, let's get the balance of the counter-token to add liquidity
    ABI = open("ABIs/UniswapV2Pair.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=LP_CA, abi=abi)
    token0_reserves, token1_reserves = [contract.functions.getReserves().call()[i] for i in (0, 1)]
    if chosen_token == "token0":
        tokens_dictionary["token1"]["amount"] = int(round((tokens_dictionary["token0"]["amount"] / token0_reserves) * token1_reserves))
    else:
        tokens_dictionary["token0"]["amount"] = int(round((tokens_dictionary["token1"]["amount"] / token1_reserves) * token0_reserves))
    # Router must be allowed to spend both tokens
    asset_allowance(tokens_dictionary["token0"]["CA"], router, amount="all", *account)
    asset_allowance(tokens_dictionary["token1"]["CA"], router, amount="all", *account)
    # Now we can construct the addLiquidity() function
    token0_min_amount = int(round(tokens_dictionary["token0"]["amount"] * ((100 - min_amount_percentage) / 100)))
    token1_min_amount = int(round(tokens_dictionary["token1"]["amount"] * ((100 - min_amount_percentage) / 100)))
    ABI = open("ABIs/UniswapV2Router.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=router, abi=abi)
    deadline = int(time()) + 60
    add_liquidity_tx = contract.functions.addLiquidity(tokens_dictionary["token0"]["CA"], tokens_dictionary["token1"]["CA"], tokens_dictionary["token0"]["amount"], tokens_dictionary["token1"]["amount"], token0_min_amount, token1_min_amount, address, deadline).buildTransaction(
        {'chainId': 10000,
         'from': address,
         'gasPrice': w3.toWei('1.05', 'gwei')
         })
    receipt = send_transaction(f"Adding liquidity: at least {token0_min_amount} of {tokens_dictionary['token0']['CA']} and {token1_min_amount} of {tokens_dictionary['token1']['CA']} in account {address}", add_liquidity_tx, *account)
    if receipt:
        ABI = open("ABIs/UniswapV2Pair.json", "r")
        abi = json.loads(ABI.read())
        contract = w3.eth.contract(address=LP_CA, abi=abi)
        addLiquidity_event = contract.events.Mint().processReceipt(receipt)
        logger.info(f'Liquidity added: {addLiquidity_event[0]["args"]["amount0"]} of token0 and {addLiquidity_event[0]["args"]["amount1"]} of token1')
def remove_liquidity(percentage_to_withdraw, LP_CA, router, *account, min_amount_percentage=1):
    if not account:
        address = portfolio_address
        priv_key_env = 'PORTFOLIO_PRIV_KEY'
    else:
        address, priv_key_env = account
    # First, let's get the balance of the LP token
    ABI = open("ABIs/UniswapV2Pair.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=LP_CA, abi=abi)
    LP_token_balance = contract.functions.balanceOf(address).call()
    amount_to_withdraw = (LP_token_balance * percentage_to_withdraw) / 100 # Liquidity parameter in removeLiquidity function
    token0_reserves, token1_reserves = [contract.functions.getReserves().call()[i] for i in (0, 1)]
    token0_address = contract.functions.token0().call()
    token1_address = contract.functions.token1().call()
    LP_total_supply = contract.functions.totalSupply().call()
    token0_amount = (amount_to_withdraw / LP_total_supply) * token0_reserves
    token1_amount = (amount_to_withdraw / LP_total_supply) * token1_reserves
    # Router must be allowed to spend the LP token
    asset_allowance(LP_CA, router, amount="all", *account)
    # Now we can construct the removeLiquidity() function
    token0_min_amount = int(round(token0_amount * ((100 - min_amount_percentage) / 100)))
    token1_min_amount = int(round(token1_amount * ((100 - min_amount_percentage) / 100)))
    ABI = open("ABIs/UniswapV2Router.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=router, abi=abi)
    deadline = int(time()) + 60
    add_liquidity_tx = contract.functions.removeLiquidity(token0_address, token1_address, amount_to_withdraw, token0_min_amount, token1_min_amount, address, deadline).buildTransaction(
        {'chainId': 10000,
         'from': address,
         'gasPrice': w3.toWei('1.05', 'gwei')
         })
    send_transaction(f"Removing liquidity: at least {token0_min_amount} of {token0_address} and {token1_min_amount} of {token1_address} in account {address}", add_liquidity_tx, *account)

def wrap_BCH(amount, *account):
    amount = int(amount)
    if not account:
        address = portfolio_address
        priv_key_env = 'PORTFOLIO_PRIV_KEY'
    else:
        address, priv_key_env = account
    ABI = open("ABIs/WBCH-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=WBCH_CA, abi=abi)
    wrap_bch_tx = contract.functions.deposit().buildTransaction(
        {'chainId': 10000,
         'from': address,
         'value': amount,
         'gasPrice': w3.toWei('1.05', 'gwei')
         })
    send_transaction(f'Wrapping {amount} BCH from account {address}', wrap_bch_tx, *account)

def unwrap_BCH(amount, *account):
    amount = int(amount)
    if not account:
        address = portfolio_address
        priv_key_env = 'PORTFOLIO_PRIV_KEY'
    else:
        address, priv_key_env = account
    ABI = open("ABIs/WBCH-ABI.json", "r")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=WBCH_CA, abi=abi)
    unwrap_bch_tx = contract.functions.withdraw(int(amount)).buildTransaction(
        {'chainId': 10000,
         'from': address,
         'gasPrice': w3.toWei('1.05', 'gwei')
         })
    send_transaction(f'Unwrapping {amount} BCH from account {address}', unwrap_bch_tx, *account)

def get_SEP20_balance(token_CA, wallet):
    ABI = open("ABIs/ERC20-ABI.json")
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=token_CA, abi=abi)
    return int(contract.functions.balanceOf(wallet).call())

def transfer_asset(asset, amount, destination, *account):
    # Function to transfer SEP20 assets
    if not account:
        address = portfolio_address
        priv_key_env = 'PORTFOLIO_PRIV_KEY'
    else:
        address, priv_key_env = account
    amount_available = get_SEP20_balance(asset, address)
    if amount == "all":
        if amount_available != 0:
            amount = amount_available
        else:
            logger.info(f'Warning: no balance of {asset} in account {address}.')
            import app.email as email
            email.send_email_to_admin(f'Warning: no balance of {asset} in account {address}.')
            return
    if amount_available < amount:
        logger.info(f'Warning: not enough {asset} balance in account {address}, needed {amount}.')
        import app.email as email
        email.send_email_to_admin(f'Warning: not enough {asset} balance, needed {amount}.')
        return
    ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address=asset, abi=abi)
    transfer_tx = contract.functions.transfer(destination, int(amount)).buildTransaction(
        {'chainId': 10000,
         'from': address,
         'gasPrice': w3.toWei('1.05', 'gwei')
         })
    send_transaction(f'Transfer {amount} of token {asset} from account {address}', transfer_tx, *account)
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
    get_farms(bch_price)
    make_pie_chart(pie_chart_data, "assets_pie_chart")
    make_pie_chart(farms_pie_chart_data, "farms_pie_chart")
    make_pie_chart(sidx_liquidity_pie_chart_data, "liquidity_allocation")
    make_pie_chart(global_stats_pie_chart_data, "global_stats")
    ETF_portfolio = get_ETF_assets_allocation(farms)
    global_portfolio_stats = {"total_liquid_value": round(total_liquid_value, 2),
                              "total_illiquid_value": round(total_illiquid_value, 2),
                              "total_portfolio_balance": round(total_liquid_value + total_illiquid_value, 2),
                              "total_rewards_value": round(total_rewards_value, 2), "value_per_sidx": round(
            round(total_liquid_value + total_illiquid_value, 2) / SIDX_stats["Total supply"], 2)}

    # Calculate the MarketValue/PortfilioValue ratio (less than 1 means 'underbacked')
    global_portfolio_stats["ratio"] = round(float(SIDX_stats["Price"].split()[0]) / global_portfolio_stats["value_per_sidx"], 2)

    # Get data for the ETF portfolio
    ETF_SEP20_tokens, ETF_staked_assets = get_balances(bch_price, portfolio_address=ETF_portfolio_address)
    get_farms(bch_price, farms=ETF_farms)

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
    with open('data/NFTs.json', 'w') as file:
        json.dump(NFTs, file, indent=4)
    with open('data/FARMS.json', 'w') as file:
        json.dump(farms, file, indent=4)
    with open('data/GLOBAL_STATS.json', 'w') as file:
        json.dump(global_portfolio_stats, file, indent=4)
    with open('data/ETF_portfolio.json', 'w') as file:
        json.dump(ETF_portfolio, file, indent=4)
    with open('data/ETF_SEP20_BALANCES.json', 'w') as file:
        json.dump(ETF_SEP20_tokens, file, indent=4)
    with open('data/ETF_STAKED_ASSETS.json', 'w') as file:
        json.dump(ETF_staked_assets, file, indent=4)
    with open('data/ETF_FARMS.json', 'w') as file:
        json.dump(ETF_farms, file, indent=4)

if __name__ == "__main__":
    main()
