import confuse
import os

ENV = 'dev'
CONFIG = confuse.Configuration('exchange-monitor')
CONFIG.set_file(os.path.join(os.getcwd(), './config/prod_config.yaml'))


def read_key_from_file(key_name, parent=None):
    key = CONFIG[key_name]
    if parent:
        key = CONFIG[parent][key_name]
    with open(key.as_filename()) as f:
        return f.read().strip()
