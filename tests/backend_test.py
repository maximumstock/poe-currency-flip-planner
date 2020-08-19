import unittest
from typing import List

from src.commons import init_logger
from src.core.backends.backend_pool import BackendPool
from src.core.offer import Offer
from src.trading.items import ItemList

item_list = ItemList.load_from_file()
init_logger(True)


class BackendTest(unittest.TestCase):
    def test_backend_pool(self):

        item_pairs = [("Chaos Orb", "Exalted Orb"),
                      ("Exalted Orb", "Chaos Orb"),
                      ("Chaos Orb", "Orb of Fusing"),
                      ("Orb of Fusing", "Exalted Orb")]
        league = "Standard"
        pool = BackendPool(item_list)
        offers: List[Offer] = pool.schedule(league, item_pairs, item_list)

        assert len(offers) > 0

        for offer in offers:
            assert hasattr(offer, "want")
            assert hasattr(offer, "have")
            assert hasattr(offer, "league")
            assert hasattr(offer, "contact_ign")
            assert hasattr(offer, "conversion_rate")
            assert hasattr(offer, "stock")
            assert offer.league == league

    def has_key(self, struct, key):
        return key in struct.keys()
