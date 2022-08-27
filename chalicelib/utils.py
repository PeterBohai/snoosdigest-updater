import time
from datetime import datetime, timezone
from typing import Optional

from praw.models import Submission as PrawSubmission
from sqlalchemy import select
from sqlalchemy.orm import Session

from chalicelib.models import PgSession, Subreddit, SubredditPost


def get_subreddits_to_update() -> list[Subreddit]:
    statement = select(Subreddit)

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
        update_source='lambda-snoosdigest-updater',
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
        curr_post.upvotes = subreddit_post.score
        curr_post.upvote_ratio = subreddit_post.upvote_ratio
        curr_post.num_comments = subreddit_post.num_comments
        curr_post.img_url = get_img_url(subreddit_post)
        curr_post.video_url = get_video_url(subreddit_post)
        curr_post.over_18 = subreddit_post.over_18
        curr_post.spoiler = subreddit_post.spoiler
        curr_post.data_updated_timestamp_utc = datetime.now(tz=timezone.utc)
        curr_post.update_source = 'lambda-snoosdigest-updater'
        if curr_post.reddit_id != post_id:
            print("*New* Post update found current reddit_id != post_id")
            curr_post.reddit_id = post_id
            curr_post.reddit_url = subreddit_post.shortlink
            curr_post.title = subreddit_post.title
            curr_post.author_name = subreddit_post.author.name
            curr_post.created_timestamp_utc = datetime.fromtimestamp(subreddit_post.created_utc)
            curr_post.created_unix_timestamp = subreddit_post.created_utc

    print(f'    --> {time.time() - start_time:.4f}s - Time taken to update_subreddit_post')


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


def get_subreddit_post_body(
    subreddit_post: PrawSubmission, post_id: str, post_permalink: str, post_selftext: Optional[str]
) -> str:
    body: str = post_selftext or ''

    # Check if body is just a http link
    permalink: str = generate_full_reddit_link(post_permalink)
    if not body:
        if subreddit_post.id_from_url(permalink) != post_id:
            # Link is another reddit post
            body = permalink
        elif hasattr(subreddit_post, 'url_overridden_by_dest'):
            # Link is a non-reddit article
            body = subreddit_post.url_overridden_by_dest

    # Check if body is a cross-post (nests another reddit post directly in the post body)
    if not body and hasattr(subreddit_post, 'crosspost_parent_list'):
        crosspost_id: str = subreddit_post.crosspost_parent_list[0].get('id', '')
        body = generate_reddit_link_from_id(crosspost_id)

    return normalize_text_content(body)
