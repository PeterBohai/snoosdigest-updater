# snoosdigest-updater

[![Main](https://github.com/PeterBohai/snoosdigest-updater/actions/workflows/lint.yml/badge.svg)](https://github.com/PeterBohai/snoosdigest-updater/actions/workflows/lint.yml)
<a href="https://github.com/PeterBohai/snoosdigest/blob/main/requirements.txt">
<img alt="python" src="https://img.shields.io/badge/python-v3.9.6-blue"></a>
<a href="https://github.com/PeterBohai/snoosdigest/blob/main/frontend/package.json">
<img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white"></a>
<br/>
<a href="https://www.linkedin.com/in/peterbohai">
<img alt="LinedIn" src="https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin&logoColor=white"></a>

This project contains AWS Lambda serverless functions that runs on a schedule to update post data in the SnoosDigest database.

[SnoosDigest](https://www.snoosdigest.com/) is a web application that provides users with only the top posts from select subreddits on reddit.
Similar to how one scans the headlines of the day's or week's news, SnoosDigest will save you from scrolling through endless content.

The main repository for the web application can be found here: https://github.com/PeterBohai/snoosdigest

## Built With

These are the main frameworks, libraries, and tools used in this project.

-   [AWS Lambda](https://aws.amazon.com/lambda/)
    -   [AWS Chalice](https://aws.github.io/chalice/)
-   [SQLAlchemy](https://www.sqlalchemy.org/)
-   [PostgreSQL](https://www.postgresql.org/)



## Running Locally

### Clone the repo

```shell
git clone https://github.com/PeterBohai/snoosdigest-updater.git
```

### Create .env

Copy the contents from `.env.example` to a new `.env` file and update the values to hold the appropriate values and credentials.

You can run a PostgreSQL instance locally or from an online managed service. Some options include

-   [Amazon RDS](https://aws.amazon.com/rds/) (in AWS)
-   Render's [Managed PostgreSQL](https://render.com/docs/databases) service
-   An instance on [ElephantSQL](https://www.elephantsql.com/)

For Reddit API credentials, follow the instructions from the docs to create your own

-   [Reddit OAuth2 - Getting Started](https://github.com/reddit-archive/reddit/wiki/OAuth2#getting-started)
-   [Reddit API Rules](https://github.com/reddit-archive/reddit/wiki/API)

### Install packages

```shell
pip3 install -r dev-requirements.txt
```

### Set up pre-commit

[pre-commit](https://pre-commit.com/) allows us to easily configure and run git hooks for things such as static analysis and code formatting before each `git commit`.

The pre-commit package should already be installed in the previous step. To set up and install the git hooks scripts defined in `.pre-commit-config.yaml` run the following (only for the initial set up)

```shell
pre-commit install
```

For more information on pre-commit, please refer to the docs linked above.

### Deploy Lambda Functions to AWS

The following commands are just for reference. Please follow the official [Chalice documentation](https://aws.github.io/chalice/index.html)
for how to set up deployments to AWS.

For deploying the functions using DEV environments and settings
```shell
chalice deploy --stage dev
```

For deploying the functions using PROD environments and settings
```shell
chalice deploy --stage prod
```

## Contributing

If you experience any bugs or see anything that can be improved or added, please feel free to [open an issue](https://github.com/PeterBohai/snoosdigest-updater/issues) or create a [pull request](https://github.com/PeterBohai/snoosdigest-updater/pulls).
