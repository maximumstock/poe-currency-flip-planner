import logging
from typing import Any, Dict, List, Set

import numpy as np

league_names = ["Ritual", "Hardcore Ritual", "Standard", "Hardcore"]


def filter_large_outliers(offers: List[Dict]) -> List[Dict]:
    """
    Filter out all offers with a conversion rate which is above the
    95th percentile of all found conversion rates for an item pair.
    """

    if len(offers) > 10:
        conversion_rates = [e["conversion_rate"] for e in offers]
        upper_boundary = np.percentile(conversion_rates, 95)
        offers = [x for x in offers if x["conversion_rate"] < upper_boundary]

    return offers


def init_logger(debug: bool):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format='%(message)s')


def load_excluded_traders():
    default_path = "config/excluded_traders.txt"
    with open(default_path, "r") as f:
        excluded_traders = [x.strip() for x in f.readlines()]
        return excluded_traders


def unique_conversions_by_trader_name(
        conversions: List[Dict[str, Any]]) -> List[Dict]:
    seen_traders: Set[str] = set()
    unique_conversions = []

    for conversion in conversions:
        trader_names = [t.contact_ign for t in conversion["transactions"]]
        has_seen_trader = any(
            [True for x in trader_names if x in seen_traders])
        if has_seen_trader:
            continue

        for t in trader_names:
            seen_traders.add(t)

        unique_conversions.append(conversion)

    return unique_conversions
