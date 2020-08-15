import unittest

from src.config.user_config import UserConfig
from src.core.graph import build_graph, find_paths, build_conversion, is_profitable
from src.core.offer import Offer
from src.core.edge import Edge
from typing import List, Dict

LEAGUE = "Abyss"

test_offers: List[Offer] = [
    Offer(
        contact_ign="KnifeySpooneyClaw",
        conversion_rate=0.0893,
        stock=153,
        want="Chaos",
        have="Alteration",
        league="Abyss",
    ),
    Offer(
        contact_ign="_ZEUS___",
        conversion_rate=0.0909,
        stock=10,
        want="Chaos",
        have="Chromatic",
        league="Abyss",
    ),
    Offer(
        contact_ign="MVP_Kefir",
        conversion_rate=0.087,
        stock=20,
        want="Chaos",
        have="Chromatic",
        league="Abyss",
    ),
    Offer(
        contact_ign="wreddnuy",
        conversion_rate=12.0,
        stock=24,
        want="Alteration",
        have="Chaos",
        league="Abyss",
    ),
    Offer(
        contact_ign="Corailthedog",
        conversion_rate=11.0,
        stock=2,
        want="Alteration",
        have="Chaos",
        league="Abyss",
    ),
    Offer(
        contact_ign="Marcvz_GreenAgain",
        conversion_rate=0.7143,
        stock=222,
        want="Alteration",
        have="Chromatic",
        league="Abyss",
    ),
    Offer(
        contact_ign="Azure_Dragon",
        conversion_rate=1.0101,
        stock=4261,
        want="Alteration",
        have="Chromatic",
        league="Abyss",
    ),
    Offer(
        contact_ign="MinerinoAbysss",
        conversion_rate=11.1,
        stock=322,
        want="Chromatic",
        have="Chaos",
        league="Abyss",
    ),
    Offer(
        contact_ign="The_Dank_Fire_God",
        conversion_rate=11.5,
        stock=106,
        want="Chromatic",
        have="Chaos",
        league="Abyss",
    ),
    Offer(
        contact_ign="Shioua_ouah",
        conversion_rate=0.6897,
        stock=1576,
        want="Chromatic",
        have="Alteration",
        league="Abyss",
    ),
    Offer(
        contact_ign="Ashkeri",
        conversion_rate=0.7143,
        stock=449,
        want="Chromatic",
        have="Alteration",
        league="Abyss",
    ),
]

expected_graph: Dict[str, Dict[str, List[Offer]]] = {
    "Alteration": {
        "Chaos": [
            Offer(league=LEAGUE,
                  want="Chaos",
                  have="Alteration",
                  contact_ign="KnifeySpooneyClaw",
                  conversion_rate=0.0893,
                  stock=153),
        ],
        "Chromatic": [
            Offer(league=LEAGUE,
                  want="Chromatic",
                  have="Alteration",
                  contact_ign="Shioua_ouah",
                  conversion_rate=0.6897,
                  stock=1576),
            Offer(league=LEAGUE,
                  want="Chromatic",
                  have="Alteration",
                  contact_ign="Ashkeri",
                  conversion_rate=0.7143,
                  stock=449),
        ],
    },
    "Chaos": {
        "Alteration": [
            Offer(league=LEAGUE,
                  want="Alteration",
                  have="Chaos",
                  contact_ign="wreddnuy",
                  conversion_rate=12.0,
                  stock=24),
            Offer(league=LEAGUE,
                  want="Alteration",
                  have="Chaos",
                  contact_ign="Corailthedog",
                  conversion_rate=11.0,
                  stock=2),
        ],
        "Chromatic": [
            Offer(league=LEAGUE,
                  want="Chromatic",
                  have="Chaos",
                  contact_ign="MinerinoAbysss",
                  conversion_rate=11.1,
                  stock=322),
            Offer(league=LEAGUE,
                  want="Chromatic",
                  have="Chaos",
                  contact_ign="The_Dank_Fire_God",
                  conversion_rate=11.5,
                  stock=106),
        ],
    },
    "Chromatic": {
        "Chaos": [
            Offer(league=LEAGUE,
                  want="Chaos",
                  have="Chromatic",
                  contact_ign="_ZEUS___",
                  conversion_rate=0.0909,
                  stock=10),
            Offer(league=LEAGUE,
                  want="Chaos",
                  have="Chromatic",
                  contact_ign="MVP_Kefir",
                  conversion_rate=0.087,
                  stock=20),
        ],
        "Alteration": [
            Offer(league=LEAGUE,
                  want="Alteration",
                  have="Chromatic",
                  contact_ign="Marcvz_GreenAgain",
                  conversion_rate=0.7143,
                  stock=222),
            Offer(league=LEAGUE,
                  want="Alteration",
                  have="Chromatic",
                  contact_ign="Azure_Dragon",
                  conversion_rate=1.0101,
                  stock=4261),
        ],
    },
}

# Below structures are modified for simpler testing => number reduced, offers slightly changed

