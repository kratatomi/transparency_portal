import json
from datetime import date
import matplotlib.pyplot as plt
from os import listdir, getcwd
from os.path import isfile, join, abspath
from datetime import datetime
import logging

logger = logging.getLogger("app.engine")
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
            if asset != "Total value" and asset != "Total yield value" and asset not in assets_list:
                assets_list[asset] = {"Yields": [], "USD total value": [], "Weeks tracked": 0}
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
                assets_list[asset]["Weeks tracked"] += 1
        if "GLOBAL_STATS" in weekly_report:
            value_per_sidx.append(weekly_report["GLOBAL_STATS"]["value_per_sidx"])
        else:
            value_per_sidx.append(None)
    # Time to plot the yields graph
    fig, ax = plt.subplots()

    ax.set(xlabel='Week',
           ylabel='Yield percentage',
           title='Yield percentage of staked assets')

    for asset in assets_list:
        ax.plot(weeks, assets_list[asset]["Yields"], label=asset)

    plt.legend()
    plt.savefig("app/static/yields.png")

    # Now, the total value graph
    fig, ax = plt.subplots()

    ax.set(xlabel='Week',
           ylabel='USD value',
           title='Value of staked assets')

    for asset in assets_list:
        ax.plot(weeks, assets_list[asset]["USD total value"], label=asset)

    plt.legend()
    plt.savefig("app/static/assets_value.png")

    #The graph showing price per SIDX evolution:
    fig, ax = plt.subplots()

    ax.set(xlabel='Week',
           ylabel='USD value per SIDX token',
           title='Value per SIDX token')

    ax.plot(weeks, value_per_sidx)

    plt.savefig("app/static/sidx_value.png")

    #Finally, a graph with the APY of every asset
    columns = [] #List of assets
    rows = [] #List of APYs
    for asset in assets_list:
        columns.append(asset)
        yield_percentage_sum = sum(filter(None, assets_list[asset]["Yields"]))
        rows.append(yield_percentage_sum * (52 / assets_list[asset]["Weeks tracked"])) #52 weeks per year

    '''Broken axis method extracted from https://matplotlib.org/3.1.0/gallery/subplots_axes_and_figures/broken_axis.html'''
    f, (ax, ax2) = plt.subplots(2, 1, sharex=True, figsize=(16, 9))
    ax.bar(columns, rows, color='maroon', width=0.4)
    ax2.bar(columns, rows, color='maroon', width=0.4)
    ax.set_ylim(200, 600)
    ax2.set_ylim(0, 100)
    ax.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax.xaxis.tick_top()
    ax.tick_params(labeltop=False)  # don't put tick labels at the top
    ax2.xaxis.tick_bottom()
    ax.set(xlabel='Asset',
           ylabel='Estimated APY',
           title='Estimated APY of staked assets in the portfolio')

    ax.grid(visible=True, color='grey',
            linestyle='-.', linewidth=0.5,
            alpha=0.2)

    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((-d, +d), (-d, +d), **kwargs)  # top-left diagonal
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal
    plt.savefig("app/static/assets_apy.png")

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
    #Let's harvest the rewards from pools
    import engine
    engine.start_celery_stake() # Turning to staking mode harvest the CLY rewards
    for asset in stacked_assets:
        if isinstance(stacked_assets[asset], dict): # Don't grab Total value and Total yield value entries
            engine.harvest_pools_rewards(asset, amount=stacked_assets[asset]["Yield"] * 10**18)

    try:
        engine.harvest_farms_rewards()
    except Exception as e:
        logger.error(f'Function harvest_farms_rewards failed. Exception: {e}')
        import app.email as email
        email.send_email_to_admin(f'Function harvest_farms_rewards failed. Exception: {e}')
    else:
        # We have to take the profits from the BCH/bcBCH and flexUSD/BCH farms and swap them for bcUSDT (proposal #42)
        amount_to_swap = 0
        for farm in farms["Mistswap"]["farms"]:
            if farm["pool_id"] in (1, 60):
                amount_to_swap += farm["reward"]

        amount_to_swap = amount_to_swap * 10 ** 18
        engine.swap_assets("0x5fA664f69c2A4A3ec94FaC3cBf7049BD9CA73129", "0xBc2F884680c95A02cea099dA2F524b366d9028Ba",
                           amount_to_swap)
    try:
        engine.harvest_tango_sidx_farm(engine.punk_wallets[1], 'SECOND_WALLET_PRIV_KEY')
    except Exception as e:
        logger.error(f'Function harvest_tango_sidx_farm failed. Exception: {e}')
        import app.email as email
        email.send_email_to_admin(f'Function harvest_tango_sidx_farm failed. Exception: {e}')

    try:
        engine.harvest_sidx_ember_farm(engine.punk_wallets[1], 'SECOND_WALLET_PRIV_KEY')
    except Exception as e:
        logger.error(f'Function harvest_sidx_ember_farm failed. Exception: {e}')
        import app.email as email
        email.send_email_to_admin(f'Function harvest_sidx_ember_farm failed. Exception: {e}')


if __name__ == "__main__":
    main()