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
from functools import reduce
import json
from dataclasses import dataclass
from typing import List, Dict

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
    "Silver Coin",
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

    def add_item(self, item: Item):
        pass

    @staticmethod
    def load_from_file(path: str) -> List[Item]:
        pass

    def serialize(self):
        return self.items

    @staticmethod
    def generate() -> ItemList:
        poetrade_data = poetrade()
        poeofficial_data = poeofficial()

        # Needs to be in this order for current naive merging approach, as
        # more details are pulled from official sources
        item_list = ItemList.__merge_lists(poetrade_data, poeofficial_data)
        item_list = ItemList.__postprocess_list(item_list)

        item_dict = dict()
        for item in item_list:
            item_dict[item.name] = item


        return ItemList(item_dict)

    @staticmethod
    def __merge_lists(list1: List[Item], list2: List[Item]) -> List[Item]:
        main_list: List[Item] = sorted(list1, key=lambda x: x.name)
        secondary_list: List[Item] = sorted(list2, key=lambda x: x.name)

        for i1 in main_list:
            for i2 in secondary_list:
                if i1.name == i2.name:
                    i1.ids.update(i2.ids)
                    i1.category = i2.category

        return main_list

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
    resp = requests.get("http://currency.poe.trade/")
    html = resp.text

    soup = BeautifulSoup(html, "html.parser")
    currency_have_div = soup.find("div", {"id": "currency-have"})
    elements = currency_have_div.find_all(class_="currency-selectable")

    item_list = [Item(
        name=x.get("title", x["data-title"]),
        backend="poetrade",
        item_id=x["data-id"],
        is_currency=False,
        is_basic=False,
        is_bulk_target=False
    ) for x in elements]

    return item_list


def poeofficial() -> List[Item]:
    resp = requests.get("https://www.pathofexile.com/api/trade/data/static")
    json_data = resp.json()["result"]

    # currency_data = [x for x in json_data if x["id"] == "Currency"][0]["entries"]
    item_list = []
    for category in json_data:
        for x in category["entries"]:
            item = Item(
                name=x["text"],
                backend="poeofficial",
                item_id=x["id"],
                is_currency=False,
                is_basic=False,
                is_bulk_target=False,
                category=category["id"]
            )
            item_list.append(item)

    return item_list


if __name__ == "__main__":
    # poe_trade_data = poetrade()
    # with open("assets/poetrade.json", "w") as f:
    #     json.dump(poe_trade_data, f, indent=2)

    # poeofficial_data = poeofficial()
    # with open("assets/poeofficial.json", "w") as f:
    #     json.dump(poeofficial_data, f, indent=2)

    item_list = ItemList.generate()
    with open("assets/items.json", "w") as f:
        data = json.dumps(item_list.serialize(), default=lambda o: o.__dict__,
                   sort_keys=True, indent=4)
        f.write(data)

