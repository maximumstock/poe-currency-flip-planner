import math
from collections import deque
from typing import Dict, List, Optional
import copy

from src.config.user_config import UserConfig
from src.core.offer import Offer
from src.core.edge import Edge


def build_graph(offers: List[Offer]) -> Dict[str, Dict[str, List[Offer]]]:
    """
    Builds a simple dictionary graph from found offers in our common format.
    An edge can be interpreted as trading from_currency->to_currency.
    Each edge contains a list with all offers that were found for that trading
    direction between the two currencies.
    """
    graph: Dict[str, Dict[str, List[Offer]]] = dict()

    for offer in offers:
        if offer.have not in graph.keys():
            graph[offer.have] = dict()

        if offer.want not in graph[offer.have].keys():
            graph[offer.have][offer.want] = list()

        graph[offer.have][offer.want].append(copy.copy(offer))

    return graph


def find_paths(graph: Dict[str, Dict[str, List[Offer]]],
               have: str,
               want: str,
               user_config: UserConfig,
               max_length: int = 3) -> List:
    """
    Returns a list of all possible paths from `want` to `have` for a given graph.
    A path is simply a list of transactions between two currency nodes.
    """
    paths: deque = deque()
    correct_paths: List[List[Dict]] = []

    # If there are no paths between the specified currencies, simply abort
    if have not in graph:
        return []

    for currency in graph[have]:
        for offer in graph[have][currency]:
            paths.append([offer])

    while len(paths) > 0:
        next: List[Offer] = paths.pop()

        if len(next) > max_length:
            continue

        # If a path contains an edge with a stock outside of the user-specified boundaries, prune it
        for edge in next:
            (minimum,
             maximum) = user_config.get_stock_boundaries(edge.have, edge.want)
            if edge.stock < minimum or edge.stock > maximum:
                continue

        # We have arrived at the target currency
        if next[-1].want == want:
            if is_profitable(next):
                correct_paths.append(next)
            continue

        next_currency = next[-1].want
        seen_currencies = [edge.have for edge in next]

        # If there are no paths between the specified currencies, simply skip
        if next_currency in graph:
            for currency in graph[next_currency]:
                if max_length == len(next) + 1 and currency != have:
                    continue

                if currency not in seen_currencies[1:]:
                    for offer in graph[next_currency][currency]:
                        paths.append(next + [offer])

    return correct_paths


def maximum_conversion_rate(path: List[Offer]):
    v = 1.0
    for e in path:
        v = v * e.conversion_rate
    return v


def is_profitable(path: List[Dict]):
    return maximum_conversion_rate(path) > 1.0


def equalize_stock_differences(path: List[Offer],
                               user_config: UserConfig) -> List[Edge]:
    """
    Finds the maximum flow for a found path and alters the conversion edges accordingly.
    Also rounds up the trading values to trade for full pieces of currency.
    """

    edges: List[Edge] = [Edge(offer, 1, 1) for offer in path]

    # Limit the first transaction's volume based on maximum trading volume
    first_edge = edges[0]
    sell_trading_cap = user_config.get_maximum_trade_volume_for_item(
        first_edge.have)
    buy_trading_cap = math.floor(first_edge.conversion_rate * sell_trading_cap)
    first_edge.stock = min(first_edge.stock, buy_trading_cap)

    # add some precalculated values
    for idx, edge in enumerate(edges):
        edge.paid = math.floor(edge.stock / edge.conversion_rate)
        edge.received = math.floor(edge.paid * edge.conversion_rate)

    # need this double loop to make sure that all stock quantity differences
    # per transaction pair are equalized. The worst case for this (starting
    # at the front of the path) is that the limiting transaction is the last one.
    # Therefore, we have to run the inner loop n times to propagate the stock
    # quantity fix towards the front of the path
    for k in range(0, len(edges)):
        for i in range(1, len(edges)):
            left = edges[i - 1]
            right = edges[i]

            if (left.received == 0 or left.paid == 0 or right.paid == 0
                    or right.received == 0):
                return []

            if left.received > right.paid:
                factor = left.received / right.paid
                left.paid = math.ceil(left.paid / factor)
                left.received = right.paid

            if left.received < right.paid:
                factor = right.paid / left.received
                right.received = math.floor(right.received / factor)
                right.paid = left.received

    return edges


def build_conversion(path: List[Offer],
                     user_config: UserConfig) -> Optional[Dict]:
    """
    Simplifies a found path into a dictionary structure to handle the found data
    for easily.
    """
    equalized_path: List[Edge] = equalize_stock_differences(path, user_config)

    if len(equalized_path) == 0:
        return None

    return {
        "from": equalized_path[0].have,
        "to": equalized_path[-1].want,
        "starting": equalized_path[0].paid,
        "ending": equalized_path[-1].received,
        "winnings": equalized_path[-1].received - equalized_path[0].paid,
        "transactions": equalized_path,
    }
