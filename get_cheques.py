import json
from web3 import Web3
import requests
from datetime import datetime
import calendar

w3 = Web3(Web3.HTTPProvider('https://smartbch.squidswap.cash/'))
if not w3.isConnected():
    w3 = Web3(Web3.HTTPProvider('https://smartbch.fountainhead.cash/mainnet'))

voting_wallets = ["0xa3533751171786035fC440bFeF3F535093EAd686",
                  "0xe26B069480c24b195Cd48c8d61857B5Aaf610569",
                  "0x711CA8Da9bE7a3Ee698dD76C632A19cFB6F768Cb",
                  "0x00033C53E5ac4A61f084D7525BAD246E61dFDc81"]
choices_list = ["ACCEPT", "REJECT", "A", "B", "C", "D"]
SIDX_CA = w3.toChecksumAddress("0xF05bD3d7709980f60CD5206BddFFA8553176dd29")
cheque_CA = w3.toChecksumAddress("0xa36C479eEAa25C0CFC7e099D3bEbF7A7F1303F40")

with open("data/SIDX_STATS.json", "r") as file:
    SIDX_STATS = json.load(file)

quorum = SIDX_STATS["Quorum"]

class SBCH:
    ID = 0
    headers = {'Content-type': 'application/json'}
    payload = {"jsonrpc": "2.0",
               "method": "undefined",
               "params": [],
               "id": ID}
    session = requests.Session()
    new_cheque = Web3.keccak(text="NewCheque(address,uint256,address,uint256,uint256,uint256,bytes)").hex() #NewCheque topic

    def queryLogs(self, address, start, topics_array=[new_cheque], end='latest', txs_limit = 0):
        address = Web3.toChecksumAddress(address)
        if type(start) == int:
            start = hex(start)
        if type(end) == int:
            end = hex(end)
        if type(txs_limit) == int:
            txs_limit = hex(txs_limit)
        self.payload["method"] = "sbch_queryLogs"
        self.payload["params"] = [address, topics_array, start, end, txs_limit]
        self.get_response()

    def get_response(self):
        self.response = self.session.post('https://smartbch.fountainhead.cash/mainnet', json=self.payload, headers=self.headers).json()

    def __init__(self):
        SBCH.ID += 1
        self.payload["id"] = self.ID

def submit_proposal(proposal_id, proposal_text, author, start="now", choices="simple", voting_period=7):
    # Start time always in UNIX timestamp
    with open("data/VOTES.json", "r") as file:
        votes = json.load(file)
    if not proposal_id[0] == "#" and proposal_id[1:].isnumeric() == True:
        return "Incorrect proposal ID format"
    if proposal_id in votes["proposals"]:
        return "Proposal ID already in file"
    proposal = {"Proposal text": proposal_text,
                "Author": author}
    if start == "now":
        d = datetime.utcnow()
        proposal["UNIX Start time"] = calendar.timegm(d.utctimetuple())
        proposal["Start time"] = datetime.utcfromtimestamp(int(calendar.timegm(d.utctimetuple()))).strftime('%Y-%m-%d %H:%M:%S')
    else:
        proposal["UNIX Start time"] = start
        proposal["Start time"] = datetime.utcfromtimestamp(proposal["UNIX Start time"]).strftime('%Y-%m-%d %H:%M:%S')

    if choices == "simple":
        proposal["Choices"] = {"ACCEPT": {"TAG": "ACCEPT", "Votes": 0}, "REJECT": {"TAG": "REJECT", "Votes": 0}}
    else:
        proposal["Choices"] = choices

    proposal["UNIX End time"] = proposal["UNIX Start time"] + voting_period * 24 * 60 * 60
    proposal["End time"] = datetime.utcfromtimestamp(proposal["UNIX End time"]).strftime('%Y-%m-%d %H:%M:%S')
    d = datetime.utcnow()
    if calendar.timegm(d.utctimetuple()) > proposal["UNIX End time"]:
        proposal["Open"] = False
    else:
        proposal["Open"] = True
    votes["proposals"][proposal_id] = proposal
    with open('data/VOTES.json', 'w') as file:
        json.dump(votes, file, indent=4, default=str)

def main():
    with open("data/VOTES.json", "r") as file:
        votes = json.load(file)
    start_block = votes["last scanned block"]
    last_block = w3.eth.get_block("latest")["number"]
    logs = SBCH()
    logs.queryLogs(cheque_CA, start_block, end=last_block)
    for log in logs.response["result"]:
        ABI = open("ABIs/ChainCheque-ABI.json", "r")
        abi = json.loads(ABI.read())
        contract = w3.eth.contract(address=cheque_CA, abi=abi)
        transaction = w3.eth.getTransaction(log["transactionHash"])
        transaction_timestamp = w3.eth.getBlock(log["blockNumber"]).timestamp
        cheque = contract.decode_function_input(transaction.input)
        if "payee" in cheque[1]:
            if cheque[1]["payee"] in voting_wallets and cheque[1]["coinType"] == SIDX_CA and len(cheque[1]["memo"].decode("utf-8")[2:].split(":")) == 2:
                vote_ID, choice = cheque[1]["memo"].decode("utf-8")[2:].split(":")
                if vote_ID in votes["proposals"]:
                    if cheque[1]["deadline"] >= votes["proposals"][vote_ID]["UNIX End time"] and transaction_timestamp >= votes["proposals"][vote_ID]["UNIX Start time"] and choice in votes["proposals"][vote_ID]["Choices"]:
                        votes["proposals"][vote_ID]["Choices"][choice]["Votes"] += (cheque[1]["amount"] / 10 ** 18)
    votes["last scanned block"] = last_block

    #Now it's time to check if any proposal has closed:
    d = datetime.utcnow()
    current_time = calendar.timegm(d.utctimetuple())
    for proposal in votes["proposals"]:
        if votes["proposals"][proposal]["UNIX End time"] < current_time and votes["proposals"][proposal]["Open"] == True:
            votes["proposals"][proposal]["Open"] = False
            total_votes = 0
            for choice in votes["proposals"][proposal]["Choices"]:
                total_votes += votes["proposals"][proposal]["Choices"][choice]["Votes"]
            if total_votes < quorum:
                votes["proposals"][proposal]["Result"] = f"REJECTED: Required quorum of {quorum} SIDX not reached"
            else:
                result_dict = {}
                for choice in votes["proposals"][proposal]["Choices"]:
                    result_dict[votes["proposals"][proposal]["Choices"][choice]["TAG"]] = votes["proposals"][proposal]["Choices"][choice]["Votes"]
                votes["proposals"][proposal]["Result"] = sorted(result_dict.items(), key=lambda x: x[1], reverse=True)[0][0]

    with open('data/VOTES.json', 'w') as file:
        json.dump(votes, file, indent=4, default=str)
        file.close()

if __name__ == "__main__":
    main()