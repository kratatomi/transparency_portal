import json
import time
from os import listdir, getcwd
from os.path import isfile, join, abspath
from datetime import datetime

from eth_account.messages import defunct_hash_message
from flask import render_template, url_for, request, send_from_directory, abort, redirect, flash
from flask_login import current_user, login_user, login_required
from sqlalchemy import desc
from web3 import Web3

from app import app, db
from app.models import Proposal, Users
from app.forms import ProposalForm
from app.email import send_new_proposal_email

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
    with open('data/PUNKS_BALANCES.json') as punks_balances_file:
        punks = json.load(punks_balances_file)
    with open('data/FARMS.json') as farms_file:
        farms = json.load(farms_file)
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    return render_template("index.html", title="Portfolio tracker", sidx_stats=sidx_stats, sep20_balances=sep20_balances, stacked_assets=stacked_assets, lp_balances=lp_balances, extra_lp_balances=extra_lp_balances, punks=punks, farms=farms)

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
        return render_template("index.html", title=f"Earnings report at {name}", sidx_stats=sidx_stats,  date=date, sep20_balances=sep20_balances, stacked_assets=stacked_assets, lp_balances=lp_balances, extra_lp_balances=extra_lp_balances, punks=punks, farms=farms)


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
        ABI = open("ABIs/ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
        abi = json.loads(ABI.read())
        contract = w3.eth.contract(address="0xF05bD3d7709980f60CD5206BddFFA8553176dd29", abi=abi)
        SIDX_balance = contract.functions.balanceOf(signer).call() / 10 ** 18
        if SIDX_balance < 5000:
            flash('You need at least 5000 SIDX token to submit a proposal')
            return url_for('proposals')
        else:
            if db.session.query(Users).filter(Users.public_address == signer).first() is None:
                user = Users(public_address=signer)
                db.session.add(user)
                db.session.commit()
            user = Users.query.filter_by(public_address=signer).first()
            login_user(user)
            return redirect(url_for('submit_proposal'))
    else:
        abort(401, 'Could not authenticate signature')
    return redirect(url_for('submit_proposal'))


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
    return render_template("submit_proposal.html", title="Submit a proposal", sidx_stats=sidx_stats, form=form)