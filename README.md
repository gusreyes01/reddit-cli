# Reddit-cli

## Description

_This is a challenge as part of the Onaroll interview. This CLI communicates with the public Reddit API, stores information about posts, and on subsequent executions can tell which posts are new, which posts have dropped off, and which had vote changes._

[https://www.reddit.com/r/popular.json](https://www.reddit.com/r/popular.json)


## Quickstart

_Install CLI requirements:_

``` $: pip install -r requirements.txt ```


_Create the initial database:_

``` $: python src/cli.py initdb ```

_Run the CLI:_

``` $: python src/cli.py updatedb ```


## Docker

``` $: docker build -t redis-cli . ```

``` $: docker run redis-cli python cli.py initdb ```

``` $: docker run redis-cli python cli.py updatedb ```