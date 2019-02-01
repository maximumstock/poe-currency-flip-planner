import pickle
import argparse
from datetime import datetime
from src.pathfinder import PathFinder
from src.backends import poetrade, poeofficial
from src.items import build_item_list


def gen_filename() -> str:
    timestamp = str(datetime.now()).split(".")[0]
    for i in ["-", ":", " "]:
        timestamp = timestamp.replace(i, "_")
    return "{}.pickle".format(timestamp)


def run():

    parser = argparse.ArgumentParser(
        description="data collection tool for PathFinder class"
    )
    parser.add_argument(
        "--league",
        default="Betrayal",
        choices=["Betrayal", "Hardcore Betrayal", "Standard", "Hardcore"],
        help="League specifier, ie. 'Betrayal', 'Hardcore Betrayal' or 'Flashback Event (BRE001)'",
    )
    parser.add_argument(
        "--path",
        default="data_analysis/raw",
        help="Location where to save collected data",
    )
    parser.add_argument(
        "--poetrade",
        default=False,
        action="store_true",
        help="Flag to fetch trading data from poe.trade instead of pathofexile.com/trade.",
    )
    parser.add_argument(
        "--fullbulk",
        default=False,
        action="store_true",
        help="Whether to use all supported bulk items",
    )

    arguments = parser.parse_args()

    league = arguments.league
    path = arguments.path
    use_poetrade = arguments.poetrade
    fullbulk = arguments.fullbulk

    backend = poetrade if use_poetrade else poeofficial

    if use_poetrade is True:
        chosen_currencies = build_item_list("poetrade", fullbulk)
    else:
        chosen_currencies = build_item_list("poeofficial", fullbulk)

    p = PathFinder(league, chosen_currencies, backend)
    p.run(3)

    filename = "{}/{}".format(path, gen_filename())
    with open(filename, "wb") as f:
        data = p.prepickle()
        pickle.dump(data, f)


if __name__ == "__main__":
    run()
