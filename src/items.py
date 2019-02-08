"""
This module handles managing and building different sets of currency pairs for
arbitrage planning for a given backend.
"""

import json
import itertools
from typing import Dict, List, Tuple

"""
Public API
"""


def load_items(backend: str) -> Dict[str, Dict]:
    if backend is "poetrade":
        return load_items_poetrade()
    if backend is "poeofficial":
        return load_items_poeofficial()

    raise UnknownBackendException("Unknown or empty backend string given")


def build_item_list(backend: str, config: Dict = {}) -> List:
    """
    Builds a list of item pairs to use for arbitrage planning based
    on a given backend.
    """
    if backend is "poetrade":
        items = load_items_poetrade()
        data = build_item_list_poetrade(items.values(), config)
        data = list(map(lambda x: (x[0]["name"], x[1]["name"]), data))
        return data
    if backend is "poeofficial":
        items = load_items_poeofficial()
        return build_item_list_poeofficial(items.keys(), config)

    raise UnknownBackendException("Unknown or empty backend string given")


"""
Private Stuff
"""


def build_item_list_poetrade(items: List, config: Dict = {}):
    """
    For poe.trade, we support many different currencies and other bulk items,
    like maps, essences, etc. Since nobody trades maps for maps, we need to
    carefully construct item pairs, which are then used to request data for
    our offer graph. We want to include paths...

    1. between two currencies
    2. between non-currency items and currency items that are flagged to usually
       be the target of sales for non-currency items (eg. Chaos and Exalts)
    """
    currency_items = [x for x in items if x["currency"] is True]
    non_currency_items = [x for x in items if x["currency"] is False]
    non_currency_targets = [x for x in items if x["non_currency_sales_target"] is True]

    result: List = list(itertools.permutations(currency_items, 2))

    # Use edge filter to remove unnecessary edges
    allowed_pairs = load_pair_filter()
    result = filter_pairs(result, allowed_pairs)

    if config.get("fullbulk") is True:
        result = result + list(
            itertools.product(non_currency_targets, non_currency_items)
        ) + list(
            itertools.product(non_currency_items, non_currency_targets)
        )

    return result


def build_item_list_poeofficial(items: List, config: Dict = {}) -> List:
    permutations = list(itertools.permutations(items, 2))
    return permutations


class UnknownBackendException(Exception):
    pass


def load_items_poetrade() -> Dict[str, Dict]:
    with open("assets/poetrade.json", "r") as f:
        return json.load(f)


def load_items_poeofficial() -> Dict[str, Dict]:
    with open("assets/poeofficial.json", "r") as f:
        return json.load(f)


def load_pair_filter() -> List[str]:
    with open("assets/pair_filter.json", "r") as f:
        return list(set(json.load(f)))


def filter_pairs(pairs: List[Tuple[str, str]], allowed_pairs: List[str]):
    return [x for x in pairs if "{}-{}".format(x[0]["name"], x[1]["name"]) in allowed_pairs]
