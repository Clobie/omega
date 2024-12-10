# utils/config.py

import configparser
import os
import discord
from utils.log import logger

class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self.load_config()
        logger.debug(f"Config initialized with path: {config_path}")

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        for section in config.sections():
            for key, value in config[section].items():
                try:
                    if value == 'ENV':
                        env_value = os.getenv(key.upper())
                        if env_value is None:
                            logger.error(f"Environment variable {key.upper()} not found.")
                        else:
                            logger.info(f"Environment variable {key.upper()} found.")
                            setattr(self, key.upper(), env_value)
                    else:
                        if value.startswith('0x') and len(value) == 8:
                            value = discord.Color(int(value, 16))
                        setattr(self, key.upper(), value)
                except Exception as e:
                    logger.error(f"Error setting attribute {key.upper()}: {e}")

    def save_config(self):
        try:
            config = configparser.ConfigParser()
            attrs = vars(self)
            config['DEFAULT'] = {k.lower(): str(v) for k, v in attrs.items() if k.isupper()}
            with open(self.config_path, 'w') as configfile:
                config.write(configfile)
            logger.info(f"Config saved to path: {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def set_variable(self, key, value):
        try:
            if not key.isidentifier():
                raise ValueError("Invalid key format.")
            if not isinstance(value, (str, int, float, bool)):
                raise ValueError("Invalid value type.")
            setattr(self, key.upper(), value)
            logger.info(f"Variable {key.upper()} set with value: {value}")
            self.save_config()
        except Exception as e:
            logger.error(f"Error setting variable {key}: {e}")
            raise

    def get_variable(self, key, default=None):
        try:
            value = getattr(self, key.upper(), default)
            logger.debug(f"Retrieved variable {key.upper()}: {value}")
            return value
        except Exception as e:
            logger.error(f"Error retrieving variable {key}: {e}")
            return default
    
    def variable_exists(self, key):
        exists = hasattr(self, key.upper())
        logger.debug(f"Variable exists check for {key.upper()}: {exists}")
        return exists
    
    def get_all_variables(self):
        vars_list = list(self.get_all_variables())
        logger.debug(f"All variables retrieved: {vars_list}")
        return (key for key in vars_list)

    def print_config(self):
        attrs = vars(self)
        logger.info("Printing config:")
        for key, value in attrs.items():
            print(f"{key} = {value}")

cfg = Config('./config/bot.conf')