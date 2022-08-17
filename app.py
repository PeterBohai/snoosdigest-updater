from typing import Any, Iterable

from chalice import Chalice
from praw import Reddit as PrawReddit
from praw.models import Submission as PrawSubmission
from praw.models import Subreddit as PrawSubreddit

from chalicelib import settings, utils

app = Chalice(app_name='snoosdigest-updater')


@app.lambda_function(name='reddit-posts')
def reddit_posts(event: dict, context: Any) -> dict[str, list]:
    print(f'IS_PROD_SYSTEM: {settings.IS_PROD_SYSTEM}')
    app_settings = settings.SYS_SETTINGS

    praw_reddit: PrawReddit = PrawReddit(**app_settings['REDDIT_APP_SETTINGS'])

    subreddit_names = utils.get_subreddits_to_update()
    res = {}
    for subreddit_name in subreddit_names:
        praw_subreddit: PrawSubreddit = praw_reddit.subreddit(subreddit_name)
        subreddit_top_posts: Iterable[PrawSubmission] = praw_subreddit.top(
            'day', limit=settings.MAX_NUM_POSTS_PER_SUBREDDIT
        )
        post_results = []
        for post in subreddit_top_posts:
            post_results.append(
                {
                    'reddit_id': post.id,
                    'author_name': post.author.name if post.author else '',  # User is "deleted"
                    'upvotes': post.score,
                    'num_comments': post.num_comments,
                }
            )
        res[subreddit_name] = post_results

    return res
