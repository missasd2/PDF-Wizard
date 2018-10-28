import json

set  = json.loads(open("config.json", 'r').read())

from .settings import Settings

settings = Settings()