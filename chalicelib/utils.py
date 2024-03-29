import time
from datetime import date, datetime, timezone
from typing import Optional

from praw.models import Submission as PrawSubmission
from praw.models import Subreddit as PrawSubreddit
from sqlalchemy import select
from sqlalchemy.orm import Session

from chalicelib.models import PgSession, Subreddit, SubredditPost
from chalicelib.settings import UPDATE_SOURCE


def get_subreddits_to_update() -> list[Subreddit]:
    statement = select(Subreddit).where(Subreddit.last_viewed_timestamp.isnot(None))

    pg_session: Session
    with PgSession.begin() as pg_session:
        result = pg_session.execute(statement).scalars().all()
        pg_session.expunge_all()  # To make row objects available outside the scope of the session

    return result


def get_subreddit_post(subreddit_id: int, order: int, time_filter: str = 'day') -> SubredditPost:
    statement = select(SubredditPost).where(
        SubredditPost.subreddit_id == subreddit_id,
        SubredditPost.__table__.columns[f'top_{time_filter}_order'] == order,
    )

    pg_session: Session
    with PgSession.begin() as pg_session:
        result = pg_session.execute(statement).scalars().first()
        pg_session.expunge_all()

    return result


def insert_subreddit_post(
    subreddit_post: PrawSubmission, subreddit_id: int, order: int, time_filter: str = 'day'
) -> None:
    start_time = time.time()
    post_id = subreddit_post.id
    post_permalink = subreddit_post.permalink
    post_selftext = subreddit_post.selftext
    new_post = SubredditPost(
        reddit_id=post_id,
        reddit_url=subreddit_post.shortlink,
        title=subreddit_post.title,
        body=get_subreddit_post_body(subreddit_post, post_id, post_permalink, post_selftext),
        body_url=get_subreddit_post_body_url(
            subreddit_post, post_id, post_permalink, post_selftext
        ),
        author_name=subreddit_post.author.name,
        upvotes=subreddit_post.score,
        upvote_ratio=subreddit_post.upvote_ratio,
        num_comments=subreddit_post.num_comments,
        img_url=get_img_url(subreddit_post),
        video_url=get_video_url(subreddit_post),
        over_18=subreddit_post.over_18,
        spoiler=subreddit_post.spoiler,
        created_timestamp_utc=datetime.fromtimestamp(subreddit_post.created_utc),
        created_unix_timestamp=subreddit_post.created_utc,
        data_updated_timestamp_utc=datetime.now(tz=timezone.utc),
        update_source=UPDATE_SOURCE,
        subreddit_id=subreddit_id,
        **{f'top_{time_filter}_order': order},
    )

    pg_session: Session
    with PgSession.begin() as pg_session:
        pg_session.add(new_post)
    print(f'    --> {time.time() - start_time:.4f}s - Time taken to insert_subreddit_post')


def update_subreddit_post(
    subreddit_post: PrawSubmission, subreddit_id: int, order: int, time_filter: str = 'day'
) -> None:
    start_time = time.time()

    statement = select(SubredditPost).where(
        SubredditPost.subreddit_id == subreddit_id,
        SubredditPost.__table__.columns[f'top_{time_filter}_order'] == order,
    )
    post_id = subreddit_post.id
    post_permalink = subreddit_post.permalink
    post_selftext = subreddit_post.selftext

    pg_session: Session
    with PgSession.begin() as pg_session:
        curr_post = pg_session.execute(statement).scalars().first()
        curr_post.body = get_subreddit_post_body(
            subreddit_post, post_id, post_permalink, post_selftext
        )
        curr_post.body_url = get_subreddit_post_body_url(
            subreddit_post, post_id, post_permalink, post_selftext
        )
        curr_post.upvotes = subreddit_post.score
        curr_post.upvote_ratio = subreddit_post.upvote_ratio
        curr_post.num_comments = subreddit_post.num_comments
        curr_post.img_url = get_img_url(subreddit_post)
        curr_post.video_url = get_video_url(subreddit_post)
        curr_post.over_18 = subreddit_post.over_18
        curr_post.spoiler = subreddit_post.spoiler
        curr_post.data_updated_timestamp_utc = datetime.now(tz=timezone.utc)
        curr_post.update_source = UPDATE_SOURCE
        if curr_post.reddit_id != post_id:
            print("*New* Post update found current reddit_id != post_id")
            curr_post.reddit_id = post_id
            curr_post.reddit_url = subreddit_post.shortlink
            curr_post.title = subreddit_post.title
            curr_post.author_name = subreddit_post.author.name
            curr_post.created_timestamp_utc = datetime.fromtimestamp(subreddit_post.created_utc)
            curr_post.created_unix_timestamp = subreddit_post.created_utc

    print(f'    --> {time.time() - start_time:.4f}s - Time taken to update_subreddit_post')


