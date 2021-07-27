import logging
import urllib.parse
from typing import Any, Dict, List, Tuple

import aiohttp

from src.commons import filter_large_outliers
from src.core.offer import Offer
from src.core.backends.task import Task, TaskException
from src.trading.items import ItemList


class PoeOfficial:

    # pathofexile.com/trade seems to impose a limit on how many actual trade
    # offers you're allowed to request together
    max_offers_per_request = 20
    item_list: ItemList

    def __init__(self, item_list: ItemList):
        self.item_list = item_list

    async def fetch_offer_async(self, client_session: aiohttp.ClientSession,
                                task: Task) -> List[Offer]:

        offer_ids: List[str] = []
        query_id = None
        offers: List[Offer] = []

        # Fetching offer ids is rate-limited by 5:15:60,10:90:300,30:300:1000
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

        try:
            response = await fetch_ids(client_session, offer_id_url, payload)
            json = await response.json()

            offer_ids = json["result"]
            query_id = json["id"]
            offers = []

        except Exception as e:
            logging.debug("Body: {}".format(json))
            logging.debug("Rate limited during ids: {} -> {}".format(
                task.have, task.want))
            raise TaskException()

        try:
            if len(offer_ids) != 0:
                # Fetching offer data is rate-limited by 12:4:10,16:12:300
                id_string = ",".join(offer_ids[:self.max_offers_per_request])
                url = "http://www.pathofexile.com/api/trade/fetch/{}?query={}&exchange".format(
                    id_string, query_id)

                response = await client_session.get(url)
                if response.status != 200:
                    raise TaskException()
                json = await response.json()
                raw_offers: List[Dict[str, Any]] = json["result"]

                offers_details = [
                    PoeOfficial.map_offers_details(x) for x in raw_offers
                ]
                offers_details = filter_large_outliers(
                    offers_details)[:task.limit]

                offers = [
                    Offer(league=task.league,
                          have=task.have,
                          want=task.want,
                          contact_ign=details["contact_ign"],
                          conversion_rate=details["conversion_rate"],
                          stock=details["stock"]) for details in offers_details
                ]

            return offers
        except Exception as e:
            logging.debug("Body: {}".format(json))
            logging.debug("Rate limited during data: {} -> {}".format(
                task.have, task.want))
            raise TaskException()

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
