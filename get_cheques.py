import json
from web3 import Web3
import requests
from datetime import datetime
import calendar
from app import db
from app.models import Proposal, User

w3 = Web3(Web3.HTTPProvider('https://smartbch.greyh.at'))
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

def migrate_proposals():
    # Migrates proposals from dict to SQL
    with open("data/VOTES.json", "r") as file:
        votes = json.load(file)
    for proposal in votes["proposals"]:
        proposal_id = proposal[1:]
        proposal_text = votes["proposals"][proposal]["Proposal text"]
        author = votes["proposals"][proposal]["Author"]
        unixtime_start = votes["proposals"][proposal]["UNIX Start time"]
        start_time = votes["proposals"][proposal]["Start time"]
        unixtime_end = votes["proposals"][proposal]["UNIX End time"]
        end_time = votes["proposals"][proposal]["End time"]
        status = votes["proposals"][proposal]["Open"]
        voting_period = (unixtime_end - unixtime_start) / 24*60*60
        option_b_tag = None
        option_b_votes = None
        option_c_tag = None
        option_c_votes = None
        if "Result" in votes["proposals"][proposal]:
            result = votes["proposals"][proposal]["Result"]
        else:
            result = None
        if "ACCEPT" in votes["proposals"][proposal]["Choices"]:
            option_a_tag = "ACCEPT"
            option_a_votes = votes["proposals"][proposal]["Choices"]["ACCEPT"]["Votes"]
            reject_votes = votes["proposals"][proposal]["Choices"]["REJECT"]["Votes"]
            reject_option = "B"
        else:
            for choice in votes["proposals"][proposal]["Choices"]:
                if votes["proposals"][proposal]["Choices"][choice]["TAG"] == "REJECT":
                    reject_votes = votes["proposals"][proposal]["Choices"][choice]["Votes"]
                    reject_option = choice
                else:
                    if choice == "A":
                        option_a_tag = votes["proposals"][proposal]["Choices"][choice]["TAG"]
                        option_a_votes = votes["proposals"][proposal]["Choices"][choice]["Votes"]
                    if choice == "B":
                        option_b_tag = votes["proposals"][proposal]["Choices"][choice]["TAG"]
                        option_b_votes = votes["proposals"][proposal]["Choices"][choice]["Votes"]
                    if choice == "C":
                        option_c_tag = votes["proposals"][proposal]["Choices"][choice]["TAG"]
                        option_c_votes = votes["proposals"][proposal]["Choices"][choice]["Votes"]
        if db.session.query(User).filter(User.public_address == author).first() is None:
            u = User(public_address=author)
            db.session.add(u)
        else:
            u = db.session.query(User).filter(User.public_address == author).first()
        p = Proposal(id=proposal_id, proposal=proposal_text, author=u.public_address, voting_period=voting_period, unixtime_start=unixtime_start, start_time=start_time, unixtime_end=unixtime_end, end_time=end_time, open=status, option_a_tag=option_a_tag, option_a_votes=option_a_votes, reject_votes=reject_votes, reject_option=reject_option, result=result)
        db.session.add(p)
        if option_b_tag is not None:
            p = db.session.query(Proposal).filter(Proposal.id == proposal_id).first()
            p.option_b_tag = option_b_tag
            p.option_b_votes = option_b_votes
            db.session.add(p)
        if option_c_tag is not None:
            p = db.session.query(Proposal).filter(Proposal.id == proposal_id).first()
            p.option_c_tag = option_c_tag
            p.option_c_votes = option_c_votes
            db.session.add(p)
        db.session.commit()

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

