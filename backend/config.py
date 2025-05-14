import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    PG_LINK = os.getenv('PG_LINK')
    PG_LINK_ALEMBIC = os.getenv('PG_LINK_ALEMBIC')

