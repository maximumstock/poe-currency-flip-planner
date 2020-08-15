import logging
from typing import List

import aiohttp
from bs4 import BeautifulSoup

from src.commons import filter_large_outliers
from src.core.offer import Offer
from src.core.backends.task import Task, TaskException
from src.trading.items import ItemList


class PoeTrade:

    item_list: ItemList

    def __init__(self, item_list: ItemList):
        self.item_list = item_list

    async def fetch_offer_async(self, client_session: aiohttp.ClientSession,
                                task: Task) -> List[Offer]:
        url = "https://currency.poe.trade/search"
        params = {
            "league": task.league,
            "want": self.item_list.map_item(task.want, self.name()),
            "have": self.item_list.map_item(task.have, self.name()),
            "online": "x",
        }

        response = await client_session.request("GET", url=url, params=params)
        html = await response.text()

        if response.status != 200:
            logging.debug("Error during poe.trade fetch: Status {}".format(
                response.status))
            logging.debug(html)
            raise TaskException()

        offers = PoeTrade.parse_conversion_offers(html)
        offers = filter_large_outliers(offers)[:task.limit]

        offers = [
            Offer(task.league, task.have, task.want, x["contact_ign"],
                  x["conversion_rate"], x["stock"]) for x in offers
        ]

        return offers

    def name(self):
        return "poetrade"

    """
    Helper functions to parse results from poe.trade."
    """

    @staticmethod
    def parse_conversion_offers(html):
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all(class_="displayoffer")
        parsed_rows = [PoeTrade.parse_conversion_offer(x) for x in rows]
        return [x for x in parsed_rows if x is not None]

    @staticmethod
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
