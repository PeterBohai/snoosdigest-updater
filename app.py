import logging
import time
from typing import Iterable

from chalice import Chalice, Rate
from praw import Reddit as PrawReddit
from praw.models import Submission as PrawSubmission
from praw.models import Subreddit as PrawSubreddit

from chalicelib import settings, utils
from chalicelib.models import Subreddit

app = Chalice(app_name='snoosdigest-updater')

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
for logger_name in ("praw", "prawcore"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


@app.schedule(Rate(8, unit=Rate.MINUTES), name='reddit-posts')
def reddit_posts(event: dict) -> dict[str, list]:
    start_time = time.time()
    print(f'IS_PROD_SYSTEM: {settings.IS_PROD_SYSTEM}')
    app_settings = settings.SYS_SETTINGS
    num_posts = settings.MAX_NUM_POSTS_PER_SUBREDDIT

    praw_reddit: PrawReddit = PrawReddit(**app_settings['REDDIT_APP_SETTINGS'])

    subreddit_objs: list[Subreddit] = utils.get_subreddits_to_update()

    total_posts = 0
    for subreddit_obj in subreddit_objs:
        subreddit_id: int = subreddit_obj.subreddit_id
        subreddit_name: str = subreddit_obj.display_name
        start_posts = time.time()
        praw_subreddit: PrawSubreddit = praw_reddit.subreddit(subreddit_name)

        subreddit_top_posts: list[PrawSubmission] = list(praw_subreddit.top('day', limit=num_posts))
        if len(subreddit_top_posts) < num_posts:
            # Sometimes there are not enough posts under the top category
            subreddit_top_posts = list(praw_subreddit.hot(limit=num_posts))

        for post_order, post in enumerate(subreddit_top_posts, 1):
            total_posts += 1
            post_id = post.id

            curr_subreddit_post = utils.get_subreddit_post(
                subreddit_id, post_order, time_filter='day'
            )
            if not curr_subreddit_post:
                print(
                    f'INSERTing new subreddit post (subreddit: {subreddit_id} <{subreddit_name}>, '
                    f'order: {post_order}, post.id: {post_id}, filter: day)'
                )
                try:
                    utils.insert_subreddit_post(post, subreddit_id, post_order, time_filter='day')
                except Exception as err:
                    print(f'ERROR occurred while INSERTing: {err}')
                continue
            print(
                f'UPDATing existing subreddit post (subreddit: {subreddit_id} <{subreddit_name}>, '
                f'order: {post_order}, post.id: {post_id}, filter: day)'
            )
            try:
                utils.update_subreddit_post(post, subreddit_id, post_order, time_filter='day')
            except Exception as err:
                print(f'ERROR occurred while UPDATing: {err}')
        print(
            f'{time.time() - start_posts:.4f}s - Total time taken to get top/hot {num_posts} '
            f'<{subreddit_name}> posts'
        )
    print(f'>>> {time.time() - start_time:.4f}s - Total time, {total_posts} - Total posts')
    return {}


@app.lambda_function('subreddit-list')
def subreddit_list(event: dict, context: dict) -> dict:
    start_time = time.time()
    print(f'IS_PROD_SYSTEM: {settings.IS_PROD_SYSTEM}')
    app_settings = settings.SYS_SETTINGS
    num_subreddits = app_settings['NUM_SUBREDDITS']
    praw_reddit: PrawReddit = PrawReddit(**app_settings['REDDIT_APP_SETTINGS'])

    popular_subreddits: Iterable[PrawSubreddit] = praw_reddit.subreddits.popular(
        limit=num_subreddits
    )
    for i, praw_subreddit in enumerate(popular_subreddits, 1):
        print(f'#{i} Attempting to insert or update subreddit')
        utils.insert_or_update_subreddit(praw_subreddit)

    print(f'>>> {time.time() - start_time:.4f}s - Total time to update {num_subreddits} subreddits')
    return {}
