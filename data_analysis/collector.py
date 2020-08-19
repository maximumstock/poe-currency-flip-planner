import argparse
from datetime import datetime
from src.pathfinder import PathFinder
from src.core.backends.poetrade import PoeTrade
from src.commons import league_names, init_logger
from src.config.user_config import UserConfig
from src.trading.items import ItemList
from dataclasses import dataclass


@dataclass
class CollectorConfig:
    league: str
    path: str
    fullbulk: bool
    use_filter: bool


def gen_filename() -> str:
    timestamp = str(datetime.now()).split(".")[0]
    for i in ["-", ":", " "]:
        timestamp = timestamp.replace(i, "_")
    return "{}.json".format(timestamp)


def parse_args() -> CollectorConfig:
    parser = argparse.ArgumentParser(
        description="data collection tool for PathFinder class")
    parser.add_argument(
        "--league",
        default=league_names[0],
        help=
        "League specifier, ie. 'Synthesis', 'Hardcore Synthesis' or 'Flashback Event (BRE001)'. Defaults to {}"
        .format(league_names[0]),
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
    parser.add_argument("--nofilter",
                        default=False,
                        action="store_true",
                        help="Whether to disable item pair filters")

    arguments = parser.parse_args()

    return CollectorConfig(league=arguments.league,
                           path=arguments.path,
                           fullbulk=arguments.fullbulk,
                           use_filter=False if arguments.nofilter else True)


class Collector:
    def run(self):
        params = parse_args()
        # Generate file name at the start, so it indicates when the collection started
        filename = "{}/{}".format(params.path, gen_filename())

        item_list = ItemList.load_from_file()
        user_config = UserConfig.from_file()
        # By default,
        default_backend = PoeTrade(item_list)

        item_pairs = user_config.get_item_pairs(
        ) if params.use_filter else item_list.get_item_list_for_backend(
            default_backend, {"fullbulk": params.fullbulk})

        p = PathFinder(params.league, item_pairs, user_config)
        p.run(2)

        with open(filename, "w") as f:
            data = p.prepickle()
            f.write(data)


if __name__ == "__main__":
    init_logger(True)
    (Collector()).run()
