import unittest
from src.graph import *


test_offers = [{
  'offers': [
    {'contact_ign': 'KnifeySpooneyClaw', 'conversion_rate': 0.0893, 'stock': 153}
  ],
  'want': 'Chaos',
  'have': 'Alteration',
  'league': 'Abyss'
}, {
  'offers': [
    {'contact_ign': '_ZEUS___', 'conversion_rate': 0.0909, 'stock': 10},
    {'contact_ign': 'MVP_Kefir', 'conversion_rate': 0.087, 'stock': 20}
  ],
  'want': 'Chaos',
  'have': 'Chromatic',
  'league': 'Abyss'
}, {
  'offers': [
    {'contact_ign': 'wreddnuy', 'conversion_rate': 12.0, 'stock': 24},
    {'contact_ign': 'Corailthedog', 'conversion_rate': 11.0, 'stock': 2}
  ],
  'want': 'Alteration',
  'have': 'Chaos',
  'league': 'Abyss'
}, {
  'offers': [
    {'contact_ign': 'Azure_Dragon', 'conversion_rate': 1.0101, 'stock': 4261},
    {'contact_ign': 'Marcvz_GreenAgain', 'conversion_rate': 0.7143, 'stock': 222}
  ],
    'want': 'Alteration',
    'have': 'Chromatic',
    'league': 'Abyss'
}, {
  'offers': [
    {'contact_ign': 'The_Dank_Fire_God', 'conversion_rate': 11.5, 'stock': 106},
    {'contact_ign': 'MinerinoAbysss', 'conversion_rate': 11.1, 'stock': 322}
  ],
  'want': 'Chromatic',
  'have': 'Chaos',
  'league': 'Abyss'
}, {
  'offers': [
    {'contact_ign': 'Ashkeri', 'conversion_rate': 0.7143, 'stock': 449},
    {'contact_ign': 'Shioua_ouah', 'conversion_rate': 0.6897, 'stock': 1576}
  ],
  'want': 'Chromatic',
  'have': 'Alteration',
  'league': 'Abyss'
}]

expected_graph = {
  'Chaos': {
    'Alteration': [
      {'contact_ign': 'wreddnuy', 'conversion_rate': 12.0, 'stock': 24},
      {'contact_ign': 'Corailthedog', 'conversion_rate': 11.0, 'stock': 2}
    ],
    'Chromatic': [
      {'contact_ign': 'The_Dank_Fire_God', 'conversion_rate': 11.5, 'stock': 106},
      {'contact_ign': 'MinerinoAbysss', 'conversion_rate': 11.1, 'stock': 322}
    ]
  },
  'Alteration': {
    'Chaos': [
      {'contact_ign': 'KnifeySpooneyClaw', 'conversion_rate': 0.0893, 'stock': 153}
    ],
    'Chromatic': [
      {'contact_ign': 'Ashkeri', 'conversion_rate': 0.7143, 'stock': 449},
      {'contact_ign': 'Shioua_ouah', 'conversion_rate': 0.6897, 'stock': 1576}
    ]
  },
  'Chromatic': {
    'Chaos': [
      {'contact_ign': '_ZEUS___', 'conversion_rate': 0.0909, 'stock': 10},
      {'contact_ign': 'MVP_Kefir', 'conversion_rate': 0.087, 'stock': 20}
    ],
    'Alteration': [
      {'contact_ign': 'Azure_Dragon', 'conversion_rate': 1.0101, 'stock': 4261},
      {'contact_ign': 'Marcvz_GreenAgain', 'conversion_rate': 0.7143, 'stock': 222}
    ]
  }
}



### Below structures are modified for simpler testing => number reduced, offers slightly changed


# Exptected graph when trading from Chaos to Chaos over one other currency
expected_graph_small = {
  'Chaos': {
    'Alteration': [
      {'contact_ign': 'wreddnuy', 'conversion_rate': 12.0, 'stock': 100}
    ]
  },
  'Alteration': {
    'Chromatic': [
      {'contact_ign': 'Ashkeri', 'conversion_rate': 0.7143, 'stock': 449},
      {'contact_ign': 'Shioua_ouah', 'conversion_rate': 0.6897, 'stock': 1576}
    ]
  },
  'Chromatic': {
    'Chaos': [
      {'contact_ign': '_ZEUS___', 'conversion_rate': 0.0909, 'stock': 100},
      {'contact_ign': 'MVP_Kefir', 'conversion_rate': 0.087, 'stock': 200}
    ]
  }
}

