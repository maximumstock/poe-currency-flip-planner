from src.graph import *
from src.flip import *


leagues = ["Abyss"]
trading_currencies = list(currencies.keys())
currency_combinations = list(itertools.permutations(trading_currencies, 2))
offers = [fetch_conversion_offers(leagues[0], c1, c2) for (c1, c2) in currency_combinations]

graph = build_graph(offers)
for c in trading_currencies:
  print("Checking {}".format(c))
  paths = find_paths(graph, c, c)
  for p in paths:
    rate = maximum_conversion_rate(p)
    if rate > 1.0:
      print("{} league: {} is profitable: {}".format(leagues[0], c, rate))
