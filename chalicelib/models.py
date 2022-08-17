from typing import Any

from sqlalchemy import Table, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from chalicelib.settings import SYS_SETTINGS

db_settings = SYS_SETTINGS['DATABASE_SETTINGS']
db_user = db_settings["db_user"]
db_password = db_settings["db_password"]
db_host = db_settings["db_host"]
db_name = db_settings["db_name"]

sql_engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}', future=True)
PgSession = sessionmaker(sql_engine)
Base: Any = declarative_base()


class Subreddit(Base):
    __table__ = Table('subreddit', Base.metadata, autoload_with=sql_engine)
