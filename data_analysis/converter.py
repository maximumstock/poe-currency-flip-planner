import os
import operator
import pickle
import argparse
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description="Data Converter")
parser.add_argument("--league-folder", default="delve", help="Folder name of the dumps")
arguments = parser.parse_args()

folder = arguments.league_folder

def map_filename(filename):
  with open("data_analysis/raw/{}/{}".format(folder, filename), "rb") as f:
    pf = pickle.load(f)
    return pf

data = [map_filename(x) for x in os.listdir("data_analysis/raw/{}".format(folder)) if "pickle" in x]
sorted_data = sorted(data, key=operator.itemgetter("timestamp"))
with open("data_analysis/{}_conversion.pickle".format(folder), "wb") as f:
  pickle.dump(sorted_data, f)
