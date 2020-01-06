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

from bs4 import BeautifulSoup
import requests
from functools import reduce
import json

blacklist = [
    "Scroll of Wisdom",
    "Portal Scroll",
    "Armourer's Scrap",
    "Blacksmith's Whetstone",
    "Silver Coin",
]

# List of items that people usually sell their non-currency bulk items for
target_currency_for_item_sales = ["Chaos Orb", "Exalted Orb"]
EVERYTHING_UNTIL_VAAL_ORBS = 16


def poetrade():
    resp = requests.get("http://currency.poe.trade/")
    html = resp.text

    soup = BeautifulSoup(html, "html.parser")
    currency_have_div = soup.find("div", {"id": "currency-have"})
    elements = currency_have_div.find_all(class_="currency-selectable")
    parsed = [{
        "id": int(x["data-id"]),
        "name": x.get("title", x["data-title"]),
        "currency": False,
        "basic": True if int(x["data-id"]) <= EVERYTHING_UNTIL_VAAL_ORBS else False,
        "non_currency_sales_target": False,
    } for x in elements]

    parsed = postprocess_list(parsed)
    parsed_dictionary = list_to_dict(parsed)

    return parsed_dictionary


def poeofficial():
    resp = requests.get("https://www.pathofexile.com/api/trade/data/static")
    json_data = resp.json()["result"]

    currency_data = [x for x in json_data if x["id"] == "Currency"][0]["entries"]

    currency_data = [{
        "id": x["id"],
        "name": x["text"],
        "currency": False,
        "basic": False,
        "non_currency_sales_target": False
    } for x in currency_data]

    postprocess_list(currency_data)
    return list_to_dict(currency_data)


def postprocess_list(item_list):
    # Filter out Nets
    parsed = [x for x in item_list if " Net" not in x["name"]]

    # Filter out blacklisted items
    parsed = [x for x in parsed if x["name"] not in blacklist]

    # Mark certain currency items for analysis usage
    for e in parsed:
        # mark orbs and shards as actual currency
        if "Orb" in e["name"] or "Shard" in e["name"]:
            e["currency"] = True
        # mark certain currency items as targets for non-currency item sales
        if e["name"] in target_currency_for_item_sales:
            e["non_currency_sales_target"] = True

    return parsed


def list_to_dict(dictionary):
    # transform into dictionary with the name as key
    parsed = sorted(dictionary, key=lambda x: x["id"])
    parsed = [{"".join(x["name"].split('\'')): x} for x in parsed]
    parsed_dictionary = reduce(lambda x, y: x.update(y) or x, parsed)
    return parsed_dictionary


if __name__ == "__main__":
    poe_trade_data = poetrade()
    with open("assets/poetrade.json", "w") as f:
        json.dump(poe_trade_data, f, indent=2)

    poeofficial_data = poeofficial()
    with open("assets/poeofficial.json", "w") as f:
        json.dump(poeofficial_data, f, indent=2)
