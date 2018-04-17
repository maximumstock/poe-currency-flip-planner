import requests
import itertools
from bs4 import BeautifulSoup

"""
Dictionary with all supported currencies and their tiers.
Tiers are supposed to be used later on for filtering out unrealistically good
trade offers, eg. offers from price fixers. The idea is to filter out offers
that offer a profitable trade from a lower tier into a higher tier.

For example, trading 1 Alteration into 1 Chaos should never happen under normal
considerations, hence we want to ignore these offers. Finding a suitable tier
for each currency is key to improve the overall quality of found trading paths.

Current tier setup: from 1 to 3. Trading upwards in tiers with a conversion rate
above 1 is forbidden, while trading within a tier or a tier down with any
conversion rate is fine. This is very basic at the moment.

Exalted

Chaos
Fusing
Cartographer's Chisel
Regal
Regret
Scouring
Chromatic
Alchemy
Gemcutter's Prism
Jewellers

Alteration
Augmentation
Transmutation
"""
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
    "tier": 2
  },
  "Chaos": {
    "id": 4,
    "tier": 2
  },
  "Gemcutter's Prism": {
    "id": 5,
    "tier": 2
  },
  "Exalted": {
    "id": 6,
    "tier": 1
  },
  "Chromatic": {
    "id": 7,
    "tier": 2
  },
  "Jewellers": {
    "id": 8,
    "tier": 2
  },
  "Cartographer's Chisel": {
    "id": 10,
    "tier": 2
  },
  "Scouring": {
    "id": 11,
    "tier": 2
  },
  "Regret": {
    "id": 13,
    "tier": 2
  },
  "Regal": {
    "id": 14,
    "tier": 2
  },
  "Transmutation": {
    "id": 22,
    "tier": 3
  },
  "Augmentation": {
    "id": 23,
    "tier": 3
  }
}


"""
Fetches trading offers for a specific league and a pair of currencies from
poe.trade and turns the data into a suitable format.
"""
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


"""
Filters offers for a given pair of currencies via specified tiers (see above)
to filter out unrealistically good offers.
"""
def filter_viable_offers(want, have, offers):
  return [x for x in offers if is_offer_viable(want, have, x) == True]


"""
Helper method that holds the actual logic for deciding whether an offer is too
good to be true or not.
"""
def is_offer_viable(want, have, offer):
  # lower tier value means higher value
  have_tier = currencies[have]["tier"]
  want_tier = currencies[want]["tier"]
  conversion_rate = offer["conversion_rate"]

  # if `want` is worth more than `have`, the conversion rate cannot be bigger than 1
  # This should be enough to successfully filter out price-fixing offers.
  if have_tier > want_tier and conversion_rate > 1:
    return False

  # if `have` is worth more than `have`, the conversion rate cannot be smaller than 1
  # We shouldn't need this case, since conversion rates below 1 will typically
  # result in unprofitable conversions and are therefore ignored anyway.
  # if have_tier < want_tier and conversion_rate < 1:
    # return False

  return True


"""
Helper functions to parse results from poe.trade."
"""
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

