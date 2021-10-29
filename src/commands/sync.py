import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from src.config.user_config import UserConfig
from tqdm import tqdm


def execute_sync(config_file_path: Optional[str], league: str):
    try:
        # Load user config
        config_file_path = UserConfig.get_file_path(config_file_path)
        user_config = UserConfig.from_file(config_file_path, False)
    except Exception as ex:
        logging.error(f"Error: {ex.args[0]}")
        exit(1)

    if user_config.account_name == None:
        raise Exception("Missing accountName in config file")
    if user_config.poe_session_id == None:
        raise Exception("Missing POESESSID in config file")

    logging.info(
        f"Starting sync for account {user_config.account_name} in league {league}"
    )

    session = requests.Session()
    session.headers.update({
        "Cookie":
        "POESESSID={}".format(user_config.poe_session_id),
        "User-Agent":
        "curl/7.76.1"
    })

    stash_tabs = fetch_stash_tabs(session, league, user_config.account_name)
    public_tab_indices = find_public_stashes(stash_tabs)
    logging.info("Found {} public stash tabs".format(len(public_tab_indices)))

    if len(public_tab_indices) == 0:
        logging.warn("No public stash tabs to sync with were found")
        return

    items: Dict[str, int] = dict()

    for tab_idx in tqdm(public_tab_indices):
        stash_items = fetch_stash_tab_items(session, league,
                                            user_config.account_name, tab_idx)
        aggregate(items, stash_items)
        time.sleep(1)

    for item_name, stack_size in items.items():
        user_config.set_asset_quantity(item_name, stack_size)

    user_config.save(config_file_path)
    logging.info(f"Successfully synced {len(items)} items")


def aggregate(acc: Dict[str, int], stash_items: List[Tuple[str, int]]) -> dict:
    for item_name, stack_size in stash_items:
        acc.update({item_name: acc.get(item_name, 0) + stack_size})

    return acc


def fetch_stash_tabs(session: requests.Session, league: str,
                     account_name: str) -> List[Dict[str, Any]]:
    url = "https://www.pathofexile.com/character-window/get-stash-items"
    params = {
        "league": league,
        "accountName": account_name,
        "tabs": 1,  # this should give a list of all tabs
    }
    return session.get(url, params=params).json()["tabs"]


def fetch_stash_tab_items(session: requests.Session, league: str,
                          account_name: str,
                          tab_idx: int) -> List[Tuple[str, int]]:
    url = "https://www.pathofexile.com/character-window/get-stash-items"

    response = session.get(
        url,
        params={
            "league": league,
            "accountName": account_name,
            "tabIndex": tab_idx
        },
    )

    synced_items = parse_items(response.json()["items"])
    return synced_items


def find_public_stashes(json: List[Dict[str, Any]]) -> List[int]:
    return [stash["i"] for stash in json if stash["type"] == "PremiumStash"]


# TODO maybe we have to check back the items found here with the list of
# supported items in the item_list module
def parse_items(json: List[Dict[str, Any]]) -> List[Tuple[str, int]]:
    """
    Parses a list of tuples of <type_line, stack_size>.
    """
    stackable_items = [(item.get("typeLine"), item.get("stackSize"))
                       for item in json if item.get("stackSize") != None]

    return stackable_items