# Expected graph when trading from Chaos to Chaos over one other currency
expected_graph_small: Dict[str, Dict[str, List[Offer]]] = {
    "Chaos": {
        "Alteration": [
            Offer(contact_ign="wreddnuy",
                  conversion_rate=12.0,
                  stock=100,
                  league=LEAGUE,
                  have="Chaos",
                  want="Alteration")
        ]
    },
    "Alteration": {
        "Chromatic": [
            Offer(contact_ign="Ashkeri",
                  conversion_rate=0.7143,
                  stock=449,
                  league=LEAGUE,
                  have="Chaos",
                  want="Alteration"),
            Offer(contact_ign="Shioua_ouah",
                  conversion_rate=0.6897,
                  stock=1576,
                  league=LEAGUE,
                  have="Chaos",
                  want="Alteration")
        ]
    },
    "Chromatic": {
        "Chaos": [
            Offer(contact_ign="MVP_Kefir",
                  conversion_rate=0.087,
                  stock=20,
                  league=LEAGUE,
                  have="Chromatic",
                  want="Chaos"),
            Offer(contact_ign="_ZEUS___",
                  conversion_rate=0.0909,
                  stock=100,
                  league=LEAGUE,
                  have="Chromatic",
                  want="Chaos"),
        ]
    },
}

# Expected paths from Chaos to Chaos


def expected_paths_small_same_currency() -> List[List[Offer]]:
    return [
        [
            Offer(contact_ign="wreddnuy",
                  conversion_rate=12.0,
                  stock=100,
                  have="Chaos",
                  want="Alteration",
                  league=LEAGUE),
            Offer(contact_ign="Shioua_ouah",
                  conversion_rate=0.6897,
                  stock=1576,
                  have="Alteration",
                  want="Chromatic",
                  league=LEAGUE),
            Offer(contact_ign="MVP_Kefir",
                  conversion_rate=0.087,
                  stock=20,
                  have="Chromatic",
                  want="Chaos",
                  league=LEAGUE),
        ],
        [
            Offer(contact_ign="wreddnuy",
                  conversion_rate=12.0,
                  stock=100,
                  have="Chaos",
                  want="Alteration",
                  league=LEAGUE),
            Offer(contact_ign="Shioua_ouah",
                  conversion_rate=0.6897,
                  stock=1576,
                  have="Alteration",
                  want="Chromatic",
                  league=LEAGUE),
            Offer(contact_ign="_ZEUS___",
                  conversion_rate=0.0909,
                  stock=100,
                  have="Chromatic",
                  want="Chaos",
                  league=LEAGUE)
        ],
        [
            Offer(contact_ign="wreddnuy",
                  conversion_rate=12.0,
                  stock=100,
                  have="Chaos",
                  want="Alteration",
                  league=LEAGUE),
            Offer(contact_ign="Ashkeri",
                  conversion_rate=0.7143,
                  stock=449,
                  have="Alteration",
                  want="Chromatic",
                  league=LEAGUE),
            Offer(contact_ign="MVP_Kefir",
                  conversion_rate=0.087,
                  stock=200,
                  have="Chromatic",
                  want="Chaos",
                  league=LEAGUE),
        ],
        [
            Offer(contact_ign="wreddnuy",
                  conversion_rate=12.0,
                  stock=100,
                  have="Chaos",
                  want="Alteration",
                  league=LEAGUE),
            Offer(contact_ign="Ashkeri",
                  conversion_rate=0.7143,
                  stock=449,
                  have="Alteration",
                  want="Chromatic",
                  league=LEAGUE),
            Offer(contact_ign="_ZEUS___",
                  conversion_rate=0.0909,
                  stock=100,
                  have="Chromatic",
                  want="Chaos",
                  league=LEAGUE)
        ],
    ]


def expected_profitable_paths_small_same_currency():
    return []


expected_conversion = {
    "from":
    "Chaos",
    "to":
    "Chaos",
    "starting":
    8,
    "ending":
    5,
    "winnings":
    -3,
    "transactions": [
        Edge(offer=Offer(contact_ign="wreddnuy",
                         want="Alteration",
                         have="Chaos",
                         conversion_rate=12.0,
                         league=LEAGUE,
                         stock=100),
             paid=8,
             received=96),
        Edge(offer=Offer(contact_ign="Shioua_ouah",
                         want="Chromatic",
                         have="Alteration",
                         conversion_rate=0.6897,
                         league=LEAGUE,
                         stock=1576),
             paid=96,
             received=66),
        Edge(offer=Offer(contact_ign="MVP_Kefir",
                         want="Chaos",
                         have="Chromatic",
                         conversion_rate=0.087,
                         league=LEAGUE,
                         stock=20),
             paid=66,
             received=5),
    ],
}

user_config = UserConfig.from_file()


class GraphTest(unittest.TestCase):
    def test_build_graph(self):
        graph = build_graph(test_offers)
        self.assertDictEqual(graph, expected_graph)

    def test_find_paths(self):
        paths_small_same_currency = find_paths(expected_graph_small, "Chaos",
                                               "Chaos", user_config)
        self.assertListEqual(expected_profitable_paths_small_same_currency(),
                             paths_small_same_currency)

    def test_is_profitable(self):
        path = expected_paths_small_same_currency()[0]
        self.assertEqual(False, is_profitable(path))

    def test_build_non_profitable_conversions(self):
        path = expected_paths_small_same_currency()[0]
        conversion = build_conversion(path, user_config)
        self.assertEqual(expected_conversion, conversion)
