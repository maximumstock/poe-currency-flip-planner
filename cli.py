import argparse
from src.backends import poetrade, poeofficial
from src.items import build_item_list, load_items
from src.pathfinder import PathFinder
from src.commons import league_names

default_backend = poeofficial
cli_default_items = [
    x["name"] for x in load_items(default_backend).values() if x["currency"] is True
]


def log_conversions(conversions, league, currency, limit):
    for c in conversions[currency][:limit]:
        log_conversion(c, league)


def log_conversion(c, league):
    print("{} {} -> {} {}: {} {}".format(c["starting"], c["from"], c["ending"],
                                         c["to"], c["winnings"], c["to"]))
    for t in c["transactions"]:
        print("\t@{} Hi, I'd like to buy your {} {} for {} {} in {}. ({}x)".format(
            t["contact_ign"],
            t["received"],
            t["to"],
            t["paid"],
            t["from"],
            league,
            t["conversion_rate"],
        ))
    print("\n")


parser = argparse.ArgumentParser(description="CLI interface for PathFinder")

parser.add_argument(
    "--league",
    default=league_names[0],
    type=str,
    help="League specifier, ie. 'Synthesis', 'Hardcore Synthesis' or 'Flashback Event (BRE001)'. Defaults to '{}'.".format(
        league_names[0]),
)
parser.add_argument(
    "--currency",
    default="all",
    choices=cli_default_items,
    type=str,
    help="Full name of currency to flip, ie. 'Cartographer's Chisel, or 'Chaos Orb'. Defaults to all currencies.",
)
parser.add_argument(
    "--limit",
    default=3,
    type=int,
    help="Limit the number of displayed conversions. Defaults to 3.",
)
parser.add_argument(
    "--fullbulk",
    default=False,
    action="store_true",
    help="Use all supported bulk items",
)
parser.add_argument(
    "--nofilter",
    default=False,
    action="store_true",
    help="Disable item pair filters")
parser.add_argument(
    "--poetrade",
    default=False,
    action="store_true",
    help="Use poe.trade instead of pathofexile.com/trade")

arguments = parser.parse_args()
league = arguments.league
currency = arguments.currency
limit = arguments.limit
fullbulk = arguments.fullbulk
use_filter = False if arguments.nofilter else True
backend = poetrade if arguments.poetrade else poeofficial
config = {"fullbulk": fullbulk}
chosen_currencies = build_item_list(backend, config)

# Load excluded trader list
with open("excluded_traders.txt", "r") as f:
    excluded_traders = [x.strip() for x in f.readlines()]

p = PathFinder(league, chosen_currencies, backend, excluded_traders,
               use_filter)
p.run(3, True)

try:
    if currency == "all":
        for c in p.graph.keys():
            log_conversions(p.results, league, c, limit)
    else:
        log_conversions(p.results, league, currency, limit)

except KeyError:
    print("Could not find any profitable conversions for {} in {}".format(
        currency, league))