def submit_sql_proposal(proposal_id, proposal_text, author, start="now", choices="simple", voting_period=7):
    # Start time always in UNIX timestamp
    # This function stores the proposal in a SQL table instead of a dictionary
    # proposal_id is a number
    if db.session.query(Proposal).filter(Proposal.id == proposal_id).first() is not None:
        return "Proposal ID already exists"
    if not type(proposal_id) == int:
        return "Incorrect proposal ID format"

    proposal = Proposal(id=proposal_id, proposal=proposal_text, proposal_author=author, voting_period=voting_period)

    if start == "now":
        d = datetime.utcnow()
        proposal.unixtime_start = calendar.timegm(d.utctimetuple())
        proposal.start_time = datetime.utcfromtimestamp(int(calendar.timegm(d.utctimetuple()))).strftime('%Y-%m-%d %H:%M:%S')
    else:
        proposal.unixtime_start = start
        proposal.start_time = datetime.utcfromtimestamp(proposal.unixtime_start).strftime('%Y-%m-%d %H:%M:%S')

    if choices == "simple":
        proposal.option_a_tag = "ACCEPT"
        proposal.option_a_votes = 0
        proposal.reject_option = "B"
        proposal.reject_votes = 0
    else:
        # In this case, choices are input as a dict {"A": {"TAG": "foo", "Votes": 0}...}
        for choice in choices:
            if choices[choice]["TAG"] == "REJECT":
                proposal.reject_option = choice
                proposal.reject_votes = choices[choice]["Votes"]
            elif choice == "A":
                proposal.option_a_tag = choices[choice]["A"]["TAG"]
                proposal.option_a_votes = choices[choice]["A"]["Choices"]
            elif choice == "B":
                proposal.option_b_tag = choices[choice]["B"]["TAG"]
                proposal.option_b_votes = choices[choice]["B"]["Choices"]
            elif choice == "C":
                proposal.option_c_tag = choices[choice]["C"]["TAG"]
                proposal.option_c_votes = choices[choice]["C"]["Choices"]
    proposal.unixtime_end = proposal.unixtime_start + voting_period * 24 * 60 * 60
    proposal.end_time = datetime.utcfromtimestamp(proposal.unixtime_end).strftime('%Y-%m-%d %H:%M:%S')

    d = datetime.utcnow()
    if calendar.timegm(d.utctimetuple()) > proposal.unixtime_end:
        proposal.open = False
    else:
        proposal.open = True

    db.session.add(proposal)
    db.session.commit()

def approve_proposal(proposal_id):
    proposal = Proposal.query.get(int(proposal_id))
    d = datetime.utcnow()
    proposal.unixtime_start = calendar.timegm(d.utctimetuple())
    proposal.start_time = datetime.utcfromtimestamp(int(calendar.timegm(d.utctimetuple()))).strftime(
        '%Y-%m-%d %H:%M:%S')
    proposal.unixtime_end = proposal.unixtime_start + proposal.voting_period * 24 * 60 * 60
    proposal.end_time = datetime.utcfromtimestamp(proposal.unixtime_end).strftime('%Y-%m-%d %H:%M:%S')
    proposal.admin_approved = True
    if proposal.option_b_tag == None:
        proposal.reject_option = "B"
    elif proposal.option_c_tag == None:
        proposal.reject_option = "C"
    else:
        proposal.reject_option = "D"
    db.session.commit()

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
                vote_ID = vote_ID[1:] # Remove the hashtag
                if db.session.query(Proposal).filter(Proposal.id == vote_ID).first() != None:
                    proposal = Proposal.query.get(vote_ID)
                    if cheque[1]["deadline"] >= proposal.unixtime_end and transaction_timestamp >= proposal.unixtime_start:
                        if choice == "ACCEPT" and proposal.option_a_tag == "ACCEPT":
                            proposal.option_a_votes += (cheque[1]["amount"] / 10 ** 18)
                        if choice == "REJECT":
                            proposal.reject_votes += (cheque[1]["amount"] / 10 ** 18)
                        if choice == proposal.reject_option:
                            proposal.reject_votes += (cheque[1]["amount"] / 10 ** 18)
                        if choice == "A":
                            proposal.option_a_votes += (cheque[1]["amount"] / 10 ** 18)
                        if choice == "B":
                            if proposal.option_b_tag != "REJECT":
                                proposal.option_b_votes += (cheque[1]["amount"] / 10 ** 18)
                        if choice == "C":
                            if proposal.option_c_tag != "REJECT":
                                proposal.option_c_votes += (cheque[1]["amount"] / 10 ** 18)
                    db.session.commit()
    votes["last scanned block"] = last_block

    #Now it's time to check if any proposal has closed:
    d = datetime.utcnow()
    current_time = calendar.timegm(d.utctimetuple())
    proposals = Proposal.query.filter_by(open=True).filter_by(admin_approved=True).all()
    for proposal in proposals:
        if proposal.unixtime_end < current_time:
            proposal.open = False
            total_votes = 0
            result_dict = {}
            if type(proposal.option_a_votes) == float:
                result_dict[proposal.option_a_tag] = proposal.option_a_votes
                total_votes += proposal.option_a_votes
            if type(proposal.option_b_votes) == float:
                result_dict[proposal.option_b_tag] = proposal.option_b_votes
                total_votes += proposal.option_b_votes
            if type(proposal.option_c_votes) == float:
                result_dict[proposal.option_c_tag] = proposal.option_c_votes
                total_votes += proposal.option_c_votes
            result_dict["REJECT"] = proposal.reject_votes
            total_votes += proposal.reject_votes
            if total_votes < quorum:
                proposal.result = f"REJECTED: Required quorum of {quorum} SIDX not reached"
            else:
                proposal.result = sorted(result_dict.items(), key=lambda x: x[1], reverse=True)[0][0]
    db.session.commit()

    with open('data/VOTES.json', 'w') as file:
        json.dump(votes, file, indent=4, default=str)

if __name__ == "__main__":
    main()