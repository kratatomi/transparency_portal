import json
from datetime import date
import matplotlib.pyplot as plt
from os import listdir, getcwd
from os.path import isfile, join, abspath
from datetime import datetime

def generate_graphs():
    snapshots_dir = abspath(getcwd()) + "/data/snapshots"
    snapshot_files = [f for f in listdir(snapshots_dir) if isfile(join(snapshots_dir, f))]
    # Let's order snapshot files by date
    snapshots_dates = []
    for file in snapshot_files:
        snapshots_dates.append(str(file.split(".")[0]))
    snapshots_dates.sort(key=lambda date: datetime.strptime(date, "%d-%m-%Y"))
    # Now, let's generate a list with the number of weeks and a dict with the assets available
    weeks = []
    assets_list = {}
    value_per_sidx = []
    i = 1
    for file in snapshots_dates:
        weeks.append(i)
        i += 1
        with open(f'data/snapshots/{file}.json') as weekly_report_file:
            weekly_report = json.load(weekly_report_file)
        stacked_assets = weekly_report["STACKED_ASSETS"]
        for asset in stacked_assets:
            if asset != "Total value" and asset != "Total yield value" and asset != 'Celery' and asset not in assets_list:
                assets_list[asset] = {"Yields": [], "USD total value": []}
    # Next, we will populate the assets_list dict with the yield % for every week and current value
    for file in snapshots_dates:
        with open(f'data/snapshots/{file}.json') as weekly_report_file:
            weekly_report = json.load(weekly_report_file)
        stacked_assets = weekly_report["STACKED_ASSETS"]
        for asset in assets_list:
            if asset not in stacked_assets:
                assets_list[asset]["Yields"].append(None)
                assets_list[asset]["USD total value"].append(None)
            else:
                yield_percentage = (stacked_assets[asset]['Yield value'] / stacked_assets[asset]['Current value']) * 100
                assets_list[asset]["Yields"].append(yield_percentage)
                assets_list[asset]["USD total value"].append(stacked_assets[asset]["Current value"])
        if "GLOBAL_STATS" in weekly_report:
            value_per_sidx.append(weekly_report["GLOBAL_STATS"]["value_per_sidx"])
        else:
            value_per_sidx.append(None)
    # Time to plot the yields graph
    fig, ax = plt.subplots()

    ax.set(xlabel='Week',
           ylabel='Yield percentage',
           title='Yield percentage of stacked assets')

    for asset in assets_list:
        ax.plot(weeks, assets_list[asset]["Yields"], label=asset)

    plt.legend()
    plt.savefig("app/static/yields.png")

    # Now, the total value graph
    fig, ax = plt.subplots()

    ax.set(xlabel='Week',
           ylabel='USD value',
           title='Value of stacked assets')

    for asset in assets_list:
        ax.plot(weeks, assets_list[asset]["USD total value"], label=asset)

    plt.legend()
    plt.savefig("app/static/assets_value.png")

    #Finally, the graph showing price per SIDX evolution
    fig, ax = plt.subplots()

    ax.set(xlabel='Week',
           ylabel='USD value per SIDX token',
           title='Value per SIDX token')

    ax.plot(weeks, value_per_sidx)

    plt.savefig("app/static/sidx_value.png")

def main():
    with open('data/SIDX_STATS.json') as sidx_stats_file:
        sidx_stats = json.load(sidx_stats_file)
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
    with open('data/GLOBAL_STATS.json') as global_stats_file:
        global_stats = json.load(global_stats_file)

    today = date.today()
    d1 = today.strftime("%d-%m-%Y")

    weekly_stats = {"snapshot date": d1,
                    "SIDX_STATS": sidx_stats,
                    "SEP20_BALANCES": sep20_balances,
                    "STACKED_ASSETS": stacked_assets,
                    "LP_BALANCES": lp_balances,
                    "EXTRA_LP_BALANCES": extra_lp_balances,
                    "PUNKS_BALANCES": punks,
                    "FARMS": farms,
                    "GLOBAL_STATS": global_stats}

    with open(f'data/snapshots/{d1}.json', 'x') as file:
        json.dump(weekly_stats, file, indent=4)
    file.close()
    generate_graphs()

if __name__ == "__main__":
    main()