#!/usr/bin/env python
import argparse
import logging

from src.commons import (init_logger, LEAGUE_NAMES, load_excluded_traders,
                         unique_conversions_by_trader_name)
from src.config.user_config import UserConfig
from src.core.backends.poeofficial import PoeOfficial
from src.pathfinder import PathFinder
from src.trading.items import ItemList


def log_conversions(conversions, limit):
    for c in conversions[:limit]:
        log_conversion(c)


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
    default=LEAGUE_NAMES[0],
    type=str,
    help=
    "League specifier, ie. 'Synthesis', 'Hardcore Synthesis' or 'Flashback Event (BRE001)'. Defaults to '{}'."
    .format(LEAGUE_NAMES[0]),
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
                    default=None,
                    action="store_true",
                    help="Enables debug logging")
parser.add_argument("--config",
                    default=None,
                    type=str,
                    help="Specify your config file path")

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
config_file_path = arguments.config

# Load excluded trader list
excluded_traders = load_excluded_traders()

# Load user config
user_config = UserConfig.from_file(config_file_path)

# Load item pairs
item_pairs = item_list.get_item_list_for_backend(
    backend, config) if no_filter else user_config.get_item_pairs()

p = PathFinder(league, item_pairs, user_config, excluded_traders)
p.run(2)

try:
    logging.info("\n")
    if currency == "all":
        for c in p.graph.keys():
            conversions = unique_conversions_by_trader_name(p.results[c])
            log_conversions(conversions, limit)
    else:
        conversions = unique_conversions_by_trader_name(p.results[currency])
        log_conversions(conversions, limit)

except KeyError:
    logging.warning(
        "Could not find any profitable conversions for {} in {}".format(
            currency, league))
