from __future__ import annotations

from typing import Dict, NewType, Optional, Tuple
from marshmallow import Schema, fields, post_load
import os
import json

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


class TradingConfigItemSellItemSchema(Schema):
    minimum_stock = fields.Int(allow_none=True, default=0)
    maximum_stock = fields.Int(allow_none=True, default=INT_INFINITY)

    @post_load
    def make_trading_config_item_sell_item(self, data, many, partial):
        return TradingConfigItemSellItem(**data)


class TradingConfigItem:
    minimum_stock: int
    maximum_stock: int
    sell_for: Dict[str, Optional[TradingConfigItemSellItem]]

    def __init__(self, sell_for: Dict[str, Optional[TradingConfigItemSellItem]] = {}, minimum_stock: int = 0, maximum_stock: int = INT_INFINITY):
        self.minimum_stock = minimum_stock
        self.maximum_stock = maximum_stock
        self.sell_for = sell_for


class TradingConfigItemSchema(Schema):
    minimum_stock = fields.Int(allow_none=True, default=0)
    maximum_stock = fields.Int(allow_none=True, default=INT_INFINITY)
    sell_for = fields.Dict(keys=fields.Str(), values=fields.Nested(TradingConfigItemSellItemSchema, allow_none=True), allow_none=True)

    @post_load
    def make_trading_config_item(self, data, many, partial):
        print(data)
        return TradingConfigItem(**data)


AssetConfig = NewType("AssetConfig", Dict[str, int])
TradingConfig = NewType("TradingConfig", Dict[str, TradingConfigItem])


class UserConfigSchema(Schema):
    version = fields.Int()
    assets = fields.Dict(keys=fields.Str(), values=fields.Int())
    trading = fields.Dict(keys=fields.Str(), values=fields.Nested(TradingConfigItemSchema, allow_none=True), allow_none=True)

    @post_load
    def make_user_config(self, data, many, partial):
        return UserConfig(**data)


class UserConfig:
    version: int
    assets: AssetConfig
    trading: TradingConfig
    stack_sizes: StackSizeHelper

    def __init__(self, version: int, assets: AssetConfig, trading: TradingConfig):
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
                data = json.loads(f.read())
                return UserConfigSchema().load(data)
        except OSError:
            raise Exception("The specified config file path does not exist")

    @staticmethod
    def from_raw(raw: str) -> UserConfig:  # noqa F821
        data = json.loads(raw)
        return UserConfigSchema().load(data)
