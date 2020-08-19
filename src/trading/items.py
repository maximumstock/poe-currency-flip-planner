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
from typing import List, Dict, Tuple, Any
import itertools
import os
import attr
import json
import deserialize


class UnsupportedItemException(Exception):
    pass


# List of items that people usually sell their non-currency bulk items (eg.
# maps, div cards, fossils, etc.) for
bulk_targets = ["Chaos Orb", "Exalted Orb"]

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
    "Vaal Orb",
    "Gemcutter's Prism",
    "Glassblower's Bauble",
    "Divine Orb",
    "Blessed Orb",
    "Regal Orb",
    "Cartographer's Chisel",
]


@attr.s
class Item:
    name: str = attr.ib()
    ids: Dict[str, str] = attr.ib()
    is_currency: bool = attr.ib()
    is_basic_currency: bool = attr.ib()
    is_bulk_target: bool = attr.ib()
    category: str = attr.ib()

    def is_supported_by(self, backend_name: str) -> bool:
        return backend_name in self.ids.keys()


class UnknownBackendException(Exception):
    pass


@attr.s
class ItemList:
    items: Dict[str, Item] = attr.ib()

    @staticmethod
    def load_from_file(path: str = None) -> ItemList:
        if path is None:
            path = os.path.dirname(
                os.path.abspath(__file__)) + "/../../assets/items.json"

        with open(path, "r") as f:
            item_list_json = json.load(f)
            return deserialize.deserialize(ItemList, item_list_json)

    def find_discrepancies(self) -> Tuple[Dict[str, int], List[Item]]:
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
                    backend_counts[backend] = (backend_counts[backend]
                                               if backend in backend_counts
                                               else 0) + 1

        return backend_counts, unsynced_items

    def map_item(self, name: str, backend: str) -> str:
        try:
            return self.items[name].ids[backend]
        except Exception:
            raise UnsupportedItemException(
                "{} backend does not support item {}".format(backend, name))

    def is_item_supported(self, name: str) -> bool:
        try:
            # Some backend that supports it exists
            return len(self.items[name].ids) > 0
        except Exception:
            raise UnsupportedItemException(
                "backend does not support item {}".format(name))

    def ensure_items_are_supported(self,
                                   requested_item_pairs: List[Tuple[str, str]],
                                   backend: Any) -> bool:
        for pair in requested_item_pairs:
            self.is_item_supported(pair[0])
            self.is_item_supported(pair[1])

        return True

    def get_item_list_for_backend(self,
                                  backend: Any,
                                  config: Dict = {}) -> List[Tuple[str, ...]]:
        backend_name: str = backend.name()

        supported_items = [
            i for i in self.items.values() if i.is_supported_by(backend_name)
        ]

        if len(supported_items) == 0:
            raise UnknownBackendException(
                "Unknown backend {}".format(backend_name))

        item_list: List = []

        for item in self.items.values():
            if item.is_supported_by(backend_name):

                currency_items = [
                    i.name for i in supported_items if i.is_currency is True
                ]
                bulk_items = [
                    i.name for i in supported_items if i.is_currency is False
                ]
                bulk_targets = [
                    i.name for i in supported_items if i.is_bulk_target is True
                ]

                result = list(itertools.permutations(currency_items, 2))

                if config.get("fullbulk") is True:
                    result = result + list(
                        itertools.product(bulk_targets, bulk_items)) + list(
                            itertools.product(bulk_items, bulk_targets))

                item_list = result
                return item_list

        return item_list

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
    def __merge_lists(ground_truth: List[Item],
                      incoming: List[Item]) -> List[Item]:
        """
        Try to merge @incoming list of items into @ground_truth list of items
        """
        ground_truth = sorted(ground_truth, key=lambda x: x.name)
        incoming = sorted(incoming, key=lambda x: x.name)

        for true_item in ground_truth:
            for inc_item in incoming:
                if true_item.name == inc_item.name:
                    true_item.ids.update(inc_item.ids)

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
    item_categories = currency_have_div.find_all_next("div",
                                                      {"class": "category"})

    def map_item_name(name: str):
        _map = {
            "Apprentice Cartographer's Sextant": "Simple Sextant",
            "Journeyman Cartographer's Sextant": "Prime Sextant",
            "Master Cartographer's Sextant": "Awakened Sextant"
        }
        return _map[name] if name in _map else name

    for category_div in item_categories:
        category_name = category_div.find_all_next(
            "div", {"class": "currency-toggle"})[0].contents[1]
        elements = category_div.find_all_next("div",
                                              {"class": "currency-selectable"})

        for x in elements:
            item_name = str(x.get("title", x.text.strip()))
            item_name = map_item_name(item_name)
            item_id = x.get("data-id")
            if item_id is None:
                print(x)
            item = Item(name=item_name,
                        ids={"poetrade": item_id},
                        is_currency=False,
                        is_basic_currency=False,
                        is_bulk_target=False,
                        category=category_name or "Currency")
            item_list.append(item)

    return item_list


def poeofficial() -> List[Item]:
    resp = requests.get("https://www.pathofexile.com/api/trade/data/static")
    json_data = resp.json()["result"]

    item_list = []
    for category in json_data:
        for x in category["entries"]:
            item = Item(name=x["text"].strip(),
                        ids={"poeofficial": x["id"]},
                        is_currency=False,
                        is_basic_currency=False,
                        is_bulk_target=False,
                        category=category["label"] or category["id"])
            item_list.append(item)

    return item_list
