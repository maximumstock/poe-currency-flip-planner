from collections import deque

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
"""
def find_paths(graph, have, want, max_length = 5):
  paths = deque()
  correct_paths = []

  for currency in graph[have]:
    for offer in graph[have][currency]:
      o = decorate_offer(offer, have, currency)
      paths.append([o])

  while len(paths) > 0:
    next = paths.pop()

    if len(next) > max_length:
      continue

    if next[-1]['want'] == want:
      correct_paths = correct_paths + [next]
      continue

    next_currency = next[-1]['want']
    seen_currencies = [edge['have'] for edge in next]
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

def calculate_path(path):
  transactions = []

  starting_amount = int(path[0]['stock'] / path[0]['conversion_rate'])
  transactions.append({
    "from": path[0]['have'],
    "to": path[0]['want'],
    "paid": starting_amount,
    "received": int(starting_amount * path[0]['conversion_rate'])
  })

  for i in range(1,len(path)):
    last = path[i-1]
    v = int(transactions[i-1]['received'] / path[i]['conversion_rate'])
    transactions.append({
      "from": path[i]['have'],
      "to": path[i]['want'],
      "paid": transactions[i-1]['received'],
      "received": int(transactions[i-1]['received'] * path[i]['conversion_rate'])
    })

  return {
    "from": path[0]['have'],
    "to": path[-1]['want'],
    "starting": transactions[0]['paid'],
    "ending": transactions[-1]['received'],
    "winnings": transactions[-1]['received'] - transactions[0]['paid'],
    "transactions": transactions
  }
