import os
import configparser

# Constants
CONFIG_FILE = 'config.ini'

class ConfigManager:
    @staticmethod
    def load_config():
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE)
        return config

    @staticmethod
    def save_config(config):
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
