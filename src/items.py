"""
This module handles managing and building different sets of currency pairs for
arbitrage planning for a given backend.
"""

import json
import itertools
from typing import Dict, List
"""
Public API
"""


def load_items(backend) -> Dict[str, Dict]:
    if backend.name() is "poetrade":
        return load_items_poetrade()
    if backend.name() is "poeofficial":
        return load_items_poeofficial()

    raise UnknownBackendException("Unknown or empty backend string given")


def build_item_list(backend, config: Dict = {}) -> List:
    """
    Builds a list of item pairs to use for arbitrage planning based
    on a given backend.
    """
    items = load_items(backend)
    if backend.name() is "poetrade":
        data = build_item_list_poetrade(items.values(), config)
    elif backend.name() is "poeofficial":
        data = build_item_list_poetrade(items.values(), config)
    else:
        raise UnknownBackendException("Unknown Backend")

    data = list(map(lambda x: (x[0]["name"], x[1]["name"]), data))
    return data


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
    non_currency_targets = [
        x for x in items if x["non_currency_sales_target"] is True
    ]

    result = list(itertools.permutations(currency_items, 2))

    if config.get("fullbulk") is True:
        result = result + list(
            itertools.product(non_currency_targets, non_currency_items)
        ) + list(itertools.product(non_currency_items, non_currency_targets))

    return result


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
