from typing import Dict, NewType, Optional
from marshmallow import Schema, fields, post_load

DEFAULT_CONFIG_FILE_PATH = "config/config.json"
DEFAULT_CONFIG_DEFAULT_FILE_PATH = "config/config.default.json"
INT_INFINITY = 1_000_000


class TradingConfigItemSellItem:
    minimum_stock: int
    maximum_stock: int

    def __init__(self,
                 minimum_stock: int = 0,
                 maximum_stock: int = INT_INFINITY):
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

    def __init__(self,
                 sell_for: Dict[str, Optional[TradingConfigItemSellItem]] = {},
                 minimum_stock: int = 0,
                 maximum_stock: int = INT_INFINITY):
        self.minimum_stock = minimum_stock
        self.maximum_stock = maximum_stock
        self.sell_for = sell_for


class TradingConfigItemSchema(Schema):
    minimum_stock = fields.Int(allow_none=True, default=0)
    maximum_stock = fields.Int(allow_none=True, default=INT_INFINITY)
    sell_for = fields.Dict(keys=fields.Str(),
                           values=fields.Nested(
                               TradingConfigItemSellItemSchema,
                               allow_none=True),
                           allow_none=True)

    @post_load
    def make_trading_config_item(self, data, many, partial):
        return TradingConfigItem(**data)


AssetConfig = NewType("AssetConfig", Dict[str, int])
TradingConfig = NewType("TradingConfig", Dict[str, TradingConfigItem])
