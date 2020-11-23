* Description

This is a challenge as part of the Onaroll interview. This CLI communicates with the public Reddit API, stores information about posts, and on subsequent executions can tell which posts are new, which posts have dropped off, and which had vote changes.

[https://www.reddit.com/r/popular.json](https://www.reddit.com/r/popular.json)


* Quickstart

Create the initial database:

$: python src/cli.py initdb

Run the CLI:

$: python src/cli.py updatedb
