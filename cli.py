import argparse

from src.pathfinder import PathFinder
from src.backends import poeofficial
from src.backends import poetrade
from src.items import build_item_list, load_items


currency_items = [x["name"] for x in load_items(
    "poetrade").values() if x["currency"] is True]

league_names = [
    "Betrayal",
    "Hardcore Betrayal",
    "Standard",
    "Hardcore"
]


def log_conversions(conversions, currency, limit):
    for c in conversions[currency][:limit]:
        log_conversion(c)


def log_conversion(c):
    print("{} {} -> {} {}: {} {}".format(c['starting'],
                                         c['from'], c['ending'], c['to'], c['winnings'], c['to']))
    for t in c['transactions']:
        print("\t@{} Hi, I'd like to buy your {} {} for {} {}. ({})".format(
            t['contact_ign'], t['received'], t['to'], t['paid'], t['from'], t['conversion_rate']))
    print("\n")


parser = argparse.ArgumentParser(description="CLI interface for PathFinder")
parser.add_argument("--league", default="Betrayal", choices=league_names, type=str,
                    help="League specifier, ie. 'Betrayal', 'Hardcore Betrayal' or 'Flashback Event (BRE001)'. Defaults to 'Betrayal'.")
parser.add_argument("--currency", default="all", choices=currency_items, type=str,
                    help="Full name of currency to flip, ie. 'Cartographer\'s Chisel, or 'Chaos Orb'. See a full list of currency names under src/constants.py. Defaults to all currencies.")
parser.add_argument("--limit", default=3, type=int,
                    help="Limit the number of displayed conversions. Defaults to 3.")
parser.add_argument("--poetrade", default=False, action="store_true",
                    help="Flag to fetch trading data from poe.trade instead of pathofexile.com/trade.")
arguments = parser.parse_args()

league = arguments.league
currency = arguments.currency
limit = arguments.limit
use_poetrade = arguments.poetrade

backend = poetrade if use_poetrade else poeofficial

if use_poetrade is True:
    chosen_currencies = build_item_list("poetrade", {})
else:
    chosen_currencies = build_item_list("poeofficial", {})

p = PathFinder(league, chosen_currencies, backend)
p.run(3, True)

try:
    if currency == "all":
        for c in p.graph.keys():
            log_conversions(p.results, c, limit)
    else:
        log_conversions(p.results, currency, limit)

except KeyError:
    print("Could not find any proftiable conversions for {} in {}".format(
        currency, league))
