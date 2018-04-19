import unittest
from src.flip import fetch_conversion_offers, parallel_fetch_conversion_offers


class FlipTest(unittest.TestCase):
  def test_fetch_conversion_offers(self):
    league = "Abyss"
    want = "Chaos"
    have = "Chromatic"
    offers = fetch_conversion_offers(league, want, have)
    parallel_offers = parallel_fetch_conversion_offers(league, [(want, have)])

    for struct in [offers, parallel_offers[0]]:
      assert ("offers" in struct.keys()) == True
      assert struct["want"] == want
      assert struct["have"] == have
      assert struct["league"] == league
