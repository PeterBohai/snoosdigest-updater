from datetime import datetime, timezone

from praw.models import Submission as PrawSubmission
from praw.models import Subreddit as PrawSubreddit
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from chalicelib.models import PgSession, Subreddit, SubredditPost


def update_or_insert_subreddit_posts(praw_subreddit: PrawSubreddit, time_filter: str) -> list[dict]:
    pass


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
    new_post = SubredditPost(
        reddit_id=subreddit_post.id,
        reddit_url=subreddit_post.shortlink,
        title=subreddit_post.title,
        body=get_subreddit_post_body(subreddit_post),
        author_name=subreddit_post.author.name if subreddit_post.author else '',
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
        subreddit_id=subreddit_id,
        **{f'top_{time_filter}_order': order},
    )

    pg_session: Session
    with PgSession.begin() as pg_session:
        pg_session.add(new_post)


def update_subreddit_post(
    subreddit_post: PrawSubmission, curr_post: SubredditPost, time_filter: str = 'day'
) -> None:
    order_col = f'top_{time_filter}_order'
    update_statement = (
        update(SubredditPost)
        .where(
            SubredditPost.subreddit_id == curr_post.subreddit_id,
            getattr(SubredditPost, order_col) == getattr(curr_post, order_col),
        )
        .values(
            reddit_id=subreddit_post.id,
            reddit_url=subreddit_post.shortlink,
            title=subreddit_post.title,
            body=get_subreddit_post_body(subreddit_post),
            author_name=subreddit_post.author.name if subreddit_post.author else '',
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
        )
    )
    pg_session: Session
    with PgSession.begin() as pg_session:
        pg_session.execute(update_statement)


def generate_full_reddit_link(link_path: str) -> str:
    return f'https://www.reddit.com{link_path}'.strip()


def generate_reddit_link_from_id(reddit_id: str) -> str:
    return f'https://redd.it/{reddit_id}'.strip()


def normalize_text_content(text: str) -> str:
    text = text.replace('&#x200B;', '')
    return text.strip()


def get_img_url(subreddit_post: PrawSubmission) -> str:
    if 'i.redd.it' in subreddit_post.url:
        return subreddit_post.url
    return ''


def get_video_url(subreddit_post: PrawSubmission) -> str:
    if 'v.redd.it' in subreddit_post.url and subreddit_post.media.get('reddit_video'):
        return subreddit_post.media['reddit_video'].get('fallback_url', '')
    return ''


def get_reddit_permalink(subreddit_post: PrawSubmission) -> str:
    return generate_full_reddit_link(subreddit_post.permalink)


def get_subreddit_post_body(subreddit_post: PrawSubmission) -> str:
    body: str = subreddit_post.selftext or ''

    # Check if body is just a http link
    permalink: str = get_reddit_permalink(subreddit_post)
    if not body:
        if subreddit_post.id_from_url(permalink) != subreddit_post.id:
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
