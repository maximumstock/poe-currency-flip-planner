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

  # Refactor the double loop
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
