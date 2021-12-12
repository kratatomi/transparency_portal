from app import app
from flask import render_template, url_for
import json
from os import listdir, getcwd
from os.path import isfile, join, abspath

@app.route('/')
@app.route('/index')
def index():
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    with open('data/SEP20_BALANCES.json') as sep20_balances_file:
        sep20_balances = json.load(sep20_balances_file)
    with open('data/STACKED_ASSETS.json') as stacked_assets_file:
        stacked_assets = json.load(stacked_assets_file)
    with open('data/LP_BALANCES.json') as lp_balances_file:
        lp_balances = json.load(lp_balances_file)
    with open('data/PUNKS_BALANCES.json') as punks_balances_file:
        punks = json.load(punks_balances_file)
    return render_template("index.html", title="Portfolio tracker", sidx_stats=sidx_stats, sep20_balances=sep20_balances, stacked_assets=stacked_assets, lp_balances=lp_balances,punks=punks)

@app.route('/proposals')
def proposals():
    with open('data/VOTES.json') as votes_file:
        votes = json.load(votes_file)
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
    return render_template("proposals.html", title="Proposals", proposals=votes["proposals"], sidx_stats=sidx_stats)

@app.route('/yield')
def yield_page():
    snapshots_dir = abspath(getcwd()) + "/data/snapshots"
    snapshot_files = [f for f in listdir(snapshots_dir) if isfile(join(snapshots_dir, f))]
    snapshots_dict = {}
    for file in snapshot_files:
        snapshots_dict[file] = file.split(".")[0]
