import unittest
from src.trading.items import ItemList

item_list = ItemList.load_from_file()

class ItemListTest(unittest.TestCase):
    def test_loading_itemlist_from_fs(self):
        item_list: ItemList = ItemList.load_from_file()
        self.assertTrue(len(item_list.items) > 800)
