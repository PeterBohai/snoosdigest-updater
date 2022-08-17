from praw.models import Subreddit as PrawSubreddit
from sqlalchemy import select
from sqlalchemy.orm import Session

from chalicelib.models import PgSession, Subreddit


def update_or_insert_subreddit_posts(praw_subreddit: PrawSubreddit, time_filter: str) -> list[dict]:
    pass


def get_subreddits_to_update() -> list[str]:
    statement = select(Subreddit.display_name)

    pg_session: Session
    with PgSession.begin() as pg_session:
        result = pg_session.execute(statement).scalars().all()

    print(result)

    return result
