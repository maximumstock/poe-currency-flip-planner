import argparse
import logging
from typing import List, Dict, Any, Set

from src.config.user_config import UserConfig
from src.core.backends.poeofficial import PoeOfficial
from src.pathfinder import PathFinder
from src.commons import league_names, init_logger, load_excluded_traders
from src.trading import ItemList


def log_conversions(conversions, currency, limit):

    unique_conversions = derp(conversions[currency], limit)

    for c in unique_conversions[:limit]:
        log_conversion(c)


def derp(conversions: List[Dict[str, Any]], limit: int) -> List[Dict]:
    seen_traders: Set[str] = set()
    unique_conversions = []

    for conversion in conversions:
        trader_names = [t.contact_ign for t in conversion["transactions"]]
        has_seen_trader = any(
            [True for x in trader_names if x in seen_traders])
        if has_seen_trader:
            continue

        for t in trader_names:
            seen_traders.add(t)

        unique_conversions.append(conversion)

    return unique_conversions


def log_conversion(c):
    logging.info("\t{} {} -> {} {}: {} {}".format(c["starting"], c["from"],
                                                  c["ending"], c["to"],
                                                  c["winnings"], c["to"]))
    for t in c["transactions"]:
        logging.info(
            "\t\t@{} Hi, I'd like to buy your {} {} for {} {} in {}. ({}x)".
            format(
                t.contact_ign,
                t.received,
                t.want,
                t.paid,
                t.have,
                t.league,
                t.conversion_rate,
            ))
    logging.info("\n")


parser = argparse.ArgumentParser(description="CLI interface for PathFinder")

parser.add_argument(
    "--league",
    default=league_names[0],
    type=str,
    help=
    "League specifier, ie. 'Synthesis', 'Hardcore Synthesis' or 'Flashback Event (BRE001)'. Defaults to '{}'."
    .format(league_names[0]),
)
parser.add_argument(
    "--currency",
    default="all",
    # choices=cli_default_items,
    type=str,
    help=
    "Full name of currency to flip, ie. 'Cartographer's Chisel, or 'Chaos Orb'. Defaults to all currencies.",
)
parser.add_argument(
    "--limit",
    default=5,
    type=int,
    help="Limit the number of displayed conversions. Defaults to 5.",
)
parser.add_argument(
    "--fullbulk",
    default=False,
    action="store_true",
    help="Use all supported bulk items",
)
parser.add_argument("--nofilter",
                    default=False,
                    action="store_true",
                    help="Disable item pair filters")
parser.add_argument("--debug",
                    default=False,
                    action="store_true",
                    help="Enables debug logging")

arguments = parser.parse_args()
init_logger(arguments.debug)
item_list = ItemList.load_from_file()
backend = PoeOfficial(item_list)

league = arguments.league
currency = arguments.currency
limit = arguments.limit
fullbulk = arguments.fullbulk
no_filter = arguments.nofilter
config = {"fullbulk": fullbulk}

# Load excluded trader list
excluded_traders = load_excluded_traders()

# Load user config
user_config = UserConfig.from_file()

# Load item pairs
item_pairs = item_list.get_item_list_for_backend(
    backend, config) if no_filter else user_config.get_item_pairs()

p = PathFinder(league, item_pairs, user_config, excluded_traders)
p.run(2)

try:
    logging.info("\n")
    if currency == "all":
        for c in p.graph.keys():
            log_conversions(p.results, c, limit)
    else:
        log_conversions(p.results, currency, limit)

except KeyError:
    logging.warning(
        "Could not find any profitable conversions for {} in {}".format(
            currency, league))
