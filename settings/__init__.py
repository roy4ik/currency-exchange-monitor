import os

ENV = os.environ.get("ENV", "PROD")
if ENV == "DEV":
    import settings.local_settings as local_settings
    settings = local_settings
else:
    import settings.prod_settings as prod_settings
    settings = prod_settings
