import confuse
import os

ENV = 'dev'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = confuse.Configuration('exchange-monitor')
CONFIG.set_file(os.path.join(BASE_DIR, './config/prod_config.yaml'))


