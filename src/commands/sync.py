from src.config.user_config import UserConfig


def execute_sync(user_config: UserConfig):
    if user_config.account_name == None:
        raise Exception("Missing accountName in config file")
    if user_config.poe_session_id == None:
        raise Exception("Missing POESESSID in config file")

    print(user_config.poe_session_id)
    print(user_config.account_name)