# Expected paths from Chaos to Chaos
def expected_paths_small_same_currency():
  return [
    [
      {'contact_ign': 'wreddnuy', 'conversion_rate': 12.0, 'stock': 100, 'have': 'Chaos', 'want': 'Alteration'},
      {'contact_ign': 'Shioua_ouah', 'conversion_rate': 0.6897, 'stock': 1576, 'have': 'Alteration', 'want': 'Chromatic'},
      {'contact_ign': 'MVP_Kefir', 'conversion_rate': 0.087, 'stock': 200, 'have': 'Chromatic', 'want': 'Chaos'}
    ], [
      {'contact_ign': 'wreddnuy', 'conversion_rate': 12.0, 'stock': 100, 'have': 'Chaos', 'want': 'Alteration'},
      {'contact_ign': 'Shioua_ouah', 'conversion_rate': 0.6897, 'stock': 1576, 'have': 'Alteration', 'want': 'Chromatic'},
      {'contact_ign': '_ZEUS___', 'conversion_rate': 0.0909, 'stock': 100, 'have': 'Chromatic', 'want': 'Chaos'}
    ], [
      {'contact_ign': 'wreddnuy', 'conversion_rate': 12.0, 'stock': 100, 'have': 'Chaos', 'want': 'Alteration'},
      {'contact_ign': 'Ashkeri', 'conversion_rate': 0.7143, 'stock': 449, 'have': 'Alteration', 'want': 'Chromatic'},
      {'contact_ign': 'MVP_Kefir', 'conversion_rate': 0.087, 'stock': 200, 'have': 'Chromatic', 'want': 'Chaos'}
    ], [
      {'contact_ign': 'wreddnuy', 'conversion_rate': 12.0, 'stock': 100, 'have': 'Chaos', 'want': 'Alteration'},
      {'contact_ign': 'Ashkeri', 'conversion_rate': 0.7143, 'stock': 449, 'have': 'Alteration', 'want': 'Chromatic'},
      {'contact_ign': '_ZEUS___', 'conversion_rate': 0.0909, 'stock': 100, 'have': 'Chromatic', 'want': 'Chaos'}
    ]
  ]


# Expected paths from Chaos to Chromatics
# This is not really relevant to us, since we only care about trade paths between the same currency in order to
# guarantee easily comparable results. However, it's good to make sure that the path exploration also works for this
# edge case
expected_paths_small_different_currency = [
  [
    {'contact_ign': 'wreddnuy', 'conversion_rate': 12.0, 'stock': 100, 'have': 'Chaos', 'want': 'Alteration'},
    {'contact_ign': 'Shioua_ouah', 'conversion_rate': 0.6897, 'stock': 1576, 'have': 'Alteration', 'want': 'Chromatic'}
  ], [
    {'contact_ign': 'wreddnuy', 'conversion_rate': 12.0, 'stock': 100, 'have': 'Chaos', 'want': 'Alteration'},
    {'contact_ign': 'Ashkeri', 'conversion_rate': 0.7143, 'stock': 449, 'have': 'Alteration', 'want': 'Chromatic'}
  ]
]


expected_conversion = {
  "from": "Chaos",
  "to": "Chaos",
  "starting": 8,
  "ending": 5,
  "winnings": -3,
  "transactions": [{
    "contact_ign": "wreddnuy",
    "from": "Chaos",
    "to": "Alteration",
    "paid": 8,
    "received": 96
  }, {
    "contact_ign": "Shioua_ouah",
    "from": "Alteration",
    "to": "Chromatic",
    "paid": 96,
    "received": 66
  }, {
    "contact_ign": "MVP_Kefir",
    "from": "Chromatic",
    "to": "Chaos",
    "paid": 66,
    "received": 5
  }]
}


class GraphTest(unittest.TestCase):
  def test_build_graph(self):
    graph = build_graph(test_offers)
    self.assertDictEqual(graph, expected_graph)

  def test_find_paths(self):
    paths_small_same_currency = find_paths(expected_graph_small, 'Chaos', 'Chaos')
    self.assertListEqual(expected_paths_small_same_currency(), paths_small_same_currency)
    paths_small_different_currency = find_paths(expected_graph_small.copy(), 'Chaos', 'Chromatic')
    self.assertListEqual(expected_paths_small_different_currency, paths_small_different_currency)

  def test_is_profitable(self):
    path = expected_paths_small_same_currency()[0]
    self.assertEqual(False, is_profitable(path))

  def test_build_conversions(self):
    path = expected_paths_small_same_currency()[0]
    conversion = build_conversion(path)
    print(conversion)
    self.assertDictEqual(expected_conversion, conversion)
