from src import constants

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
  have_tier = constants.currencies[have]["tier"]
  want_tier = constants.currencies[want]["tier"]
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
