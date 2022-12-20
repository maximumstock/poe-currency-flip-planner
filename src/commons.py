import logging
from typing import Any, Dict, List, Set

LEAGUE_NAMES = ["Kalandra", "Hardcore Kalandra", "Standard", "Hardcore"]
VENDOR_OFFER_IGN = "__vendor__"


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
