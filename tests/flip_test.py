import unittest
from src.flip import fetch_conversion_offers


class FlipTest(unittest.TestCase):
  def test_fetch_conversion_offers(self):
    league = "Abyss"
    want = "Chaos"
    have = "Chromatic"
    offers = fetch_conversion_offers(league, want, have)
    assert ("offers" in offers.keys()) == True
    assert offers["want"] == want
    assert offers["have"] == have
    assert offers["league"] == league
