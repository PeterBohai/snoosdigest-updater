# snoos-digest-posts-updater

[![Main](https://github.com/PeterBohai/snoosdigest-updater/actions/workflows/lint.yml/badge.svg)](https://github.com/PeterBohai/snoosdigest-updater/actions/workflows/lint.yml)
<a href="https://github.com/PeterBohai/snoosdigest/blob/main/requirements.txt">
<img alt="python" src="https://img.shields.io/badge/python-v3.9.6-blue"></a>
<a href="https://github.com/PeterBohai/snoosdigest/blob/main/frontend/package.json">
<img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white"></a>
<br/>
<a href="https://www.linkedin.com/in/peterbohai">
<img alt="LinedIn" src="https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin&logoColor=white"></a>

Snoos Digest is a web application that provides users with only the top posts from select subreddits on reddit.
Similar to how one scans the headlines of the day's or week's news, Snoos Digest will save you from scrolling through endless content.

This project is an AWS Lambda serverless function that runs frequently to update reddit posts in the SnoosDigest database.

### Built With

These are the main frameworks, libraries, and tools used in this project.

-   [AWS Lambda](https://aws.amazon.com/lambda/)
    -   [AWS Chalice](https://aws.github.io/chalice/)
-   [SQLAlchemy](https://www.sqlalchemy.org/)
-   [PostgreSQL](https://www.postgresql.org/)

## Contributing

If you experience any bugs or see anything that can be improved or added, please feel free to [open an issue](https://github.com/PeterBohai/snoosdigest-updater/issues) or create a [pull request](https://github.com/PeterBohai/snoosdigest-updater/pulls).
