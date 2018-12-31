import pandas as pd
from typing import List, Tuple
import pickle
from functools import reduce
from data_analysis.analysis import find_relevant_currency_hops


leagues = ["hc_delve", "delve", "standard", "hardcore"]


def read_merged_pickle(path):
    with open(path, "rb") as f:
        data = pickle.load(f)
        return data


# Read raw merged pickle file per league
files = ["data_analysis/raw/{}/merge.pickle".format(x) for x in leagues]
raw_data_list = [read_merged_pickle(x) for x in files]


# Map each merged pickle file to the hop data
hop_data = [find_relevant_currency_hops(x, 0) for x in raw_data_list]
hop_groups = [x["groups"] for x in hop_data]


def map_groups_to_dataframe(groups: List[Tuple[str, int]], league: str) -> pd.DataFrame:
    currency_edge = [x[0] for x in groups]
    snapshot_popularity = [x[1] for x in groups]
    return pd.DataFrame({
        "edge": currency_edge,
        "{}".format(league): snapshot_popularity
    })


edge_popularity_dfs = [map_groups_to_dataframe(
    x, leagues[idx]) for idx, x in enumerate(hop_groups)]
final_df = reduce(lambda x, y: pd.merge(x, y, on="edge", how="outer"),
                  edge_popularity_dfs, pd.DataFrame({"edge": []}))
final_df = final_df.set_index("edge")
final_df.to_csv(
    "data_analysis/experiments/edge_popularity_per_snapshot_delve/data/edge_popularity.csv")
