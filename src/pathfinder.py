from src.graph import *
from src.backends import poeofficial, poetrade
from src.constants import currencies
import itertools



def test():
  trading_currencies = list(currencies.keys())[2:4]
  pf = PathFinder("Incursion", trading_currencies, poeofficial)
  pf.run(3)


def format_conversions(conversions):
  formatted_conversions = [format_conversion(c) for c in conversions]
  msg = "\n".join(formatted_conversions)
  return msg


def format_conversion(conversion):
  msg = "{} -> {} -- {} ({}) ".format(conversion['from'], conversion['to'], conversion['winnings'], len(conversion['transactions']))
  return msg


"""
A simple class to abstract away the internal library functions for fetching
offers, constructing a graph and finding profitable paths along that graph.
"""
class PathFinder:
  def __init__(self, league, currencies, backend):
    self.league = league
    self.currencies = currencies
    self.backend = backend

    self.offers = []
    self.graph = {}
    self.results = {}

  def run(self, max_transaction_length=3):
    currency_combinations = list(itertools.permutations(self.currencies, 2))
    print("Fetching offers for", self.currencies)
    self.offers = self.backend.fetch_offers(self.league, currency_combinations)
    self.graph = build_graph(self.offers)
    print(self.offers)

    for c in self.currencies:
      # For currency @c, find all paths within the constructed path that are
      # at most @max_transaction_length long
      paths = find_paths(self.graph, c, c, max_transaction_length)
      profitable_conversions = []
      for p in paths:
        conversion = build_conversion(p)
        if conversion is not None and conversion['winnings'] > 0:
          profitable_conversions.append(conversion)
      print("Checking {} - {}".format(c, len(profitable_conversions)))
      profitable_conversions = sorted(profitable_conversions, key=lambda k: k['winnings'], reverse=True)
      self.results[c] = profitable_conversions
      if len(profitable_conversions) > 0:
        print(profitable_conversions[0])
      print(format_conversions(profitable_conversions))




if __name__ == '__main__':
  test()
