import json
from datetime import date

def main():
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


    today = date.today()
    d1 = today.strftime("%d-%m-%Y")

    weekly_stats = {"snapshot date": d1,
                    "SIDX_STATS": sidx_stats,
                    "SEP20_BALANCES": sep20_balances,
                    "STACKED_ASSETS": stacked_assets,
                    "LP_BALANCES": lp_balances,
                    "PUNKS_BALANCES": punks}

    with open(f'data/snapshots/{d1}.json', 'x') as file:
        json.dump(weekly_stats, file, indent=4)
    file.close()

if __name__ == "__main__":
    main()