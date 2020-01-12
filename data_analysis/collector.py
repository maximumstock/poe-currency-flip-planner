import pickle
import argparse
from datetime import datetime
from src.pathfinder import PathFinder
from src.backends import poeofficial as default_backend
from src.items import build_item_list
from src.commons import league_names


def gen_filename() -> str:
    timestamp = str(datetime.now()).split(".")[0]
    for i in ["-", ":", " "]:
        timestamp = timestamp.replace(i, "_")
    return "{}.pickle".format(timestamp)


def run():

    parser = argparse.ArgumentParser(
        description="data collection tool for PathFinder class")
    parser.add_argument(
        "--league",
        default=league_names[0],
        help=
        "League specifier, ie. 'Synthesis', 'Hardcore Synthesis' or 'Flashback Event (BRE001)'. Defaults to {}".format(league_names[0]),
    )
    parser.add_argument(
        "--path",
        default="data_analysis/raw",
        help="Location where to save collected data",
    )
    parser.add_argument(
        "--fullbulk",
        default=False,
        action="store_true",
        help="Whether to use all supported bulk items",
    )
    parser.add_argument(
        "--nofilter",
        default=False,
        action="store_true",
        help="Whether to disable item pair filters")

    arguments = parser.parse_args()
    league = arguments.league
    path = arguments.path
    use_filter = False if arguments.nofilter else True
    config = {"fullbulk": arguments.fullbulk}
    backend = default_backend
    chosen_currencies = build_item_list(default_backend, config)

    # Load excluded trader list
    with open("excluded_traders.txt", "r") as f:
        excluded_traders = [x.strip() for x in f.readlines()]

    p = PathFinder(league, chosen_currencies, backend, excluded_traders,
                   use_filter)
    p.run(3)

    filename = "{}/{}".format(path, gen_filename())
    with open(filename, "wb") as f:
        data = p.prepickle()
        pickle.dump(data, f)


if __name__ == "__main__":
    run()
