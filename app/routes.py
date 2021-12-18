from app import app
from flask import render_template, url_for, request, send_from_directory
import json
from os import listdir, getcwd
from os.path import isfile, join, abspath
from app.models import Proposal
from sqlalchemy import desc

with open('data/SIDX_STATS.json') as sidx_stats_file:
    sidx_stats = json.load(sidx_stats_file)

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
    return render_template("index.html", title="Portfolio tracker", sidx_stats=sidx_stats, sep20_balances=sep20_balances, stacked_assets=stacked_assets, lp_balances=lp_balances, punks=punks, farms=farms)

@app.route('/proposals')
def proposals():
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
    snapshots_dir = abspath(getcwd()) + "/data/snapshots"
    snapshot_files = [f for f in listdir(snapshots_dir) if isfile(join(snapshots_dir, f))]
    snapshots_dict = {}
    for file in snapshot_files:
        snapshots_dict[file] = str(file.split(".")[0])
    return render_template("yield.html", title="Weekly yield", snapshots=snapshots_dict, sidx_stats=sidx_stats)

@app.route('/yields/<name>', methods=['GET', 'POST'])
def weekly_report(name):
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
