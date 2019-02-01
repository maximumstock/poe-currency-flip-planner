import unittest
from src.items import load_items, build_item_list_poetrade


class ItemTest(unittest.TestCase):
    def test_items_loading(self):
        data = load_items("poetrade")
        self.assertIsInstance(data, dict)
        assert len(data.keys()) > 600

        data = load_items("poeofficial")
        self.assertIsInstance(data, dict)

    def test_build_items_list(self):
        data = [
            {
                "id": 4,
                "name": "Chaos Orb",
                "currency": True,
                "non_currency_sales_target": True,
            },
            {
                "id": 6,
                "name": "Exalted Orb",
                "currency": True,
                "non_currency_sales_target": True,
            },
            {
                "id": 7,
                "name": "Chromatic Orb",
                "currency": True,
                "non_currency_sales_target": False,
            },
            {
                "id": 26,
                "name": "Perandus Coin",
                "currency": False,
                "non_currency_sales_target": False,
            },
            {
                "id": 27,
                "name": "Sacrifice at Dusk",
                "currency": False,
                "non_currency_sales_target": False,
            },
            {
                "id": 28,
                "name": "Sacrifice at Midnight",
                "currency": False,
                "non_currency_sales_target": False,
            },
        ]
        poetrade_pairs = build_item_list_poetrade(data, {"use_bulk_items": True})
        poetrade_pairs = list(
            sorted(map(lambda x: (x[0]["name"], x[1]["name"]), poetrade_pairs))
        )
        expected_result = sorted(
            [
                ("Chaos Orb", "Exalted Orb"),
                ("Chaos Orb", "Chromatic Orb"),
                ("Exalted Orb", "Chaos Orb"),
                ("Exalted Orb", "Chromatic Orb"),
                ("Chromatic Orb", "Chaos Orb"),
                ("Chromatic Orb", "Exalted Orb"),
                ("Chaos Orb", "Perandus Coin"),
                ("Exalted Orb", "Perandus Coin"),
                ("Chaos Orb", "Sacrifice at Dusk"),
                ("Exalted Orb", "Sacrifice at Dusk"),
                ("Chaos Orb", "Sacrifice at Midnight"),
                ("Exalted Orb", "Sacrifice at Midnight"),
                ("Sacrifice at Dusk", "Chaos Orb"),
                ("Sacrifice at Dusk", "Exalted Orb"),
                ("Sacrifice at Midnight", "Chaos Orb"),
                ("Sacrifice at Midnight", "Exalted Orb"),
                ("Perandus Coin", "Chaos Orb"),
                ("Perandus Coin", "Exalted Orb"),
            ]
        )
        self.assertEqual(len(poetrade_pairs), len(expected_result))
        self.assertListEqual(poetrade_pairs, expected_result)
