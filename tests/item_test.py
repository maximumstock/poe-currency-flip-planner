import unittest
from src.trading.items import ItemList


class ItemListTest(unittest.TestCase):
    def test_load_itemlist_from_file(self):
        item_list = ItemList.load_from_file()
        self.assertTrue(len(item_list.items) > 800)
