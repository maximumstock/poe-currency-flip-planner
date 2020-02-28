from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, NewType, Optional
import json
import os

from src.trading import StackSizeHelper

DEFAULT_CONFIG_FILE_PATH = "config/config.json"
DEFAULT_CONFIG_DEFAULT_FILE_PATH = "config/config.default.json"


@dataclass
class TradingConfigItemSellItem:
    minimum_stock: int
    maximum_stock: int


@dataclass
class TradingConfigItem:
    minimum_stock: int
    maximum_stock: int
    sell_for: Dict[str, Optional[TradingConfigItemSellItem]]


AssetConfig = NewType("AssetConfig", Dict[str, int])
TradingConfig = NewType("TradingConfig", Dict[str, TradingConfigItem])


class UserConfig:
    version: int
    assets: AssetConfig
    trading: TradingConfig
    stack_sizes: StackSizeHelper

    def __init__(self, raw: str):
        self.__dict__ = json.loads(raw)
        self.stack_sizes = StackSizeHelper()
        self.__validate()

    def __validate(self):
        try:
            assert (self.__dict__["version"] is not None)
            assert (self.__dict__["assets"] is not None)
            assert (self.__dict__["trading"] is not None)
        except AssertionError:
            raise Exception("Seems like your config file is malformed")

    def get_maximum_trade_volume_for_item(self, item: str) -> int:
        """
        Returns the maximum amount of @item you want to or can trade with.
        Factors in:
            - how much you have (see config.json assets)
            - stack sizes, ie. how much you can transfer with one inventory
        """
        # The maximum tradeable volume based on one full inventory
        max_tradeable_volume = self.stack_sizes.get_maximum_volume_for_item(item)
        # The maximum volume the user has to trade
        max_sellable_volume = self.assets.get(item, math.inf)
        # The effective maximum volume that is possible in a trade
        max_volume = min(max_tradeable_volume, max_sellable_volume)

        return max_volume

    @staticmethod
    def from_file(file_path: Optional[str] = None) -> UserConfig:
        if file_path is None:
            file_path = DEFAULT_CONFIG_FILE_PATH

        if not os.path.exists(file_path):
            file_path = DEFAULT_CONFIG_DEFAULT_FILE_PATH

        try:
            with open(file_path, "r") as f:
                return UserConfig(f.read())
        except OSError:
            raise Exception("The specified config file path does not exist")
