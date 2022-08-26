import time
from typing import Iterable

from chalice import Chalice, Cron
from praw import Reddit as PrawReddit
from praw.models import Submission as PrawSubmission
from praw.models import Subreddit as PrawSubreddit

from chalicelib import settings, utils
from chalicelib.models import Subreddit

app = Chalice(app_name='snoosdigest-updater')


@app.schedule(Cron('0/9', '12-3', '?', '*', '*', '*'), name='reddit-posts')
def reddit_posts(event: dict) -> dict[str, list]:
    start_time = time.time()
    print(f'IS_PROD_SYSTEM: {settings.IS_PROD_SYSTEM}')
    app_settings = settings.SYS_SETTINGS
    num_posts = settings.MAX_NUM_POSTS_PER_SUBREDDIT

    praw_reddit: PrawReddit = PrawReddit(**app_settings['REDDIT_APP_SETTINGS'])

    subreddit_objs: list[Subreddit] = utils.get_subreddits_to_update()

    posts: dict = {}
    for subreddit_obj in subreddit_objs:
        subreddit_id: int = subreddit_obj.subreddit_id
        subreddit_name: str = subreddit_obj.display_name

        start_posts = time.time()
        praw_subreddit: PrawSubreddit = praw_reddit.subreddit(subreddit_name)
        subreddit_top_posts: list[PrawSubmission] = list(praw_subreddit.top('day', limit=num_posts))
        print(
            f'{time.time() - start_posts:.4f}s - Time taken to get top {num_posts} '
            f'<{subreddit_name}> posts'
        )
        if len(subreddit_top_posts) < num_posts:
            subreddit_top_posts = praw_subreddit.hot(limit=num_posts)

        recorded_ids = []
        for order_i, post in enumerate(subreddit_top_posts, 1):
            posts[post.id] = {
                'subreddit_id': subreddit_id,
                'subreddit_name': subreddit_name,
                'order': order_i,
            }
            recorded_ids.append(post.id)
        if len(recorded_ids) < num_posts:
            hot_posts: Iterable[PrawSubmission] = praw_subreddit.hot(limit=num_posts)
            for recorded_id in recorded_ids:
                del posts[recorded_id]
            for order_i, post in enumerate(hot_posts, 1):
                posts[post.id] = {
                    'subreddit_id': subreddit_id,
                    'subreddit_name': subreddit_name,
                    'order': order_i,
                }
    post_fullnames = [f't3_{post_id}' for post_id in posts]
    start_full_name = time.time()
    all_posts_info: Iterable[PrawSubmission] = praw_reddit.info(post_fullnames)
    print(f'{time.time() - start_full_name:.4f}s - Time taken to get all_posts_info')

    total_posts = 0
    for post in all_posts_info:
        total_posts += 1
        post_data = posts[post.id]
        post_order = post_data['order']
        subreddit_id = post_data['subreddit_id']
        subreddit_name = post_data['subreddit_name']

        curr_subreddit_post = utils.get_subreddit_post(subreddit_id, post_order, time_filter='day')

        if not curr_subreddit_post:
            print(
                f'Attempting to INSERT new subreddit post '
                f'(subreddit: {subreddit_id} <{subreddit_name}>, '
                f'order: {post_order}, post.id: {post.id}, filter: day)'
            )
            try:
                utils.insert_subreddit_post(post, subreddit_id, post_order, time_filter='day')
            except Exception as err:
                print(f'ERROR occurred while INSERTing: {err}')
            continue

        print(
            f'Attempting to UPDATE existing subreddit post '
            f'(subreddit: {subreddit_id} <{subreddit_name}>, '
            f'order: {post_order}, post.id: {post.id}, filter: day)'
        )
        try:
            utils.update_subreddit_post(post, curr_subreddit_post, time_filter='day')
        except Exception as err:
            print(f'ERROR occurred while UPDATing: {err}')

    print(f'>>>>>>>> {time.time() - start_time:.4f}s - Total time, {total_posts} - Total posts')
    return {}
