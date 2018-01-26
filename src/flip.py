import requests
import itertools
from bs4 import BeautifulSoup

currencies = {
  "Alteration": 1,
  "Fusing": 2,
  "Alchemy": 3,
  "Chaos": 4,
  "Gemcutters Prism": 5,
  "Exalted": 6,
  "Chromatic": 7,
  "Jewellers": 8,
  "Regret": 13,
  "Regal": 14
}

def fetch_conversion_offers(league, want, have):
  url = "http://currency.poe.trade/search"
  params = {
    "league": league,
    "want": currencies[want],
    "have": currencies[have],
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

def parse_conversion_offers(html):
  soup = BeautifulSoup(html, "html.parser")
  rows = soup.find_all(class_="displayoffer", limit=2)
  parsed_rows = [parse_conversion_offer(x) for x in rows]
  return [x for x in parsed_rows if x != None]

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

