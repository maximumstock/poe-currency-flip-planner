import unittest

from src.config.user_config import UserConfig
from src.core.graph import build_graph, find_paths, build_conversion, is_profitable, calculate_path_length
from src.core.offer import Offer
from src.core.edge import Edge
from src.trading import build_vendor_offers
from typing import List, Dict

user_config = UserConfig.from_file()


class GraphVendorTest(unittest.TestCase):
    def test_build_graph(self):
        offers_with_vendor = [
            Offer(league="Heist",
                  have="Chaos Orb",
                  want="Orbs of Regret",
                  stock=8,
                  conversion_rate=8,
                  contact_ign="some_guy"),
            Offer(league="Heist",
                  have="Orbs of Regret",
                  want="Orb of Alchemy",
                  stock=8,
                  conversion_rate=1,
                  contact_ign="__vendor__"),
            Offer(league="Heist",
                  have="Chaos Orb",
                  want="Orbs of Regret",
                  stock=8,
                  conversion_rate=8,
                  contact_ign="some_guy"),
            Offer(league="Heist",
                  have="Chaos Orb",
                  want="Orbs of Regret",
                  stock=8,
                  conversion_rate=8,
                  contact_ign="some_guy"),
        ]
        graph = build_graph(offers_with_vendor)
        paths = find_paths(graph, "Chaos", "Chaos", user_config)
