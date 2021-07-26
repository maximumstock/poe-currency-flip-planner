from __future__ import annotations

import json
import logging
import pathlib
from typing import List, Optional, Tuple

from marshmallow import Schema, fields, post_load
from src.config.parser import (AssetConfig, TradingConfig, TradingConfigItem,
                               TradingConfigItemSchema,
                               TradingConfigItemSellItem)
from src.trading import StackSizeHelper

DEFAULT_CONFIG_FILE_PATH = "config/config.json"
DEFAULT_CONFIG_DEFAULT_FILE_PATH = "config/config.default.json"
INT_INFINITY = 1_000_000


class UserConfigSchema(Schema):
    version = fields.Int()
    assets = fields.Dict(keys=fields.Str(), values=fields.Int())
    trading = fields.Dict(keys=fields.Str(),
                          values=fields.Nested(TradingConfigItemSchema,
                                               allow_none=True),
                          allow_none=True)

    @post_load
    def make_user_config(self, data, many, partial):
        return UserConfig(**data)


class UserConfig:
    version: int
    assets: AssetConfig
    trading: TradingConfig
    stack_sizes: StackSizeHelper

    def __init__(self, version: int, assets: AssetConfig,
                 trading: TradingConfig):
        self.version = version
        self.assets = assets
        self.trading = trading
        self.stack_sizes = StackSizeHelper()

    def get_maximum_trade_volume_for_item(self, item: str) -> int:
        """
        Returns the maximum amount of @item you want to or can trade with.
        Factors in:
            - how much you have (see config.json assets)
            - stack sizes, ie. how much you can transfer with one inventory
        """
        # The maximum tradeable volume based on one full inventory
        max_tradeable_volume = self.stack_sizes.get_maximum_volume_for_item(
            item)
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
            specific_buy_config: Optional[
                TradingConfigItemSellItem] = sell_config.sell_for.get(buy)
            if specific_buy_config is not None:
                minimum = specific_buy_config.minimum_stock
                maximum = specific_buy_config.maximum_stock

        return minimum, maximum

    def get_item_pairs(self) -> List[Tuple[str, str]]:
        """
        Constructs a list of item pairs based on the specified configuration file.
        """
        item_pairs = []

        for have in self.trading:
            for want in self.trading[have].sell_for:
                item_pairs.append((have, want))

        return item_pairs

    @staticmethod
    def from_file(file_path: Optional[str] = None) -> UserConfig:
        if file_path is None:
            file_path = DEFAULT_CONFIG_FILE_PATH

        path = pathlib.Path(file_path).resolve()

        # Default back to default config file
        if not path.is_file():
            path = pathlib.Path(DEFAULT_CONFIG_DEFAULT_FILE_PATH).resolve()

        try:
            logging.info("Using config file under {}".format(path))
            with open(path, "r") as f:
                data = json.loads(f.read())
                return UserConfigSchema().load(data)
        except OSError:
            raise Exception("The specified config file path does not exist")

    @staticmethod
    def from_raw(raw: str) -> UserConfig:
        data = json.loads(raw)
        return UserConfigSchema().load(data)
