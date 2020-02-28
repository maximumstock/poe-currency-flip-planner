from __future__ import annotations

import math
from typing import Dict, NewType, Optional, Tuple
import json
import os

from src.trading import StackSizeHelper

DEFAULT_CONFIG_FILE_PATH = "config/config.json"
DEFAULT_CONFIG_DEFAULT_FILE_PATH = "config/config.default.json"
INT_INFINITY = 1_000_000


class TradingConfigItemSellItem:
    minimum_stock: int
    maximum_stock: int

    def __init__(self, minimum_stock: int = 0, maximum_stock: int = INT_INFINITY):
        self.minimum_stock = minimum_stock
        self.maximum_stock = maximum_stock


class TradingConfigItem:
    minimum_stock: int
    maximum_stock: int
    sell_for: Dict[str, Optional[TradingConfigItemSellItem]]

    def __init__(self, minimum_stock: int = 0, maximum_stock: int = INT_INFINITY,
                 sell_for: Dict[str, Optional[TradingConfigItemSellItem]] = None):
        if sell_for is None:
            sell_for = dict()
        self.minimum_stock = minimum_stock
        self.maximum_stock = maximum_stock
        self.sell_for = sell_for


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
        max_sellable_volume = self.assets.get(item, INT_INFINITY)
        # The effective maximum volume that is possible in a trade
        max_volume = min(max_tradeable_volume, max_sellable_volume)

        return max_volume

    def get_stock_boundaries(self, sell: str, buy: str) -> Tuple[int, int]:
        """
        For a given transaction (Sell items @sell for @buy), this function returns
        lower and upper bounds for the allowed stock of the to-be-bought item.

        Eg. a user can specify that he only buys Chaos Orbs (eg. with Exalted Orbs)
        if the other party has a stock of lets say 400 - 1000.

        We first read possible default bounds for the target item (@buy) and overwrite
        the these values in case a more specific configuration is given for @sell -> @buy
        in the respective config file area.

        A more detailed example can be found here:
        https://github.com/maximumstock/poe-currency-flip-planner/issues/25#issuecomment-590097864
        """

        minimum = 0
        maximum = INT_INFINITY  # sufficiently large enough, supposedly

        # Default 'trading'.'Exalted Orb' config
        default_buy_config: Optional[TradingConfigItem] = self.trading.get(buy)
        if default_buy_config is not None:
            minimum = default_buy_config.minimum_stock
            maximum = default_buy_config.maximum_stock

        # Top level 'trading'.'Chaos Orb' config
        sell_config: Optional[TradingConfigItem] = self.trading.get(sell)
        if sell_config is not None:

            # Specific 'trading'.'Chaos Orb'.'sell_for'.'Exalted Orb' config
            # Takes precedence over defaults, so its evaluated later
            specific_buy_config: Optional[TradingConfigItemSellItem] = sell_config.sell_for.get(buy)
            if specific_buy_config is not None:
                minimum = specific_buy_config.minimum_stock
                maximum = specific_buy_config.maximum_stock

        return minimum, maximum

    @staticmethod
    def from_file(file_path: Optional[str] = None) -> UserConfig:  # noqa F821
        if file_path is None:
            file_path = DEFAULT_CONFIG_FILE_PATH

        if not os.path.exists(file_path):
            file_path = DEFAULT_CONFIG_DEFAULT_FILE_PATH

        try:
            with open(file_path, "r") as f:
                return UserConfig(f.read())
        except OSError:
            raise Exception("The specified config file path does not exist")
