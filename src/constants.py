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
Divine

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
Vaal

Chance
Alteration
Augmentation
Transmutation
"""
currencies = {
  "Orb of Alteration": {
    "poetrade": 1,
    "poeofficial": "alt",
    "tier": 3
  },
  "Orb of Fusing": {
    "poetrade": 2,
    "poeofficial": "fuse",
    "tier": 2
  },
  "Orb of Alchemy": {
    "poetrade": 3,
    "poeofficial": "alch",
    "tier": 2
  },
  "Chaos Orb": {
    "poetrade": 4,
    "poeofficial": "chaos",
    "tier": 2
  },
  "Gemcutter's Prism": {
    "poetrade": 5,
    "poeofficial": "gcp",
    "tier": 2
  },
  "Exalted Orb": {
    "poetrade": 6,
    "poeofficial": "exa",
    "tier": 1
  },
  "Chromatic Orb": {
    "poetrade": 7,
    "poeofficial": "chrom",
    "tier": 2
  },
  "Jewellers Orb": {
    "poetrade": 8,
    "poeofficial": "jew",
    "tier": 2
  },
  "Orb of Chance": {
    "poetrade": 9,
    "poeofficial": "chance",
    "tier": 2
  },
  "Cartographer's Chisel": {
    "poetrade": 10,
    "poeofficial": "chisel",
    "tier": 2
  },
  "Orb of Scouring": {
    "poetrade": 11,
    "poeofficial": "scour",
    "tier": 2
  },
  "Orb of Regret": {
    "poetrade": 13,
    "poeofficial": "regret",
    "tier": 2
  },
  "Regal Orb": {
    "poetrade": 14,
    "poeofficial": "regal",
    "tier": 2
  },
  "Divine Orb": {
    "poetrade": 15,
    "poeofficial": "divine",
    "tier": 2
  },
  "Vaal Orb": {
    "poetrade": 16,
    "poeofficial": "vaal",
    "tier": 2
  },
  "Orb of Transmutation": {
    "poetrade": 22,
    "poeofficial": "tra",
    "tier": 3
  },
  "Orb of Augmentation": {
    "poetrade": 23,
    "poeofficial": "aug",
    "tier": 3
  }
}
