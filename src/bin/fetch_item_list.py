import json
import logging
# import pickle
# import sys

from src.trading.items import ItemList
from src.commons import init_logger
import cattr

init_logger(False)

item_list = ItemList.generate()

(n_unsynced_items, unsynced_items) = item_list.find_discrepancies()
logging.info("Item supports counts per backend: ", n_unsynced_items)
logging.info("{} items without full backend support".format(
    len(unsynced_items)))
for item in unsynced_items:
    logging.info(item)

with open("assets/items.json", "w") as f:
    json.dump(cattr.unstructure(item_list), f, indent=2)
    # sys.setrecursionlimit(1000000)
    # pickle.dump(item_list, f)
