from src.graph import *
from src.backends import poeofficial
from src.constants import currencies
import itertools
import time
from datetime import datetime


def test():
  trading_currencies = list(currencies.keys())[:5]
  pf = PathFinder("Delve", trading_currencies, poeofficial)
  pf.run(3)


def format_conversions(conversions):
  formatted_conversions = [format_conversion(c) for c in conversions]
  msg = "\n".join(formatted_conversions)
  return msg


def format_conversion(conversion):
  msg = "{} -> {} -- {} ({} transactions) ".format(conversion['from'], conversion['to'], conversion['winnings'], len(conversion['transactions']))
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

  def prepickle(self):
    return {
      "timestamp": self.timestamp,
      "league": self.league,
      "currencies": self.currencies,
      "offers": self.offers,
      "graph": self.graph,
      "results": self.results
    }

  def run(self, max_transaction_length=3, logging=True):
    self.timestamp = str(datetime.now()).split(".")[0]
    currency_combinations = list(itertools.permutations(self.currencies, 2))
    if len(self.offers) == 0:
      if logging:
        print("Fetching {} offers for {} currencies - {} pairs".format(self.league, len(self.currencies), len(currency_combinations)))
      t0 = time.time()
      self.offers = self.backend.fetch_offers(self.league, currency_combinations)
      t1 = time.time()
      if logging:
        print("Spent {}s fetching offers".format(round(t1 - t0, 1)))
    t1 = time.time()
    self.graph = build_graph(self.offers)
    t2 = time.time()

    if logging:
      print("Spent {}s building the graph".format(round(t2 - t1, 1)))

    for c in self.currencies:
      # For currency @c, find all paths within the constructed path that are
      # at most @max_transaction_length long
      paths = find_paths(self.graph, c, c, max_transaction_length)
      profitable_conversions = []
      for p in paths:
        conversion = build_conversion(p)
        if conversion is not None:
          profitable_conversions.append(conversion)
      if logging:
        print("Checking {} -> {} Conversions".format(c, len(profitable_conversions)))
      profitable_conversions = sorted(profitable_conversions, key=lambda k: k['winnings'], reverse=True)
      self.results[c] = profitable_conversions

    t3 = time.time()
    if logging:
      print("Spent {}s finding paths".format(round(t3 - t2, 1)))


if __name__ == '__main__':
  test()
