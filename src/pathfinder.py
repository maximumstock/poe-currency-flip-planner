import time
from datetime import datetime
from typing import Dict, List, Tuple

from src import graph
from src.items import load_pair_filter


def format_conversions(conversions) -> str:
    formatted_conversions = [format_conversion(c) for c in conversions]
    msg = "\n".join(formatted_conversions)
    return msg


def format_conversion(conversion) -> str:
    msg = "{} -> {} -- {} ({} transactions) ".format(
        conversion["from"],
        conversion["to"],
        conversion["winnings"],
        len(conversion["transactions"]),
    )
    return msg


class PathFinder:
    """
    A simple class to abstract away the internal library functions for fetching
    offers, constructing a graph and finding profitable paths along that graph.
    """

    def __init__(self, league, item_pairs, backend, excluded_traders=[], use_filter=True):
        self.league = league
        self.item_pairs = item_pairs
        self.backend = backend
        self.excluded_traders = excluded_traders
        self.use_filter = use_filter

        # Private internal fields to store partial results
        self.offers = []
        self.graph = {}
        self.results = {}

        self.pair_filter = load_pair_filter()

    def prepickle(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "league": self.league,
            "item_pairs": self.item_pairs,
            "offers": self.offers,
            "graph": self.graph,
            "results": self.results,
        }

    def filter_traders(self, offers: List[Dict], excluded_traders=[]) -> List:
        for idx in range(len(offers)):
            offers[idx]["offers"] = list(
                filter(
                    lambda x: x["contact_ign"] not in excluded_traders,
                    offers[idx]["offers"],
                )
            )
        return offers

    def filter_pairs(self, pairs: List[Tuple[str, str]], allowed_pairs: List[str]):
        return [x for x in pairs if "{}-{}".format(x[0], x[1]) in allowed_pairs]

    def run(self, max_transaction_length=3, logging=True):
        self.timestamp = str(datetime.now()).split(".")[0]
        if len(self.offers) == 0:

            # Filter out unwanted item pairs if filtering is enabled
            if self.use_filter is True:
                self.item_pairs = self.filter_pairs(self.item_pairs, self.pair_filter)

            if logging:
                print(
                    "Fetching {} offers for {} pairs".format(
                        self.league, len(self.item_pairs)
                    )
                )
                print("Filter: {}".format("Enabled" if self.use_filter else "Disabled"))
                print("Backend: {}".format(self.backend.name()))
            t0 = time.time()

            self.offers = self.backend.fetch_offers(self.league, self.item_pairs)

            # Filter out unwanted traders
            self.offers = self.filter_traders(self.offers, self.excluded_traders)

            t1 = time.time()
            if logging:
                print("Spent {}s fetching offers".format(round(t1 - t0, 1)))
        t1 = time.time()
        self.graph = graph.build_graph(self.offers)
        t2 = time.time()

        if logging:
            print("Spent {}s building the graph".format(round(t2 - t1, 1)))

        for c in self.graph.keys():
            # For currency @c, find all paths within the constructed path that are
            # at most @max_transaction_length long
            paths = graph.find_paths(self.graph, c, c, max_transaction_length)
            profitable_conversions = []
            for p in paths:
                conversion = graph.build_conversion(p)
                if conversion is not None:
                    profitable_conversions.append(conversion)
            if logging:
                print(
                    "Checking {} -> {} Conversions".format(
                        c, len(profitable_conversions)
                    )
                )
            profitable_conversions = sorted(
                profitable_conversions, key=lambda k: k["winnings"], reverse=True
            )
            self.results[c] = profitable_conversions

        t3 = time.time()
        if logging:
            print("Spent {}s finding paths".format(round(t3 - t2, 1)))
