import concurrent.futures
import requests
from bs4 import BeautifulSoup

from src.trading.items import ItemList


def name():
    return "poetrade"


def fetch_offers(league, currency_pairs, item_list: ItemList, limit=10):
    """
    Fetches trading offers for a specific league and a pair of currencies from
    poe.trade and turns the data into a suitable format.
    """

    params = [[league, pair[0], pair[1], item_list, limit] for pair in currency_pairs]

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = executor.map(lambda p: fetch_offers_for_pair(*p), params)
        offers = list(map(lambda x: x, futures))
        # Filter offers from currency pairs that do not hold any offers
        offers = [x for x in offers if len(x["offers"]) > 0]
        return offers


def fetch_offers_for_pair(league, want, have, item_list: ItemList, limit=10):
    url = "http://currency.poe.trade/search"
    params = {
        "league": league,
        "want": item_list.map_item(want, name()),
        "have": item_list.map_item(have, name()),
        "online": True,
    }

    r = requests.get(url, params=params)
    offers = parse_conversion_offers(r.text, limit)

    return {"offers": offers, "want": want, "have": have, "league": league}


"""
Helper functions to parse results from poe.trade."
"""


def parse_conversion_offers(html, limit: int):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all(class_="displayoffer")
    parsed_rows = [parse_conversion_offer(x) for x in rows]
    return [x for x in parsed_rows if x is not None][:limit]


def parse_conversion_offer(offer_html):

    if "data-stock" not in offer_html.attrs:
        return None

    receive = float(offer_html["data-sellvalue"])
    pay = float(offer_html["data-buyvalue"])
    conversion_rate = round(receive / pay, 4)
    stock = int(offer_html["data-stock"])

    return {
        "contact_ign": offer_html["data-ign"],
        "conversion_rate": conversion_rate,
        "stock": stock,
    }

