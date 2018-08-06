from collections import deque
import math

"""
Builds a simple dictionary graph from found offers in our common format.
An edge can be interpreted as trading from_currency->to_currency.
Each edge contains a list with all offers that were found for that trading
direction between the two currencies.
"""
def build_graph(offers):
  graph = {}

  for cur_pair in offers:
    # if the `have` currency does not exist as a property yet
    if not cur_pair['have'] in graph.keys():
      graph[cur_pair['have']] = {}

    graph[cur_pair['have']][cur_pair['want']] = cur_pair['offers']

  return graph


"""
Returns a list of all possible paths from `want` to `have` for a given graph.
A path is simply a list of transactions between two currency nodes.
"""
def find_paths(graph, have, want, max_length = 3):
  paths = deque()
  correct_paths = []

  # If there are no paths between the specified currencies, simply abort
  if not have in graph:
    return []

  for currency in graph[have]:
    for offer in graph[have][currency]:
      o = decorate_offer(offer, have, currency)
      paths.append([o])

  while len(paths) > 0:
    next = paths.pop()

    if len(next) > max_length:
      continue

    # We have arrived at the target currency
    if next[-1]['want'] == want:
      if is_profitable(next):
        correct_paths = correct_paths + [next]
      continue

    next_currency = next[-1]['want']
    seen_currencies = [edge['have'] for edge in next]

    # If there are no paths between the specified currencies, simply skip
    if next_currency in graph:
      for currency in graph[next_currency]:
        if currency not in seen_currencies[1:]:
          for offer in graph[next_currency][currency]:
            o = decorate_offer(offer, next_currency, currency)
            paths.append(next + [o])

  return correct_paths


def decorate_offer(offer, have, want):
  offer['have'] = have
  offer['want'] = want
  return offer


def maximum_conversion_rate(path):
  v = 1.0
  for e in path:
    v = v*e['conversion_rate']
  return v


def is_profitable(path):
  return maximum_conversion_rate(path) > 1.0


"""
Finds the maximum flow for a found path and alters the conversion edges accordingly.
Also rounds up the trading values to trade for full pieces of currency.
"""
def equalize_stock_differences(path):
  # add some precalculated values
  for edge in path:
    edge['paid'] = math.floor(edge['stock'] / edge['conversion_rate'])
    edge['received'] = math.floor(edge['paid'] * edge['conversion_rate'])

  # need this double loop to make sure that all stock quantity differences
  # per transaction pair are equalized. The worst case for this (starting
  # at the front of the path) is that the limiting transaction is the last one.
  # Therefore, we have to run the inner loop n times to propagate the stock
  # quantity fix towards the front of the path
  for k in range(0, len(path)):
    for i in range(1, len(path)):
      left = path[i-1]
      right = path[i]

      if left['received'] == 0 or left['paid'] == 0 or right['paid'] == 0 or right['received'] == 0:
        return None

      if left['received'] > right['paid']:
        factor = left['received'] / right['paid']
        left['paid'] = math.floor(left['paid'] / factor)
        left['received'] = right['paid']

      if left['received'] < right['paid']:
        factor = right['paid'] / left['received']
        right['received'] = math.floor(right['received'] / factor)
        right['paid'] = left['received']

  return path


"""
Simplifies a found path into a dictionary structure to handle the found data
for easily.
"""
def build_conversion(path):
  transactions = []
  path = equalize_stock_differences(path)

  if path == None:
    return None

  # Map transactions to some nicer format
  for e in path:
    transactions.append({
      "contact_ign": e['contact_ign'],
      "from": e['have'],
      "to": e['want'],
      "paid": e['paid'],
      "received": e['received'],
      "conversion_rate": e['conversion_rate']
    })

  # Filter conversions that do not yield any profit
  if path[-1]['received'] - path[0]['paid'] < 0:
    return None

  return {
    "from": path[0]['have'],
    "to": path[-1]['want'],
    "starting": path[0]['paid'],
    "ending": path[-1]['received'],
    "winnings": path[-1]['received'] - path[0]['paid'],
    "transactions": transactions
  }
