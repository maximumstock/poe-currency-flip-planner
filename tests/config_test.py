from src.config.user_config import UserConfig
import unittest
import json


class UserConfigTest(unittest.TestCase):
    def test_load_default_user_confg_from_fs(self):
        user_config: UserConfig = UserConfig.from_file()
        self.assert_is_user_config(user_config)

    def test_load_user_confg_with_correct_defaults(self):
        raw = {"version": 1, "trading": {"Chaos Orb": {}}, "assets": {}}
        raw = json.dumps(raw)
        user_config = UserConfig.from_raw(raw)
        self.assert_is_user_config(user_config)

        x = user_config.trading["Chaos Orb"]
        assert (x.minimum_stock == 0)
        assert (x.maximum_stock != 0)
        assert (type(x.sell_for) is dict)

    def assert_is_user_config(self, obj):
        assert (hasattr(obj, "version"))
        assert (hasattr(obj, "trading"))
        assert (hasattr(obj, "assets"))
