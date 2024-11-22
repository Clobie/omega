import configparser
import os

class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        for section in config.sections():
            for key, value in config[section].items():
                if value == 'ENV':
                    env_value = os.getenv(key.upper())
                    if env_value is None:
                        print(f"Error: Environment variable {key.upper()} not found.")
                    else:
                        print(f"Info: Environment variable {key.upper()} found.")
                        setattr(self, key.upper(), env_value)
                else:
                    setattr(self, key.upper(), value)

    def save_config(self):
        config = configparser.ConfigParser()
        attrs = vars(self)
        config['DEFAULT'] = {k.lower(): str(v) for k, v in attrs.items() if k.isupper()}
        with open(self.config_path, 'w') as configfile:
            config.write(configfile)

    def set_variable(self, key, value):
        if not key.isidentifier():
            raise ValueError("Invalid key format.")
        if not isinstance(value, (str, int, float, bool)):
            raise ValueError("Invalid value type.")
        setattr(self, key.upper(), value)
        self.save_config()

    def get_variable(self, key, default=None):
        return getattr(self, key.upper(), default)
    
    def variable_exists(self, key):
        return hasattr(self, key.upper())
    
    def get_all_variables(self):
        return (key for key, value in vars(self).items() if key.isupper())

    def print_config(self):
        attrs = vars(self)
        for key, value in attrs.items():
            print(f"{key} = {value}")

config = Config('./config/bot.conf')