import os

from dotenv import load_dotenv

load_dotenv()

IS_PROD_SYSTEM = os.environ['IS_PROD_SYSTEM'].lower() == 'true'
MAX_NUM_POSTS_PER_SUBREDDIT = int(os.environ['MAX_NUM_POSTS_PER_SUBREDDIT'])
UPDATE_SOURCE = 'lambda-snoosdigest-updater'

_dev_settings = {
    'REDDIT_APP_SETTINGS': {
        'client_id': os.environ['REDDIT_APP_CLIENT_ID'],
        'client_secret': os.environ['REDDIT_APP_SECRET'],
        'user_agent': os.environ['REDDIT_APP_USER_AGENT'],
    },
    'DATABASE_SETTINGS': {
        'db_name': os.environ['DB_NAME_DEV'],
        'db_user': os.environ['DB_USER_DEV'],
        'db_password': os.environ['DB_PASSWORD_DEV'],
        'db_host': os.environ['DB_HOST_DEV'],
    },
    'NUM_SUBREDDITS': 100,
}

_prod_settings = {
    'REDDIT_APP_SETTINGS': {
        'client_id': os.environ['REDDIT_APP_CLIENT_ID_PROD'],
        'client_secret': os.environ['REDDIT_APP_SECRET_PROD'],
        'user_agent': os.environ['REDDIT_APP_USER_AGENT_PROD'],
    },
    'DATABASE_SETTINGS': {
        'db_name': os.environ['DB_NAME_PROD'],
        'db_user': os.environ['DB_USER_PROD'],
        'db_password': os.environ['DB_PASSWORD_PROD'],
        'db_host': os.environ['DB_HOST_PROD'],
    },
    'NUM_SUBREDDITS': 5000,
}

SYS_SETTINGS: dict = _prod_settings if IS_PROD_SYSTEM else _dev_settings
