import requests
import itertools
from bs4 import BeautifulSoup

currencies = {
  "Alteration": {
    "id": 1,
    "tier": 3
  },
  "Fusing": {
    "id": 2,
    "tier": 2
  },
  "Alchemy": {
    "id": 3,
    "tier": 3
  },
  "Chaos": {
    "id": 4,
    "tier": 1
  },
  "Gemcutter's Prism": {
    "id": 5,
    "tier": 3
  },
  "Exalted": {
    "id": 6,
    "tier": 0
  },
  "Chromatic": {
    "id": 7,
    "tier": 3
  },
  "Jewellers": {
    "id": 8,
    "tier": 3
  },
  "Cartographer's Chisel": {
    "id": 10,
    "tier": 2
  },
  "Scouring": {
    "id": 11,
    "tier": 1
  },
  "Regret": {
    "id": 13,
    "tier": 1
  },
  "Regal": {
    "id": 14,
    "tier": 1
  },
  "Transmutation": {
    "id": 22,
    "tier": 4
  },
  "Augmentation": {
    "id": 23,
    "tier": 4
  }
}

def fetch_conversion_offers(league, want, have):
  url = "http://currency.poe.trade/search"
  params = {
    "league": league,
    "want": currencies[want]["id"],
    "have": currencies[have]["id"],
    "online": True
  }

  r = requests.get(url, params=params)
  offers = parse_conversion_offers(r.text)
  viable_offers = filter_viable_offers(want, have, offers)

  return {
    "offers": viable_offers,
    "want": want,
    "have": have,
    "league": league
  }


def filter_viable_offers(want, have, offers):
  return [x for x in offers if is_offer_viable(want, have, x) == True]


def is_offer_viable(want, have, offer):
  # lower tier value means higher value
  have_tier = currencies[have]["tier"]
  want_tier = currencies[want]["tier"]
  conversion_rate = offer["conversion_rate"]

  # if `want` is worth more than `have`, the conversion rate cannot be bigger than 1
  if have_tier > want_tier and conversion_rate > 1:
    return False
  # if `have` is worth more than `have`, the conversion rate cannot be smaller than 1
  if have_tier < want_tier and conversion_rate < 1:
    return False
  return True


def parse_conversion_offers(html):
  soup = BeautifulSoup(html, "html.parser")
  rows = soup.find_all(class_="displayoffer")
  parsed_rows = [parse_conversion_offer(x) for x in rows]
  return [x for x in parsed_rows if x != None][:5]


def parse_conversion_offer(offer_html):

  if "data-stock" not in offer_html.attrs:
    return None

  sellvalue = float(offer_html["data-sellvalue"])
  buyvalue = float(offer_html["data-buyvalue"])
  conversion_rate = round(sellvalue/buyvalue, 4)
  stock = int(offer_html["data-stock"])

  return {
    "contact_ign": offer_html["data-ign"],
    "conversion_rate": conversion_rate,
    "stock": stock
  }

