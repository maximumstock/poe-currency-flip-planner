from src.graph import *
from src.flip import *


leagues = ["Abyss"]
trading_currencies = list(currencies.keys())
currency_combinations = list(itertools.permutations(trading_currencies, 2))
print("Fetching offers for", trading_currencies)
offers = [fetch_conversion_offers(leagues[0], c1, c2) for (c1, c2) in currency_combinations]

graph = build_graph(offers)
for c in trading_currencies:
  print("Checking {}".format(c))
  paths = find_paths(graph, c, c)
  for p in paths:
    cp = calculate_path(p)
    if cp['winnings'] > 0:
      print(cp['transactions'])
