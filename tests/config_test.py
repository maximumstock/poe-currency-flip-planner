from src.config.user_config import UserConfig, DEFAULT_CONFIG_DEFAULT_FILE_PATH
import unittest
import json


class UserConfigTest(unittest.TestCase):
    def test_deserialize_user_config_with_correct_defaults(self):
        raw = {
            "version": 1,
            "trading": {
                "Chaos Orb": {}
            },
            "assets": {},
        }
        raw = json.dumps(raw)
        user_config = UserConfig.from_raw(raw)
        self.assert_is_user_config(user_config)

        x = user_config.trading["Chaos Orb"]
        assert (x.minimum_stock == 0)
        assert (x.maximum_stock != 0)
        assert (type(x.sell_for) is dict)

        self.assertEqual(user_config.poe_session_id, None)
        self.assertEqual(user_config.account_name, None)

    def test_deserialize_user_config(self):
        raw = {
            "version": 1,
            "trading": {
                "Chaos Orb": {}
            },
            "assets": {},
            "POESESSID": "123",
            "accountName": "herpderp"
        }
        raw = json.dumps(raw)
        user_config = UserConfig.from_raw(raw)
        self.assert_is_user_config(user_config)

        x = user_config.trading["Chaos Orb"]
        assert (x.minimum_stock == 0)
        assert (x.maximum_stock != 0)
        assert (type(x.sell_for) is dict)

        self.assertEqual(user_config.poe_session_id, "123")
        self.assertEqual(user_config.account_name, "herpderp")

    def test_load_default_user_config_from_file(self):
        user_config = UserConfig.from_file(DEFAULT_CONFIG_DEFAULT_FILE_PATH)
        self.assert_is_user_config(user_config)

    def assert_is_user_config(self, obj: UserConfig):
        assert (hasattr(obj, "version"))
        assert (hasattr(obj, "trading"))
        assert (hasattr(obj, "assets"))
        assert (hasattr(obj, "poe_session_id"))
        assert (hasattr(obj, "account_name"))
