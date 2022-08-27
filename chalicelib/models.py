from typing import Any

from sqlalchemy import (
    BIGINT,
    BOOLEAN,
    SMALLINT,
    TEXT,
    TIMESTAMP,
    VARCHAR,
    Column,
    Float,
    Integer,
    Table,
    create_engine,
)
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


class SubredditPost(Base):
    __tablename__ = 'subreddit_post'

    subreddit_post_id = Column(Integer, primary_key=True)
    reddit_id = Column(VARCHAR(16))
    reddit_url = Column(VARCHAR(256))
    title = Column(VARCHAR(300))
    body = Column(TEXT)
    author_name = Column(VARCHAR(64))
    upvotes = Column(Integer)
    upvote_ratio = Column(Float)
    num_comments = Column(Integer)
    img_url = Column(VARCHAR(256))
    video_url = Column(VARCHAR(256))
    over_18 = Column(BOOLEAN)
    spoiler = Column(BOOLEAN)
    created_timestamp_utc = Column(TIMESTAMP(timezone=True))
    created_unix_timestamp = Column(BIGINT)
    data_updated_timestamp_utc = Column(TIMESTAMP(timezone=True))
    subreddit_id = Column(Integer)
    top_day_order = Column(SMALLINT)
    top_week_order = Column(SMALLINT)
    top_month_order = Column(SMALLINT)
    top_year_order = Column(SMALLINT)
    top_all_order = Column(SMALLINT)
    update_source = Column(VARCHAR(32))
