from src.trading.items import ItemList
import pickle
import sys


item_list = ItemList.generate()

(n_unsynced_items, unsynced_items) = item_list.find_discrepancies()
print("Item counts:", n_unsynced_items)
print("Encountered {} unsynced items".format(len(unsynced_items)))
for item in unsynced_items:
    print(item)

with open("assets/items.pickle", "wb") as f:
    sys.setrecursionlimit(1000000)
    pickle.dump(item_list, f)