def update_subreddit(praw_subreddit: PrawSubreddit) -> None:
    start_time = time.time()

    statement = select(Subreddit).where(Subreddit.reddit_id == praw_subreddit.id)
    pg_session: Session
    with PgSession.begin() as pg_session:
        curr_subreddit = pg_session.execute(statement).scalars().first()
        curr_subreddit.subscribers = praw_subreddit.subscribers
        curr_subreddit.data_updated_timestamp_utc = datetime.now(tz=timezone.utc)
        curr_subreddit.update_source = UPDATE_SOURCE
    print(f'    --> {time.time() - start_time:.4f}s - Time taken to update_subreddit')


def insert_or_update_subreddit(praw_subreddit: PrawSubreddit) -> None:
    start_time = time.time()
    subreddit_name = praw_subreddit.display_name
    subreddit_reddit_id = praw_subreddit.id
    statement = select(Subreddit).where(Subreddit.reddit_id == subreddit_reddit_id)
    pg_session: Session
    with PgSession.begin() as pg_session:
        curr_subreddit = pg_session.execute(statement).scalars().first()
        curr_datetime = datetime.now(tz=timezone.utc)

        if curr_subreddit:
            print(f'** UPDATE subreddit, <{subreddit_name}> already exists...')
            curr_subreddit.subscribers = praw_subreddit.subscribers
            curr_subreddit.data_updated_timestamp_utc = curr_datetime
            curr_subreddit.update_source = UPDATE_SOURCE
        else:
            print(f'** INSERT new subreddit, <{subreddit_name}> is not in the database...')
            created_unix_timestamp = int(praw_subreddit.created_utc)
            new_subreddit = Subreddit(
                reddit_id=subreddit_reddit_id,
                display_name=subreddit_name,
                display_name_prefixed=praw_subreddit.display_name_prefixed,
                reddit_url_path=praw_subreddit.url,
                subscribers=praw_subreddit.subscribers,
                created_date_utc=date.fromtimestamp(created_unix_timestamp),
                created_unix_timestamp=created_unix_timestamp,
                data_updated_timestamp_utc=curr_datetime,
                inserted_at=curr_datetime,
                update_source=UPDATE_SOURCE,
            )
            pg_session.add(new_subreddit)

    print(f'    --> {time.time() - start_time:.4f}s - Time taken to update_or_insert_subreddit')


def generate_full_reddit_link(link_path: str) -> str:
    return f'https://www.reddit.com{link_path}'.strip()


def generate_reddit_link_from_id(reddit_id: str) -> str:
    return f'https://redd.it/{reddit_id}'.strip()


def normalize_text_content(text: str) -> str:
    text = text.replace('&#x200B;', '')
    return text.strip()


def get_img_url(subreddit_post: PrawSubmission) -> str:
    url = subreddit_post.url
    if 'i.redd.it' in url:
        return url
    return ''


def get_video_url(subreddit_post: PrawSubmission) -> str:
    if 'v.redd.it' in subreddit_post.url and subreddit_post.media.get('reddit_video'):
        return subreddit_post.media['reddit_video'].get('fallback_url', '')
    return ''


def _extract_body_text_or_url(
    body_text: str, subreddit_post: PrawSubmission, post_id: str, post_permalink: str
) -> str:
    if body_text:
        return normalize_text_content(body_text)
    # Check if body is just a http link
    permalink: str = generate_full_reddit_link(post_permalink)
    if subreddit_post.id_from_url(permalink) != post_id:
        # Link is another reddit post
        return normalize_text_content(permalink)
    if hasattr(subreddit_post, "url_overridden_by_dest"):
        # Link is a non-reddit article
        return normalize_text_content(subreddit_post.url_overridden_by_dest)
    if hasattr(subreddit_post, "crosspost_parent_list"):
        # Check if body is a cross-post (links to another reddit post in the post body)
        crosspost_id: str = subreddit_post.crosspost_parent_list[0].get("id", "")
        crosspost_link = generate_reddit_link_from_id(crosspost_id)
        return normalize_text_content(crosspost_link)
    return ""


def get_subreddit_post_body(
    subreddit_post: PrawSubmission, post_id: str, post_permalink: str, post_selftext: Optional[str]
) -> str:
    return _extract_body_text_or_url(post_selftext or '', subreddit_post, post_id, post_permalink)


def get_subreddit_post_body_url(
    subreddit_post: PrawSubmission, post_id: str, post_permalink: str, post_selftext: Optional[str]
) -> str:
    body: str = post_selftext or ""
    if body:
        return ""
    return _extract_body_text_or_url(body, subreddit_post, post_id, post_permalink)
