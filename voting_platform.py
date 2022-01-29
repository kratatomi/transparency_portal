import json
from web3 import Web3
from datetime import datetime
import calendar
from app import db
from app.models import Proposal
import os

w3 = Web3(Web3.HTTPProvider('https://smartbch.greyh.at'))
if not w3.isConnected():
    w3 = Web3(Web3.HTTPProvider('https://smartbch.fountainhead.cash/mainnet'))

choices_list = ["ACCEPT", "REJECT", "A", "B", "C", "D"]
SIDX_CA = w3.toChecksumAddress("0xF05bD3d7709980f60CD5206BddFFA8553176dd29")
cheque_CA = w3.toChecksumAddress("0xa36C479eEAa25C0CFC7e099D3bEbF7A7F1303F40")

with open("data/SIDX_STATS.json", "r") as file:
    SIDX_STATS = json.load(file)

quorum = SIDX_STATS["Quorum"]

def submit_sql_proposal(proposal_id, proposal_text, author, start="now", choices="simple", voting_period=7):
    # Start time always in UNIX timestamp
    # This function allows the admin to manually submit a proposal.
    # It stores the proposal in a SQL table.
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
    from icalendar import Calendar, Event, vText
    import pytz
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
        proposal.option_b_votes = 0
        proposal.reject_option = "C"
    else:
        proposal.option_b_votes = 0
        proposal.option_c_votes = 0
        proposal.reject_option = "D"
    db.session.commit()
    # Now, make the calendar event
    cal = Calendar()
    cal.add('prodid', 'SmartIndex proposal')
    cal.add('version', '1.0')
    event = Event()
    event.add('summary', f'SmartIndex voting for proposal #{proposal.id}')
    timezone = pytz.timezone("UTC")
    date_time_obj = timezone.localize(datetime.strptime(proposal.start_time, '%Y-%m-%d %H:%M:%S'))
    event.add('dtstart', date_time_obj)
    date_time_obj = timezone.localize(datetime.strptime(proposal.end_time, '%Y-%m-%d %H:%M:%S'))
    event.add('dtend', date_time_obj)
    event['location'] = vText(f'https://transparency.smartindex.cash/proposals/{proposal.id}')
    cal.add_component(event)
    f = open(f'app/static/calendar/Proposal{proposal.id}.ics', 'wb')
    f.write(cal.to_ical())
    f.close()
    # Last step, is to make the balances snapshot associated to the proposal
    if is_tool("python3"):
        os.system("python3 sbch_eventscanner.py https://smartbch.greyh.at")
    elif is_tool("python"):
        os.system("python sbch_eventscanner.py https://smartbch.greyh.at")
    else:
        raise "No Python command found in this environment"
    import get_balances_snapshot
    get_balances_snapshot.main(proposal_id)
    print(f"Balances snapshot for proposal {proposal_id} taken")

def generate_calendar_events():
    # Use only for the first time running the app, the rest of ICS files are generate upon proposals approval
    from icalendar import Calendar, Event, vText
    import pytz
    proposals = Proposal.query.all()
    for proposal in proposals:
        if proposal.admin_approved == True:
            cal = Calendar()
            cal.add('prodid', 'SmartIndex proposal')
            cal.add('version', '1.0')
            event = Event()
            event.add('summary', f'SmartIndex voting for proposal #{proposal.id}')
            timezone = pytz.timezone("UTC")
            date_time_obj = timezone.localize(datetime.strptime(proposal.start_time, '%Y-%m-%d %H:%M:%S'))
            event.add('dtstart', date_time_obj)
            date_time_obj = timezone.localize(datetime.strptime(proposal.end_time, '%Y-%m-%d %H:%M:%S'))
            event.add('dtend', date_time_obj)
            event['location'] = vText(f'https://transparency.smartindex.cash/proposals/{proposal.id}')
            cal.add_component(event)
            f = open(f'app/static/calendar/Proposal{proposal.id}.ics', 'wb')
            f.write(cal.to_ical())
            f.close()

def is_tool(name):
    """Check whether `name` is on PATH."""

    from distutils.spawn import find_executable

    return find_executable(name) is not None

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
                vote_ID = vote_ID.strip()[1:] # Remove the hashtag
                choice = choice.strip() # Remove all potential spaces to avoid problems
                if db.session.query(Proposal).filter(Proposal.id == vote_ID).first() != None:
                    proposal = Proposal.query.get(vote_ID)
                    if cheque[1]["deadline"] >= proposal.unixtime_end and transaction_timestamp >= proposal.unixtime_start:
                        if choice == proposal.reject_option:
                            proposal.reject_votes += (cheque[1]["amount"] / 10 ** 18)
                        else:
                            if choice == "A":
                                proposal.option_a_votes += (cheque[1]["amount"] / 10 ** 18)
                            if choice == "B":
                                proposal.option_b_votes += (cheque[1]["amount"] / 10 ** 18)
                            if choice == "C":
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