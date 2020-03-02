import asyncio
import urllib
import aiohttp
from asyncio_throttle import Throttler
from typing import List, Dict, Tuple
import numpy as np

from src.trading.items import ItemList


def name():
    return "poeofficial"


class RateLimitException(Exception):
    pass


def fetch_offers(league, currency_pairs, item_list: ItemList, limit=7):
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(
        fetch_offers_async(league, currency_pairs, item_list, limit))
    return results


async def fetch_offers_async(league, currency_pairs, item_list: ItemList, limit):
    throttler = Throttler(10)

    async with aiohttp.ClientSession() as sess:
        tasks = [
            asyncio.ensure_future(
                fetch_offers_for_pair(sess, throttler, league, p[0], p[1], item_list,
                                      limit)) for p in currency_pairs
        ]

        (done, _not_done) = await asyncio.wait(tasks)
        results = [task.result() for task in done]
        successful = [x for x in results if x is not None]
        unsuccessful = [x for x in results if x is None]

        if len(unsuccessful) > 0:
            print("Failed to fetch offers for {} pairs".format(len(unsuccessful)))

        return results


"""
Private helpers below
"""


async def fetch_ids(sess, offer_id_url, payload) -> Tuple[str, List[str]]:
    response = await sess.request("POST", url=offer_id_url, json=payload)
    json = await response.json()
    offer_ids = json["result"]
    query_id = json["id"]
    return query_id, offer_ids


async def fetch_offers_for_pair(sess, throttler, league, want, have, item_list: ItemList, limit=5):
    async with throttler:
        offer_ids: List[str] = []
        query_id = None
        offers: List[Dict] = []

        offer_id_url = "http://www.pathofexile.com/api/trade/exchange/{}".format(
            urllib.parse.quote(league))
        payload = {
            "exchange": {
                "status": {
                    "option": "online"
                },
                "have": [item_list.map_item(have, name())],
                "want": [item_list.map_item(want, name())],
            }
        }

        try:
            query_id, offer_ids = await fetch_ids(sess, offer_id_url, payload)
            if len(offer_ids) != 0:
                id_string = ",".join(offer_ids[:limit])
                url = "http://www.pathofexile.com/api/trade/fetch/{}?query={}&exchange".format(
                    id_string, query_id)

                response = await sess.get(url)
                json = await response.json()
                raw_offers = json["result"]
                offers = post_process_offers(raw_offers, have, want)

            return {"offers": offers, "want": want, "have": have, "league": league}
        except Exception as e:
            print("Rate limited during: {} -> {}".format(have, want))
            return None


def post_process_offers(raw_offers: List[Dict], have: str, want: str) -> List[Dict]:
    # Extract relevant offer data from nested JSON into dictionary
    offers = [map_offers_details(x) for x in raw_offers]
    offers = filter_large_outliers(offers)

    return offers


def filter_large_outliers(offers: List[Dict]) -> List[Dict]:
    """
    Filter out all offers with a conversion rate which is above the
    95th percentile of all found conversion rates for an item pair.
    """
    conversion_rates = [e["conversion_rate"] for e in offers]
    total = sum(conversion_rates)
    avg = total / len(conversion_rates)

    upper_boundary = np.percentile(conversion_rates, 95)
    offers = [x for x in offers if x["conversion_rate"] < upper_boundary]

    return offers


def map_offers_details(offer_details):
    contact_ign = offer_details["listing"]["account"]["lastCharacterName"]
    stock = offer_details["listing"]["price"]["item"]["stock"]
    receive = offer_details["listing"]["price"]["item"]["amount"]
    pay = offer_details["listing"]["price"]["exchange"]["amount"]
    conversion_rate = round(receive / pay, 4)

    return {
        "contact_ign": contact_ign,
        "conversion_rate": conversion_rate,
        "stock": stock,
    }
