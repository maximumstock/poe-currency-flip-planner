"""
This module handles tasks that are related to fetching currency and bulk item
data from poe.trade and pathofexile.com/trade. Per backend, we fetch a list
of currency and bulk items we want to support with this tool and writes them
out to a file in `assets/<backend>.json`.

The file holds a dictionary of item name to another dictionary. The inner
dictionaries hold item id, item name, flag to mark them as currency (this is
true for "Orbs" and "Shards" and false for the remaining bulk items).

Notes:

- we filter out all types of nets
"""
from __future__ import annotations

from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from typing import List, Dict
import pickle

# List of items that people usually sell their non-currency bulk items (eg.
# maps, div cards, fossils, etc.) for
bulk_targets = [
    "Chaos Orb",
    "Exalted Orb"
]

blacklist = [
    "Scroll of Wisdom",
    "Portal Scroll",
    "Armourer's Scrap",
    "Blacksmith's Whetstone",
]

# List of items that represent basic currencies, commonly used
basic_currencies = [
    "Chaos Orb",
    "Orb of Fusing",
    "Chromatic Orb",
    "Orb of Alchemy",
    "Jeweller's Orb",
    "Exalted Orb",
    "Orb of Alteration",
    "Orb of Scouring",
    "Orb of Regret",
]


@dataclass
class Item:
    name: str
    ids: Dict[str, str]
    is_currency: bool
    is_basic_currency: bool
    is_bulk_target: bool
    category: str

    def __init__(self, name: str, backend: str, item_id: str, is_currency: bool, is_basic: bool, is_bulk_target: bool,
                 category: str = None):
        self.name = name
        self.ids = {backend: item_id}
        self.is_currency = is_currency
        self.is_basic_currency = is_basic
        self.is_bulk_target = is_bulk_target
        self.category = category


@dataclass
class ItemList:
    items: Dict[str, Item]

    @staticmethod
    def load_from_file(path: str = None) -> ItemList:
        if path is None:
            path = "assets/items.pickle"

        with open(path, "rb") as f:
            return pickle.load(f)

    def find_discrepancies(self) -> (Dict[str, int], List[Item]):
        backend_counts: Dict[str, int] = dict()
        backend_counts["all"] = 0
        supported_backends = ["poetrade", "poeofficial"]

        unsynced_items: List[Item] = []

        for item in self.items.values():
            if len(item.ids) == len(supported_backends):
                backend_counts["all"] = backend_counts["all"] + 1
            else:
                unsynced_items.append(item)
            for backend in supported_backends:
                if backend in item.ids.keys():
                    backend_counts[backend] = (backend_counts[backend] if backend in backend_counts else 0) + 1

        return backend_counts, unsynced_items

    @staticmethod
    def generate() -> ItemList:
        poetrade_data = poetrade()
        poeofficial_data = poeofficial()

        # Needs to be in this order for current naive merging approach, as
        # more details are pulled from official sources
        item_list = ItemList.__merge_lists(poeofficial_data, poetrade_data)
        item_list = ItemList.__postprocess_list(item_list)

        item_dict = dict()
        for item in item_list:
            item_dict[item.name] = item

        return ItemList(item_dict)

    @staticmethod
    def __merge_lists(ground_truth: List[Item], incoming: List[Item]) -> List[Item]:
        """
        Try to merge @incoming list of items into @ground_truth list of items
        """
        ground_truth: List[Item] = sorted(ground_truth, key=lambda x: x.name)
        incoming: List[Item] = sorted(incoming, key=lambda x: x.name)

        for true_item in ground_truth:
            for inc_item in incoming:
                if true_item.name == inc_item.name:
                    true_item.ids.update(inc_item.ids)
                    true_item.category = inc_item.category

                if inc_item.name in true_item.name:
                    true_item.ids.update(inc_item.ids)

        return ground_truth

    @staticmethod
    def __postprocess_list(item_list: List[Item]) -> List[Item]:
        # Filter out blacklisted items
        parsed: List[Item] = [x for x in item_list if x.name not in blacklist]

        # Mark certain currency items for analysis usage
        for item in parsed:
            # mark certain currency items as targets for non-currency item sales
            if item.name in bulk_targets:
                item.is_bulk_target = True
            # mark currency
            if item.category == "Currency":
                item.is_currency = True
            # mark basic currency
            if item.name in basic_currencies:
                item.is_basic_currency = True

        return parsed


def poetrade() -> List[Item]:
    item_list: List[Item] = []

    resp = requests.get("http://currency.poe.trade/")
    html = resp.text
    soup = BeautifulSoup(html, "html.parser")

    currency_have_div = soup.find("div", {"id": "currency-have"})
    item_categories = currency_have_div.find_all_next("div", {"class": "category"})

    for category_div in item_categories:
        category_name = category_div.find_all_next("div", {"class": "currency-toggle"})[0].contents[1]
        elements = category_div.find_all_next("div", {"class": "currency-selectable"})

        for x in elements:
            item = Item(
                name=str(x.get("title", x.text.strip())),
                backend="poetrade",
                item_id=x["data-id"],
                is_currency=False,
                is_basic=False,
                is_bulk_target=False,
                category=category_name or "Currency"
            )
            item_list.append(item)

    return item_list


def poeofficial() -> List[Item]:
    resp = requests.get("https://www.pathofexile.com/api/trade/data/static")
    json_data = resp.json()["result"]

    item_list = []
    for category in json_data:
        for x in category["entries"]:
            item = Item(
                name=x["text"].strip(),
                backend="poeofficial",
                item_id=x["id"],
                is_currency=False,
                is_basic=False,
                is_bulk_target=False,
                category=category["label"] or category["id"]
            )
            item_list.append(item)

    return item_list


def test():
    item_list = ItemList.generate()

    (n_unsynced_items, unsynced_items) = item_list.find_discrepancies()
    print("Item counts:", n_unsynced_items)
    print("Encountered {} unsynced items".format(len(unsynced_items)))
    for item in unsynced_items:
        print(item)

    with open("assets/items.pickle", "wb") as f:
        import sys
        sys.setrecursionlimit(1000000)
        pickle.dump(item_list, f)


if __name__ == "__main__":
    test()
