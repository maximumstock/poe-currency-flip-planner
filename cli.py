#!/usr/bin/env python

import argparse
from typing import Union
from commands.pathfinder import execute_pathfinding
from commands.sync import execute_sync

from src.commons import (
    init_logger,
    LEAGUE_NAMES,
    load_excluded_traders,
)
from src.config.user_config import UserConfig
from src.core.backends.poeofficial import PoeOfficial
from src.trading.items import ItemList

parser = argparse.ArgumentParser(description="CLI interface for PathFinder")

parser.add_argument("command",
                    default="pathfinding",
                    choices=["pathfinding", "sync"],
                    type=str,
                    nargs="?",
                    help="Specifies what subcommand to run:\n\n\
    1. pathfinding: Find profitable conversion paths (default).\n\
    2. sync: Sync your public stashes into your config file."),

parser.add_argument(
    "--league",
    default=LEAGUE_NAMES[0],
    type=str,
    help="""
    League specifier, ie. 'Synthesis', 'Hardcore Synthesis' or 'Flashback Event (BRE001)'. 
    Defaults to '{}'.""".format(LEAGUE_NAMES[0]),
)

parser.add_argument(
    "--currency",
    default="all",
    type=str,
    help=
    """Full name of currency to flip, ie. 'Cartographer's Chisel, or 'Chaos Orb'. 
    Defaults to all currencies.""",
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
                    action="store_true",
                    help="Enables debug logging")

parser.add_argument("--config",
                    default=None,
                    type=str,
                    help="Specify your config file path")

arguments = parser.parse_args()
init_logger(arguments.debug)

# global arguments
command: str = arguments.command
league: str = arguments.league
config_file_path: Union[str, None] = arguments.config

# arguments related to pathfinding
currency: Union[str, None] = arguments.currency
limit: Union[int, None] = arguments.limit
fullbulk: bool = arguments.fullbulk
no_filter: bool = arguments.nofilter
config = {"fullbulk": fullbulk}

if command is "pathfinding":
    # Load excluded trader list
    excluded_traders = load_excluded_traders()

    # Load user config
    user_config = UserConfig.from_file(config_file_path)

    # Load item pairs
    item_list = ItemList.load_from_file()
    backend = PoeOfficial(item_list)
    item_pairs = item_list.get_item_list_for_backend(
        backend, config) if no_filter else user_config.get_item_pairs()

    execute_pathfinding(currency, league, limit, item_pairs, user_config,
                        excluded_traders)
elif command is "sync":
    execute_sync()
else:
    raise Exception("Command {} does not exist".format(command))