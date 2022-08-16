from typing import Any, Iterable

from chalice import Chalice
from praw import Reddit as PrawReddit
from praw.models import Submission as PrawSubmission
from praw.models import Subreddit as PrawSubreddit

from chalicelib import settings

app = Chalice(app_name='snoosdigest-updater')


@app.lambda_function(name='reddit-posts')
def reddit_posts(event: dict, context: Any) -> list[dict]:
    print(f'IS_PROD_SYSTEM: {settings.IS_PROD_SYSTEM}')
    app_settings = settings.PROD_SETTINGS if settings.IS_PROD_SYSTEM else settings.DEV_SETTINGS

    praw_reddit: PrawReddit = PrawReddit(**app_settings['REDDIT_APP_SETTINGS'])

    praw_subreddit: PrawSubreddit = praw_reddit.subreddit('news')
    subreddit_top_posts: Iterable[PrawSubmission] = praw_subreddit.top(
        'day', limit=settings.MAX_NUM_POSTS_PER_SUBREDDIT
    )
    res = []
    for post in subreddit_top_posts:
        res.append(
            {
                'reddit_id': post.id,
                'author_name': post.author.name,
                'upvotes': post.score,
                'num_comments': post.num_comments,
            }
        )

    return res
