import asyncio
import urllib

import aiohttp

from src import constants, flip
from src.backends.lib import AsyncRateLimiter


def name():
    return "Path of Exile Offical Trade API"


class RateLimitException(Exception):
    pass


def fetch_offers(league, currency_pairs, limit=3):
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(
        fetch_offers_async(league, currency_pairs, limit))
    return results


async def fetch_offers_async(league, currency_pairs, limit=3):
    rlimiter = AsyncRateLimiter(4, 5)
    results = []
    for p in currency_pairs:
        async with rlimiter:
            result = await fetch_offers_for_pair(league, p[0], p[1], limit)
            results.append(result)
    return results


"""
Private helpers below
"""


async def fetch_offers_for_pair(league, want, have, limit=5):
    """
    The official rate-limit is 5:5:60 -> stay right under it with 4:5
    """
    async with aiohttp.ClientSession() as sess:

        offer_ids = []
        query_id = None
        offers = []

        offer_id_url = "http://www.pathofexile.com/api/trade/exchange/{}".format(
            urllib.parse.quote(league))
        payload = {
            "exchange": {
                "status": {
                    "option": "online"
                },
                "have": [map_currency(have)],
                "want": [map_currency(want)]
            }
        }

        response = await sess.request("POST", url=offer_id_url, json=payload)
        try:
            json = await response.json()
            offer_ids = json["result"]
            query_id = json["id"]
        except Exception:
            raise

        if len(offer_ids) != 0:
            id_string = ",".join(offer_ids[:limit])
            url = "http://www.pathofexile.com/api/trade/fetch/{}?query={}&exchange".format(
                id_string, query_id)

            response = await sess.get(url)
            try:
                json = await response.json()
                offers = [map_offers_details(x) for x in json["result"]]
            except Exception:
                raise

        viable_offers = flip.filter_viable_offers(want, have, offers)

        return {
            "offers": viable_offers,
            "want": want,
            "have": have,
            "league": league
        }


def map_offers_details(offer_details):
    contact_ign = offer_details["listing"]["account"]["lastCharacterName"]
    stock = offer_details["listing"]["price"]["item"]["stock"]
    receive = offer_details["listing"]["price"]["item"]["amount"]
    pay = offer_details["listing"]["price"]["exchange"]["amount"]
    conversion_rate = round(receive/pay, 4)

    return {
        "contact_ign": contact_ign,
        "conversion_rate": conversion_rate,
        "stock": stock
    }


def map_currency(currency):
    if currency in constants.currencies:
        return constants.currencies[currency]["poeofficial"]
    else:
        raise Exception("Unknown currency key")
