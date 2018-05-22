import os
import operator
import pickle
from datetime import datetime, timedelta


def parse_timestamp(filename):
  return (datetime.strptime(filename.split(".")[0], "%Y_%m_%d_%H_%M_%S") - timedelta(hours=2)).isoformat()

def map_filename(filename):
  with open("data_analysis/raw/{}".format(filename), "rb") as f:
    pf = pickle.load(f)
    return {
      "created_at": parse_timestamp(filename),
      "graph": pf.graph,
      "offers": pf.offers,
      "results": pf.results,
      "currencies": pf.currencies
    }


data = [map_filename(x) for x in os.listdir("data_analysis/raw") if "pickle" in x]
sorted_data = sorted(data, key=operator.itemgetter("created_at"))
with open("data_analysis/conversion.pickle", "wb") as f:
  pickle.dump(sorted_data, f)
