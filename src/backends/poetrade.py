import concurrent.futures
import requests
from bs4 import BeautifulSoup
from typing import Optional, List

from src.items import load_items_poetrade

items = load_items_poetrade()


class Offer:
    def __init__(self, contact_ign: str, sell_price: float, buy_price: float,
                 stock: int):
        self.contact_ign = contact_ign
        self.conversion_rate = round(sell_price / buy_price, 5)
        self.stock = stock
        self.have: str
        self.want: str

        if len(self.contact_ign
               ) == 0 or self.conversion_rate == 0 or self.stock == 0:
            raise Exception("Parsing offer from poe.trade failed", self)

    def __str__(self):
        return "{} {} {}".format(self.contact_ign, self.conversion_rate,
                                 self.stock)

    def __repr__(self):
        return self.__str__()


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
        "online": True,
    }

    r = requests.get(url, params=params)
    offers = parse_conversion_offers(r.text)

    return {"offers": offers, "want": want, "have": have, "league": league}


"""
Helper functions to parse results from poe.trade."
"""


def parse_conversion_offers(html) -> List[Offer]:
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all(class_="displayoffer")
    parsed_rows = [parse_conversion_offer(x) for x in rows]
    offers = [x for x in parsed_rows if x is not None][:10]
    return offers


def parse_conversion_offer(offer_html) -> Optional[Offer]:
    """
    Parses a single offer from the poe.trade HTML.
    """

    if "data-stock" not in offer_html.attrs:
        return None

    sell = float(offer_html["data-sellvalue"])
    buy = float(offer_html["data-buyvalue"])
    stock = int(offer_html["data-stock"])
    contact_ign = offer_html["data-ign"]
    try:
        offer = Offer(contact_ign, sell, buy, stock)
        return offer
    except:
        return None


def map_currency(currency):
    sanitized_currency = "".join(currency.split("'"))
    if sanitized_currency in items.keys():
        return items[sanitized_currency]["id"]
    else:
        raise Exception("Unknown currency key " + currency)
