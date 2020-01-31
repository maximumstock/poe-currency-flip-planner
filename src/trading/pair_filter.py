"""
This module handles managing and building different sets of currency pairs for
arbitrage planning for a given backend.
"""

import json
from typing import List, Tuple


def load_pair_filter() -> List[Tuple[str, str]]:
    with open("assets/pair_filter.json", "r") as f:
        lines: List[str] = list(set(json.load(f)))
        pairs = []
        for line in lines:
            [first, second] = line.split("-")
            pairs.append((first, second))

        return pairs
