import os

ENV = os.environ.get("ENV", "DEV")
if ENV == "DEV":
    import local_settings
    settings = local_settings
else:
    import prod_settings
    settings = prod_settings

