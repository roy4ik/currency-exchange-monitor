import os

ENV = os.environ.get("ENV", "DEV")
if ENV == "DEV":
    import settings.local_settings as local_settings
    settings = local_settings
else:
    import settings.prod_settings as prod_settings
    settings = prod_settings


def read_key_from_file(key_name, parent=None):
    key = settings.CONFIG[key_name]
    if parent:
        key = settings.CONFIG[parent][key_name]
    with open(key.as_filename()) as f:
        return f.read().strip()