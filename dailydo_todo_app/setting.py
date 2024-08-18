from starlette.config import Config
from starlette.datastructures import Secret

# ? Step-3: Create setting.py file for encrypting DatabaseURL

try:
    config = Config(".env")

except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)
