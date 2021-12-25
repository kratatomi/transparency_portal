import json
import time
from os import listdir, getcwd
from os.path import isfile, join, abspath

from eth_account.messages import defunct_hash_message
from flask import render_template, url_for, request, send_from_directory, abort, redirect, flash
from flask_login import current_user, login_user, login_required
from sqlalchemy import desc
from web3 import Web3

from app import app, db
from app.models import Proposal, Users


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
    with open('data/PUNKS_BALANCES.json') as punks_balances_file:
        punks = json.load(punks_balances_file)
    with open('data/FARMS.json') as farms_file:
        farms = json.load(farms_file)
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    return render_template("index.html", title="Portfolio tracker", sidx_stats=sidx_stats, sep20_balances=sep20_balances, stacked_assets=stacked_assets, lp_balances=lp_balances, punks=punks, farms=farms)

@app.route('/proposals')
def proposals():
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    page = request.args.get('page', 1, type=int)
    proposals = Proposal.query.order_by(desc(Proposal.id)).paginate(page, app.config['PROPOSALS_PER_PAGE'], False)
    next_url = url_for('proposals', page=proposals.next_num) \
        if proposals.has_next else None
    prev_url = url_for('proposals', page=proposals.prev_num) \
        if proposals.has_prev else None
    return render_template("proposals.html", title="Proposals", proposals=proposals.items, sidx_stats=sidx_stats, next_url=next_url,
                           prev_url=prev_url)

@app.route('/yields', methods=['GET'])
def yields():
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    snapshots_dir = abspath(getcwd()) + "/data/snapshots"
    snapshot_files = [f for f in listdir(snapshots_dir) if isfile(join(snapshots_dir, f))]
    snapshots_dict = {}
    for file in snapshot_files:
        snapshots_dict[file] = str(file.split(".")[0])
    return render_template("yield.html", title="Weekly yield", snapshots=snapshots_dict, sidx_stats=sidx_stats)

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
        return render_template("index.html", title=f"Earnings report at {name}", sidx_stats=sidx_stats,  date=date, sep20_balances=sep20_balances, stacked_assets=stacked_assets, lp_balances=lp_balances, punks=punks, farms=farms)


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
        ABI = open("ERC20-ABI.json", "r")  # Standard ABI for ERC20 tokens
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


@app.route('/submit_proposal')
@login_required
def submit_proposal():
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    print(request)
    return render_template("submit_proposal.html", title="Submit a proposal", sidx_stats=sidx_stats)