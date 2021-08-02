import confuse
import os

ENV = 'dev'
CONFIG = confuse.Configuration('exchange-monitor')
CONFIG.set_file(os.path.join(os.getcwd(), './config/prod_config.yaml'))


