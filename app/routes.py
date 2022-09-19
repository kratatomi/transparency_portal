import json
import time
from os import listdir, getcwd
from os.path import isfile, join, abspath
from datetime import datetime

from eth_account.messages import defunct_hash_message
from flask import render_template, url_for, request, send_from_directory, abort, redirect, flash
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy import desc
from web3 import Web3

import server_settings
from app import app, db
from app.models import Proposal, Users
from app.forms import ProposalForm, VoteForm
from app.email import send_new_proposal_email, send_email_to_admin

# from voting_platform import send_memo
from bitcash.wallet import Key

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(join(app.root_path, 'static'),
                          'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
@app.route('/index')
def index():
    with open('data/SEP20_BALANCES.json') as sep20_balances_file:
        sep20_balances = json.load(sep20_balances_file)
    with open('data/STACKED_ASSETS.json') as stacked_assets_file:
        stacked_assets = json.load(stacked_assets_file)
    with open('data/LP_BALANCES.json') as lp_balances_file:
        lp_balances = json.load(lp_balances_file)
    with open('data/EXTRA_LP_BALANCES.json') as extra_lp_balances_file:
        extra_lp_balances = json.load(extra_lp_balances_file)
    with open('data/NFTs.json') as NFTs_file:
        NFTs = json.load(NFTs_file)
    with open('data/FARMS.json') as farms_file:
        farms = json.load(farms_file)
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    with open('data/GLOBAL_STATS.json') as global_stats_file:
        global_stats = json.load(global_stats_file)
    return render_template("index.html", title="Portfolio tracker", sidx_stats=sidx_stats, sep20_balances=sep20_balances, stacked_assets=stacked_assets, lp_balances=lp_balances, extra_lp_balances=extra_lp_balances, punks=NFTs["PUNKS"], law_rights=NFTs["LAW Rights"], farms=farms, global_stats=global_stats)

@app.route('/proposals')
def proposals():
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    page = request.args.get('page', 1, type=int)
    proposals = Proposal.query.filter_by(admin_approved=True).order_by(desc(Proposal.id)).paginate(page, app.config['PROPOSALS_PER_PAGE'], False)
    next_url = url_for('proposals', page=proposals.next_num) \
        if proposals.has_next else None
    prev_url = url_for('proposals', page=proposals.prev_num) \
        if proposals.has_prev else None
    return render_template("proposals.html", title="Proposals", proposals=proposals.items, sidx_stats=sidx_stats, next_url=next_url,
                           prev_url=prev_url)

@app.route('/proposals/<int:id>', methods=['GET', 'POST'])
def display_proposal(id):
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    if db.session.query(Proposal).filter(Proposal.id == id).first() is not None:
        proposal = Proposal.query.get(id)
        if current_user.is_authenticated and proposal.open:
            user = Users.query.get(current_user.get_id())
            with open(f'data/balances/{proposal.id}.json') as balances_file:
                balances = json.load(balances_file)
            if user.has_voted(proposal):
                return render_template("proposal.html", title=f"Proposal {id}", proposal=proposal,
                                       sidx_stats=sidx_stats)
            if user.public_address in balances:
                user_balance = round(balances[user.public_address], 3)
                choices = []
                choices.append("A")
                if proposal.option_b_tag != None:
                    choices.append("B")
                if proposal.option_c_tag != None:
                    choices.append("C")
                choices.append("REJECT")
                form = VoteForm()
                form.choice.choices = choices
                if form.validate_on_submit():
                    if form.choice.data == "A":
                        proposal.option_a_votes += user_balance
                    if form.choice.data == "B":
                        proposal.option_b_votes += user_balance
                    if form.choice.data == "C":
                        proposal.option_c_votes += user_balance
                    if form.choice.data == "REJECT":
                        proposal.reject_votes += user_balance
                    user.votes.append(proposal)
                    db.session.commit()
                    flash(f'{user_balance} votes has been added to the option {form.choice.data}')
                    BCH_key = Key(server_settings.BCH_PRIV_KEY)
                    balance = BCH_key.get_balance()
                    if int(balance) < 2000:
                        text = f"Only {balance} satoshis left in the voting platform wallet"
                        send_email_to_admin(text)
                    vote_message = f"User {user.public_address} voted on proposal {proposal.id}: {user_balance} votes to option {form.choice.data}"
                    app.logger.info(vote_message)
                    send_memo(BCH_key, vote_message)
                    return render_template("proposal.html", title=f"Proposal {id}", proposal=proposal,
                                           sidx_stats=sidx_stats)
                return render_template("proposal.html", title=f"Proposal {id}", proposal=proposal,
                                       sidx_stats=sidx_stats, form=form, user_balance=user_balance)
        return render_template("proposal.html", title=f"Proposal {id}", proposal=proposal, sidx_stats=sidx_stats)
    else:
        abort(400, "Proposal not found")

@app.route('/yields', methods=['GET'])
def yields():
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    snapshots_dir = abspath(getcwd()) + "/data/snapshots"
    snapshot_files = [f for f in listdir(snapshots_dir) if isfile(join(snapshots_dir, f))]
    snapshots_dates = []
    for file in snapshot_files:
        snapshots_dates.append(str(file.split(".")[0]))
    snapshots_dates.sort(key=lambda date: datetime.strptime(date, "%d-%m-%Y"))
    snapshots_dates.reverse()
    return render_template("yield.html", title="Weekly yield", snapshots=snapshots_dates, sidx_stats=sidx_stats)

@app.route('/yields/<name>', methods=['GET', 'POST'])
def weekly_report(name):
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    file = name + ".json"
    snapshots_dir = abspath(getcwd()) + "/data/snapshots"
    snapshot_files = [f for f in listdir(snapshots_dir) if isfile(join(snapshots_dir, f))]
    if file in snapshot_files:
        with open(f'data/snapshots/{file}') as weekly_report_file:
            weekly_report = json.load(weekly_report_file)
        date = weekly_report["snapshot date"]
        sep20_balances = weekly_report["SEP20_BALANCES"]
        stacked_assets = weekly_report["STACKED_ASSETS"]
        lp_balances = weekly_report["LP_BALANCES"]
        punks = weekly_report["PUNKS_BALANCES"]
        if "FARMS" in weekly_report:
            farms = weekly_report["FARMS"]
        else:
            farms = None
        if "EXTRA_LP_BALANCES" in weekly_report:
            extra_lp_balances = weekly_report["EXTRA_LP_BALANCES"]
        else:
            extra_lp_balances = None
        if "GLOBAL_STATS" in weekly_report:
            global_stats = weekly_report["GLOBAL_STATS"]
        else:
            global_stats = None
        return render_template("index.html", title=f"Earnings report at {name}", sidx_stats=sidx_stats,  date=date, sep20_balances=sep20_balances, stacked_assets=stacked_assets, lp_balances=lp_balances, extra_lp_balances=extra_lp_balances, punks=punks, farms=farms, global_stats=global_stats)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('submit_proposal'))
    w3 = Web3(Web3.HTTPProvider('https://smartbch.greyh.at'))
    if not w3.isConnected():
        w3 = Web3(Web3.HTTPProvider('https://smartbch.fountainhead.cash/mainnet'))

    public_address = request.json[0]
    signature = request.json[1]

    domain = "transparency.smartindex.cash"

    rightnow = int(time.time())
    sortanow = rightnow - rightnow % 600

    original_message = 'Signing in to {} at {}'.format(domain, sortanow)
    message_hash = defunct_hash_message(text=original_message)
    signer = w3.eth.account.recoverHash(message_hash, signature=signature)

    if signer == public_address:
        if db.session.query(Users).filter(Users.public_address == signer).first() is None:
            user = Users(public_address=signer)
            db.session.add(user)
            db.session.commit()
        user = Users.query.filter_by(public_address=signer).first()
        login_user(user)
        return redirect(url_for('proposals'))
    else:
        abort(401, 'Could not authenticate signature')
    return redirect(url_for('proposals'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/submit_proposal', methods=['POST', 'GET'])
@login_required
def submit_proposal():
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    form = ProposalForm()
    if form.validate_on_submit():
        user = Users.query.get(current_user.get_id())
        flash(f'Your proposal has been submitted and is pending administrator approval')
        new_proposal = Proposal(proposal=form.proposal.data, proposal_author=user.public_address, voting_period=form.voting_period.data, option_a_tag=form.choice_a.data, option_b_tag=form.choice_b.data, option_c_tag=form.choice_c.data)
        db.session.add(new_proposal)
        db.session.commit()
        send_new_proposal_email(new_proposal)
        return redirect('/proposals')
    # Check if the logged user has at least 1250 SIDX tokens in his wallet
    user = Users.query.get(current_user.get_id())
    w3 = Web3(Web3.HTTPProvider('https://smartbch.greyh.at'))
    if not w3.isConnected():
        w3 = Web3(Web3.HTTPProvider('https://smartbch.fountainhead.cash/mainnet'))
    ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
    abi = json.loads(ABI.read())
    contract = w3.eth.contract(address="0xF05bD3d7709980f60CD5206BddFFA8553176dd29", abi=abi)
    SIDX_balance = contract.functions.balanceOf(user.public_address).call() / 10 ** 18
    if SIDX_balance < 1250:
        flash('You need at least 1250 SIDX token to submit a proposal')
        return url_for('proposals')
    return render_template("submit_proposal.html", title="Submit a proposal", sidx_stats=sidx_stats, form=form)