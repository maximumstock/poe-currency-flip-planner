import pickle
import argparse
from datetime import datetime
from src.pathfinder import PathFinder
from src.constants import currencies
from src.backends import poeofficial


def gen_filename():
    timestamp = str(datetime.now()).split(".")[0]
    for i in ["-", ":", " "]:
        timestamp = timestamp.replace(i, "_")
    return "{}.pickle".format(timestamp)


def run():

    parser = argparse.ArgumentParser(
        description="data collection tool for PathFinder class")
    parser.add_argument("--league", default="Delve",
                        help="League specifier, ie. 'Bestiary', 'Hardcore Bestiary' or 'Flashback Event (BRE001)'")
    parser.add_argument("--path", default="data_analysis/raw",
                        help="Location where to save collected data")
    arguments = parser.parse_args()

    p = PathFinder(arguments.league, currencies, poeofficial)
    p.run(3)

    filename = "{}/{}".format(arguments.path, gen_filename())
    with open(filename, "wb") as f:
        data = p.prepickle()
        pickle.dump(data, f)


if __name__ == "__main__":
    run()
