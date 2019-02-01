import os
import operator
import pickle
import argparse

parser = argparse.ArgumentParser(description="Data Converter")
parser.add_argument(
    "--path", default="data_analysis/raw/delve", help="Folder name of the dumps"
)
arguments = parser.parse_args()

folder = arguments.path


def map_filename(filename):
    with open("{}/{}".format(folder, filename), "rb") as f:
        pf = pickle.load(f)
        return pf


data = [
    map_filename(x) for x in os.listdir(folder) if "pickle" in x and "merge" not in x
]
sorted_data = sorted(data, key=operator.itemgetter("timestamp"))
with open("{}/merge.pickle".format(folder), "wb") as f:
    pickle.dump(sorted_data, f)
