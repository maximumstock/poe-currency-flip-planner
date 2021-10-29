import logging
import urllib.parse
from typing import Any, Dict, List

import aiohttp
from aiolimiter.leakybucket import AsyncLimiter
from src.core.backends.throttler_ensemble import ThrottlerEnsemble

from src.commons import filter_large_outliers
from src.core.offer import Offer
from src.core.backends.task import Task, TaskException
from src.trading.items import ItemList


class PoeOfficial:

    # pathofexile.com/trade seems to impose a limit on how many actual trade
    # offers you're allowed to request together
    max_offers_per_request = 3
    item_list: ItemList
    throttler_ensemble: ThrottlerEnsemble

    def __init__(self, item_list: ItemList):
        self.item_list = item_list
        self.throttler_ensemble = ThrottlerEnsemble([
            # Ids
            AsyncLimiter(3, 5),
            AsyncLimiter(5, 15),
            AsyncLimiter(10, 90),
            AsyncLimiter(30, 300),
            # Offers
            AsyncLimiter(6, 4),
            AsyncLimiter(12, 4),
            AsyncLimiter(16, 12),
        ])

    async def fetch_offer_async(self, client_session: aiohttp.ClientSession,
                                task: Task) -> List[Offer]:

        await self.throttler_ensemble.wait()

        client_session.headers.update({
            "User-Agent":
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
            "Cookie":
            "POESESSID=be398733532f6a251513aabc3200790b"
        })

        offer_ids: List[str] = []
        query_id = None
        offers: List[Offer] = []

        # Fetching offer ids is rate-limited by 3:5:60,7:15:60,15:90:120,45:300:1800
        offer_id_url = "http://www.pathofexile.com/api/trade/exchange/{}".format(
            urllib.parse.quote(task.league))
        payload = {
            "exchange": {
                "status": {
                    "option": "online"
                },
                "have": [self.item_list.map_item(task.have, self.name())],
                "want": [self.item_list.map_item(task.want, self.name())],
            }
        }

        response = await client_session.request("POST",
                                                url=offer_id_url,
                                                json=payload)

        if response.status == 429:
            logging.debug("Body: {}".format(response.text))
            logging.debug("Rate limited during ids: {} -> {}".format(
                task.have, task.want))
            await AsyncLimiter(60, 1).acquire()
        if response.status != 200:
            raise TaskException(response.status)

        json = await response.json()

        offer_ids = json["result"]
        query_id = json["id"]
        offers = []

        if len(offer_ids) != 0:
            id_string = ",".join(offer_ids[:self.max_offers_per_request])
            url = "http://www.pathofexile.com/api/trade/fetch/{}?query={}&exchange".format(
                id_string, query_id)

            response = await client_session.get(url)

            if response.status == 429:
                logging.debug("Body: {}".format(response.text))
                logging.debug("Rate limited during ids: {} -> {}".format(
                    task.have, task.want))
                await AsyncLimiter(60, 1).acquire()
            if response.status != 200:
                raise TaskException(response.status)

            json = await response.json()
            raw_offers: List[Dict[str, Any]] = json["result"]

            offers_details = [
                PoeOfficial.map_offers_details(x) for x in raw_offers
            ]
            offers_details = filter_large_outliers(offers_details)[:task.limit]

            offers = [
                Offer(league=task.league,
                      have=task.have,
                      want=task.want,
                      contact_ign=details["contact_ign"],
                      conversion_rate=details["conversion_rate"],
                      stock=details["stock"]) for details in offers_details
            ]

        return offers

    def name(self):
        return "poeofficial"

    """
    Private helpers below
    """

    @staticmethod
    def map_offers_details(offer_details: Dict[str, Any]) -> Dict[str, Any]:
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


async def fetch_ids(sess, offer_id_url, payload) -> Any:
    return await sess.request("POST", url=offer_id_url, json=payload)
