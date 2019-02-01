import concurrent.futures
import requests
from bs4 import BeautifulSoup

from src.items import load_items_poetrade

items = load_items_poetrade()


def name():
    return "poe.trade"


def fetch_offers(league, currency_pairs, limit=10):
    """
    Fetches trading offers for a specific league and a pair of currencies from
    poe.trade and turns the data into a suitable format.
    """

    params = [[league, pair[0], pair[1], limit] for pair in currency_pairs]

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = executor.map(lambda p: fetch_offers_for_pair(*p), params)
        offers = list(map(lambda x: x, futures))
        # Filter offers from currency pairs that do not hold any offers
        offers = [x for x in offers if len(x["offers"]) > 0]
        return offers


def fetch_offers_for_pair(league, want, have, limit=10):
    url = "http://currency.poe.trade/search"
    params = {
        "league": league,
        "want": map_currency(want),
        "have": map_currency(have),
        "online": True
    }

    r = requests.get(url, params=params)
    offers = parse_conversion_offers(r.text)

    return {
        "offers": offers,
        "want": want,
        "have": have,
        "league": league
    }


"""
Helper functions to parse results from poe.trade."
"""


def parse_conversion_offers(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all(class_="displayoffer")
    parsed_rows = [parse_conversion_offer(x) for x in rows]
    return [x for x in parsed_rows if x is not None][:5]


def parse_conversion_offer(offer_html):

    if "data-stock" not in offer_html.attrs:
        return None

    receive = float(offer_html["data-sellvalue"])
    pay = float(offer_html["data-buyvalue"])
    conversion_rate = round(receive/pay, 4)
    stock = int(offer_html["data-stock"])

    return {
        "contact_ign": offer_html["data-ign"],
        "conversion_rate": conversion_rate,
        "stock": stock
    }


def map_currency(currency):
    if currency in items.keys():
        return items[currency]["id"]
    else:
        raise Exception("Unknown currency key")
