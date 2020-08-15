import os
import operator
import pickle
import argparse

parser = argparse.ArgumentParser(description="Data Converter")
parser.add_argument("--path",
                    nargs="+",
                    help="Folder name of the dumps",
                    required=True)
arguments = parser.parse_args()


def map_filename(folder, filename):
    with open("{}/{}".format(folder, filename), "rb") as f:
        pf = pickle.load(f)
        return pf


for folder in arguments.path:
    print("Merging files for {}".format(folder))
    data = [
        map_filename(folder, x) for x in os.listdir(folder)
        if "pickle" in x and "merge" not in x
    ]
    sorted_data = sorted(data, key=operator.itemgetter("timestamp"))
    with open("{}/merge.pickle".format(folder), "wb") as f:
        pickle.dump(sorted_data, f)
