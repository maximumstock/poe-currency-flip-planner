from src.graph import *
from src.flip import *


leagues = ["Bestiary"]
trading_currencies = list(currencies.keys())
currency_combinations = list(itertools.permutations(trading_currencies, 2))
print("Fetching offers for", trading_currencies)
offers = [fetch_conversion_offers(leagues[0], c1, c2) for (c1, c2) in currency_combinations]

graph = build_graph(offers)
for c in trading_currencies:
  paths = find_paths(graph, c, c, 3)
  profitable_paths = []
  for p in paths:
    cp = calculate_path(p)
    if cp is not None and cp['winnings'] > 0:
      profitable_paths.append(cp)
  print("Checking {} - {}".format(c, len(profitable_paths)))
  for p in profitable_paths:
    print(p['winnings'], p['transactions'])
