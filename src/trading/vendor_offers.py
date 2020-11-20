from typing import List
from src.core.offer import Offer

raw_vendor_offers = [
    ("Orb of Regret", "Orb of Alchemy", 1),
    ("Orb of Scouring", "Orb of Regret", .5),
    ("Orb of Chance", "Orb of Scouring", .25),
    ("Orb of Fusing", "Orb of Change", 1),
    ("Jeweller's Orb", "Orb of Fusing", .25),
    ("Jeweller's Orb", "Chromatic Orb", .3333),
    ("Orb of Alteration", "Jeweller's Orb", .5),
    ("Orb of Augmentation", "Orb of Alteration", .25),
    ("Orb of Transmuation", "Orb of Augmentation", .25),
    ("Portal Scroll", "Orb of Transmutation", .1429),
    ("Scroll of Wisdom", "Portal Scroll", 1),
]


def build_vendor_offers(league: str) -> List[Offer]:
    ret: List[Offer] = []

    for raw in raw_vendor_offers:
        (sell, buy, conversion_rate) = raw
        offer = Offer(league=league,
                      contact_ign="__vendor__",
                      conversion_rate=conversion_rate,
                      have=sell,
                      want=buy,
                      stock=1_000_000)
        ret.append(offer)

    return ret
