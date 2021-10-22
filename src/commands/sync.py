import logging
from typing import Any, Dict, List, Optional, Tuple

import requests
from src.config.user_config import UserConfig


def execute_sync(user_config: UserConfig, league: str):
    if user_config.account_name == None:
        raise Exception("Missing accountName in config file")
    if user_config.poe_session_id == None:
        raise Exception("Missing POESESSID in config file")

    print(user_config.poe_session_id)
    print(user_config.account_name)

    headers = {
        "Cookie": "POESESSID={}".format(user_config.poe_session_id),
        "User-Agent": "curl/7.76.1"
    }
    url = "https://www.pathofexile.com/character-window/get-stash-items"
    params = {
        "league": league,
        "accountName": user_config.account_name,
        "tabs": 1,  # this *should* be the currency stash tab
    }

    # TODO the currency stash tab is somewhat irrelevant, because users
    # would want the tool to find the stuff in the public premium stash tabs (+ currency stash tab maybe)
    #
    # Do some thinking here
    response = requests.get(url, params=params, headers=headers).json()

    currency_stash_idx = find_currency_stash(response["tabs"])
    logging.info(
        "Found Currency Stash Tab at index {}".format(currency_stash_idx))

    if currency_stash_idx is None:
        logging.info("No currency stash tab to sync with was found")
        return

    url = "https://www.pathofexile.com/character-window/get-stash-items"
    response = requests.get(url,
                            params={
                                "league": league,
                                "accountName": user_config.account_name,
                                "tabIndex": currency_stash_idx
                            },
                            headers=headers).json()

    synced_items = parse_items(response["items"])
    logging.info(synced_items)


def find_currency_stash(json: List[Dict[str, Any]]) -> Optional[int]:
    for stash in json:
        if stash["type"] == "CurrencyStash":
            return stash["i"]
    return None


# TODO maybe we have to check back the items found here with the list of
# supported items in the item_list module
def parse_items(json: List[Dict[str, Any]]) -> List[Tuple[str, int]]:
    """
    Parses a list of tuples of <type_line, stack_size>.
    """
    pairs = []

    for item in json:
        p = (item.get("typeLine"), item.get("stackSize"))

        # Skip non-stackable items, eg. armour in the crafting bench
        if p[1] is None:
            continue

        pairs.append(p)

    return pairs