from src.trading import StackSizeHelper
from dataclasses import dataclass
from typing import Dict
import json


@dataclass
class StockSizeItem:
    name: str
    min: int
    max: int

    def __init__(self, name: str, min: int, max: int):
        self.name = name
        self.min = min
        self.max = max


class StockSizeHelper:
    stack_sizes: StackSizeHelper = StackSizeHelper()

    stock_sizes: Dict[str, StockSizeItem]

    @staticmethod
    def load_from_file(path: str):
        if path is None:
            path = "config.yaml"
        with open(path, "r") as f:
            data: Dict[str, Dict[str, int]] = json.loads(f)

            stock_sizes = dict()
            for name in data.keys():
                item = StockSizeItem(name, data[name]["min"], data[name]["max"])
                stock_sizes[name] = item

            StockSizeHelper(stock_sizes)

    def __init__(self, stock_sizes: Dict[str, StockSizeItem]):
        self.stock_sizes = stock_sizes

    def get_stock_sizes(self, name: str) -> StockSizeItem:
        if name in self.stock_sizes.keys():
            return self.stock_sizes.get(name)
        else:
            return StockSizeItem(name, 1, self.stack_sizes.get_stack_size(name))
