from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, NewType, Optional
import json

DEFAULT_CONFIG_FILE_PATH = "config/config.json"


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

    def __init__(self, raw: str):
        self.__dict__ = json.loads(raw)
        self.__validate()

    def __validate(self):
        try:
            assert(self.__dict__["version"] != None)
            assert(self.__dict__["assets"] != None)
            assert(self.__dict__["trading"] != None)
        except:
            raise Exception("Seems like your config file is malformed")

    @staticmethod
    def from_file(file_path: Optional[str]) -> UserConfig:
        if file_path is None:
            file_path = DEFAULT_CONFIG_FILE_PATH
        with open(file_path, "r") as f:
            return UserConfig(f.read())
