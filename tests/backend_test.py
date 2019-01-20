import unittest
from src.backends import poeofficial, poetrade
from src.constants import currencies


class BackendTest(unittest.TestCase):

    def test_currency_mappings(self):
        for key in currencies.keys():
            assert (poeofficial.map_currency(key) is not None)
            assert (poetrade.map_currency(key) is not None)

    def test_fetch_offers(self):
        league = "Standard"
        want = "Chaos Orb"
        have = "Chromatic Orb"

        poe_official_many = poeofficial.fetch_offers(league, [(want, have)])
        poe_trade_single = poetrade.fetch_offers_for_pair(league, want, have)
        poe_trade_many = poetrade.fetch_offers(league, [(want, have)])

        for struct in (poe_official_many + [poe_trade_single] + poe_trade_many):
            assert ("offers" in struct.keys()) is True
            assert len(struct["offers"]) > 0
            assert struct["want"] == want
            assert struct["have"] == have
            assert struct["league"] == league
