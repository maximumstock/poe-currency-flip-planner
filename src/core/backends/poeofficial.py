import asyncio
import urllib
import aiohttp
from asyncio_throttle import Throttler
from typing import List, Dict, Tuple
import numpy as np

from src.trading.items import ItemList
from src.commons import filter_large_outliers


def name():
    return "poeofficial"


class RateLimitException(Exception):
    pass


def fetch_offers(league, currency_pairs, item_list: ItemList, limit=10):
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(
        fetch_offers_async(league, currency_pairs, item_list, limit))
    return results


async def fetch_offers_async(league, currency_pairs, item_list: ItemList, limit):
    trade_search_throttler = Throttler(5, 3, 1)
    trade_fetch_throttler = Throttler(4, 3, 1)

    async with aiohttp.ClientSession() as sess:
        tasks = [
            asyncio.ensure_future(
                fetch_offers_for_pair(sess, trade_search_throttler, trade_fetch_throttler, league, p[0], p[1], item_list,
                                      limit)) for p in currency_pairs
        ]

        (done, _not_done) = await asyncio.wait(tasks)
        results = [task.result() for task in done]
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


async def fetch_offers_for_pair(sess, trade_search_throttler, trade_fetch_throttler, league, want, have, item_list: ItemList, limit):
    offer_ids: List[str] = []
    query_id = None
    offers: List[Dict] = []

    # Fetching offer ids is rate-limited by 12:6:60,20:12:300
    async with trade_search_throttler:
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
            print("Fetching ids")
            query_id, offer_ids = await fetch_ids(sess, offer_id_url, payload)
            offers = []
        except Exception as e:
            print("Rate limited during ids: {} -> {}".format(have, want))
            return None

    # Fetching offer data is rate-limited by 12:4:10,16:12:300
    async with trade_fetch_throttler:
        try:
            if len(offer_ids) != 0:
                id_string = ",".join(offer_ids[:20])
                url = "http://www.pathofexile.com/api/trade/fetch/{}?query={}&exchange".format(
                    id_string, query_id)

                print("Fetching data")
                response = await sess.get(url)
                json = await response.json()
                raw_offers = json["result"]
                offers = post_process_offers(raw_offers, have, want)
                offers = offers[:limit]

            return {"offers": offers, "want": want, "have": have, "league": league}
        except Exception as e:
            print("Rate limited during data: {} -> {}".format(have, want))
            return None


def post_process_offers(raw_offers: List[Dict], have: str, want: str) -> List[Dict]:
    # Extract relevant offer data from nested JSON into dictionary
    offers = [map_offers_details(x) for x in raw_offers]
    offers = filter_large_outliers(offers)

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
