from logging import log
import logging
import unittest

from src.config.user_config import UserConfig
from src.core.graph import build_graph, find_paths, build_conversion, is_profitable, calculate_path_length
from src.core.offer import Offer
from src.core.edge import Edge
from src.trading import build_vendor_offers
from typing import List, Dict
from src.config.user_config import DEFAULT_CONFIG_DEFAULT_FILE_PATH

user_config = UserConfig.from_file(DEFAULT_CONFIG_DEFAULT_FILE_PATH)


class GraphVendorTest(unittest.TestCase):
    def test_build_graph(self):
        # Hand-crafted offers to produce a profitable path
        offers_with_vendor = [
            Offer(league="Heist",
                  have="Orb of Regret",
                  want="Chaos Orb",
                  stock=8,
                  conversion_rate=8,
                  contact_ign="some_guy"),
            Offer(league="Heist",
                  have="Orb of Alchemy",
                  want="Orb of Regret",
                  stock=8,
                  conversion_rate=1,
                  contact_ign="__vendor__"),
            Offer(league="Heist",
                  have="Chaos Orb",
                  want="Orb of Alchemy",
                  stock=100,
                  conversion_rate=.25,
                  contact_ign="some_guy"),
        ]
        graph = build_graph(offers_with_vendor)
        paths = find_paths(graph, "Chaos Orb", "Chaos Orb", user_config)
        self.assertTrue(len(paths) > 0)
