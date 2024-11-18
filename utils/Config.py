# config.py

import configparser

config_path = "./config/global.conf"

def load_config():
    config = configparser.ConfigParser()
    config.read(config_path)
    config_dict = {
        key.upper(): value
        for section in config.sections()
        for key, value in config[section].items()
    }
    return config_dict