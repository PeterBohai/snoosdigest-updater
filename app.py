from typing import Any, Iterable

from chalice import Chalice
from praw import Reddit as PrawReddit
from praw.models import Submission as PrawSubmission
from praw.models import Subreddit as PrawSubreddit

from chalicelib import settings, utils
from chalicelib.models import Subreddit

app = Chalice(app_name='snoosdigest-updater')


# @app.lambda_function(name='reddit-posts')
def reddit_posts(event: dict, context: Any) -> dict[str, list]:
    print(f'IS_PROD_SYSTEM: {settings.IS_PROD_SYSTEM}')
    app_settings = settings.SYS_SETTINGS

    praw_reddit: PrawReddit = PrawReddit(**app_settings['REDDIT_APP_SETTINGS'])

    subreddit_objs: list[Subreddit] = utils.get_subreddits_to_update()
    res: dict = {}
    for subreddit_obj in subreddit_objs:
        if subreddit_obj.subreddit_id != 9:
            continue
        praw_subreddit: PrawSubreddit = praw_reddit.subreddit(subreddit_obj.display_name)
        subreddit_top_posts: Iterable[PrawSubmission] = praw_subreddit.top(
            'day', limit=settings.MAX_NUM_POSTS_PER_SUBREDDIT
        )

        for i, post in enumerate(subreddit_top_posts, 1):
            current_subreddit_post = utils.get_subreddit_post(
                subreddit_obj.subreddit_id, i, time_filter='day'
            )

            if not current_subreddit_post:
                utils.insert_subreddit_post(post, subreddit_obj.subreddit_id, i, time_filter='day')
                continue

            # Update existing subreddit
            print(f'UPDATE {current_subreddit_post}')

    return res
