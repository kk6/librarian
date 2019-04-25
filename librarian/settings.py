"""Application configuration.

See: https://bocadilloproject/github.io/guides/architecture/app.html#configuration
"""
from starlette.config import Config
from starlette.datastructures import URL

config = Config(".env")

# Define settings here.
# See: https://www.starlette.io/config/
DATABASE_URL = config("DATABASE_URL", cast=URL)
