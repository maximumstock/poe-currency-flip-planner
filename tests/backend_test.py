import unittest
import asyncio
import aiohttp

from src.core.backends import poeofficial, poetrade
from src.core.backends.backend_pool import BackendPool
from src.trading.items import ItemList
from src.commons import init_logger

item_list = ItemList.load_from_file()

init_logger(True)


class BackendTest(unittest.TestCase):

    def test_backend_pool(self):

        item_pairs = [("Chaos Orb", "Exalted Orb"), ("Exalted Orb", "Chaos Orb"),
                      ("Chaos Orb", "Orb of Fusing"), ("Orb of Fusing", "Exalted Orb")]
        league = "Standard"
        pool = BackendPool(item_list)
        results = pool.schedule(league, item_pairs, item_list)

        for struct in results:
            assert self.has_key(struct, "offers") is True
            assert len(struct["offers"]) > 0
            assert self.has_key(struct, "want")
            assert self.has_key(struct, "have")
            assert self.has_key(struct, "league")
            assert struct["league"] == league

    def has_key(self, struct, key):
        return key in struct.keys()
