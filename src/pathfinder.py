import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

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

    def __init__(self,
                 league,
                 item_pairs,
                 backend,
                 excluded_traders=[],
                 use_filter=True):
        self.league = league
        self.item_pairs = item_pairs
        self.backend = backend
        self.excluded_traders = excluded_traders
        self.use_filter = use_filter

        # Private internal fields to store partial results
        self.offers = []
        self.graph = {}
        self.results = {}
        self.timestamp = str(datetime.now()).split(".")[0]
        self.logging = True

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

    def _filter_traders(self, offers: List[Dict], excluded_traders=[]) -> List:
        for idx in range(len(offers)):
            offers[idx]["offers"] = list(
                filter(
                    lambda x: x["contact_ign"] not in excluded_traders,
                    offers[idx]["offers"],
                ))
        return offers

    def _filter_pairs(self, pairs: List[Tuple[str, str]], allowed_pairs: List[str]):
        return [(x.split("-")[0], x.split("-")[1]) for x in allowed_pairs]

    def _fetch(self):
        t_start = time.time()

        # Filter out unwanted item pairs if filtering is enabled
        if self.use_filter is True:
            self.item_pairs = self._filter_pairs(self.item_pairs, self.pair_filter)

        if self.logging:
            print("Fetching {} offers for {} pairs".format(self.league, len(self.item_pairs)))
            print("Filter: {}".format("Enabled" if self.use_filter else "Disabled"))
            print("Backend: {}".format(self.backend.name()))

        self.offers = self.backend.fetch_offers(self.league, self.item_pairs)

        # Filter out unwanted traders
        self.offers = self._filter_traders(self.offers, self.excluded_traders)

        t_end = time.time()

        if self.logging:
            print("Spent {}s fetching offers".format(round(t_end - t_start, 1)))

    def _build_graph(self):
        t_start = time.time()
        self.graph = graph.build_graph(self.offers)
        t_end = time.time()

        if self.logging:
            print("Spent {}s building the graph".format(round(t_end - t_start, 1)))

    def _find_profitable_paths(self, max_transaction_length):
        t_start = time.time()
        for c in self.graph.keys():
            # For currency @c, find all paths within the constructed path that are
            # at most @max_transaction_length long
            paths = graph.find_paths(self.graph, c, c, max_transaction_length)
            profitable_conversions = []

            for p in paths:
                conversion = graph.build_conversion(p)
                if conversion is not None:
                    profitable_conversions.append(conversion)

            if self.logging:
                print("Checking {} -> {} Conversions".format(
                    c, len(profitable_conversions)))

            profitable_conversions = sorted(
                profitable_conversions,
                key=lambda k: k["winnings"],
                reverse=True)

            self.results[c] = profitable_conversions

        t_end = time.time()
        if self.logging:
            print("Spent {}s finding paths".format(round(t_end - t_start, 1)))

    def run(self, max_transaction_length=3, max_amount: Optional[int] = None):
        self._fetch()
        self._build_graph()
        self._find_profitable_paths(max_transaction_length)
