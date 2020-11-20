import logging
import time
from datetime import datetime
from typing import Dict, List
import jsonpickle

from src.config.user_config import UserConfig
from src.core import graph
from src.core.backends.backend_pool import BackendPool
from src.core.offer import Offer
from src.trading import ItemList, build_vendor_offers


def format_conversions(conversions) -> str:
    formatted_conversions = [format_conversion(c) for c in conversions]
    msg = "\n".join(formatted_conversions)
    return msg


def format_conversion(conversion) -> str:
    msg = "{} -> {} -- {} ({} transactions)".format(
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
    def __init__(
        self,
        league,
        item_pairs,
        user_config: UserConfig,
        excluded_traders=[],
    ):
        self.league = league
        self.item_pairs = item_pairs
        self.user_config = user_config
        self.excluded_traders = excluded_traders

        # Internal fields to store partial results
        self.offers: List = []
        self.graph: Dict = {}
        self.results: Dict = {}
        self.timestamp = str(datetime.now()).split(".")[0]

        # Internal fields
        self.item_list = ItemList.load_from_file()
        self.logging = True
        self.backend_pool = BackendPool(self.item_list)

    def prepickle(self) -> str:
        return jsonpickle.encode(
            {
                "timestamp": self.timestamp,
                "league": self.league,
                "item_pairs": self.item_pairs,
                "offers": self.offers,
                "graph": self.graph,
                "results": self.results,
            },
            unpicklable=False,
            indent=2)

    def _filter_traders(self, offers: List[Offer], excluded_traders) -> List:
        excluded_traders = [name.lower() for name in excluded_traders]
        return list(
            filter(lambda x: x.contact_ign.lower() not in excluded_traders,
                   offers))

    def _fetch(self):
        t_start = time.time()

        logging.info("Fetching {} offers for {} pairs".format(
            self.league, len(self.item_pairs)))

        self.offers = self.backend_pool.schedule(self.league, self.item_pairs,
                                                 self.item_list)

        self.offers.extend(build_vendor_offers(self.league))

        # Filter out unwanted traders
        self.offers = self._filter_traders(self.offers, self.excluded_traders)

        t_end = time.time()
        logging.info("Spent {}s fetching offers".format(
            round(t_end - t_start, 2)))

    def _build_graph(self):
        t_start = time.time()
        self.graph = graph.build_graph(self.offers)
        t_end = time.time()

        logging.info("Spent {}s building the graph".format(
            round(t_end - t_start, 2)))

    def _find_profitable_paths(self, max_transaction_length):
        logging.info("Checking for profitable conversions...")
        t_start = time.time()
        for c in self.graph.keys():
            # For currency @c, find all paths within the constructed path that are
            # at most @max_transaction_length long
            paths = graph.find_paths(self.graph, c, c, self.user_config,
                                     max_transaction_length)
            profitable_conversions = []

            for p in paths:
                conversion = graph.build_conversion(p, self.user_config)
                if conversion is not None and conversion["winnings"] > 0:
                    profitable_conversions.append(conversion)

            if self.logging:
                n_profitable = len(profitable_conversions)
                if n_profitable > 0:
                    logging.info("Checking {} -> {} Conversions".format(
                        c, n_profitable))

            profitable_conversions = sorted(profitable_conversions,
                                            key=lambda k: k["winnings"],
                                            reverse=True)

            self.results[c] = profitable_conversions

        t_end = time.time()
        if self.logging:
            logging.info("Spent {}s finding paths".format(
                round(t_end - t_start, 2)))

    def run(self, max_transaction_length=2):
        self._fetch()
        self._build_graph()
        self._find_profitable_paths(max_transaction_length)
