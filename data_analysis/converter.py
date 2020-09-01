import os
import operator
import pickle
import argparse
import json
from datetime import datetime

parser = argparse.ArgumentParser(description="Data Converter")
parser.add_argument("--path",
                    nargs="+",
                    help="Folder name of the dumps",
                    required=True)

arguments = parser.parse_args()


def load_pickle(folder, filename):
    try:
        with open("{}/{}".format(folder, filename), "rb") as f:
            return pickle.load(f)
    except EOFError:
        return None


def load_json(folder, filename):
    try:
        with open("{}/{}".format(folder, filename), "r") as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        return None


def utc_ts_from_filename(filename: str) -> str:
    dt = datetime.strptime(filename.split(".")[0], "%Y_%m_%d_%H_%M_%S")
    return str(dt)


def load_pickle_incursion(folder, filename):
    """
    PathFinder did not have a `timestamp` attribute back in Incursion, so
    we have to manually parse it from the filename.
    """
    try:
        with open("{}/{}".format(folder, filename), "rb") as f:
            pathfinder_obj = pickle.load(f)
            return {
                "graph": pathfinder_obj.graph,
                "offers": pathfinder_obj.offers,
                "league": pathfinder_obj.league,
                "results": pathfinder_obj.results,
                "timestamp": utc_ts_from_filename(filename)
            }
            return pathfinder_obj
    except EOFError:
        return None


for folder in arguments.path:
    print("Merging files for {}".format(folder))

    file_names = [x for x in os.listdir(folder) if "merge" not in x]
    json_files = [x for x in file_names if "json" in x]
    pickle_files = [x for x in file_names if "pickle" in x]

    json_data = [load_json(folder, x) for x in json_files]

    if "Incursion" in folder:
        pickle_data = [load_pickle_incursion(folder, x) for x in pickle_files]
    else:
        pickle_data = [load_pickle(folder, x) for x in pickle_files]

    print("\tFound {} .json and {} .pickle".format(len(json_data),
                                                   len(pickle_data)))

    filtered_data = [x for x in json_data + pickle_data if x is not None]

    sorted_data = sorted(filtered_data, key=operator.itemgetter("timestamp"))

    with open("{}/merge.json".format(folder), "w") as f:
        json.dump(sorted_data, f)
        print("\tDumped {} elements".format(len(sorted_data)))
