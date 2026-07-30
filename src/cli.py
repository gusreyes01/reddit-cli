from datetime import UTC, datetime
from pathlib import Path

import click
import requests

from data import Post, configure_database, db
from echo import echo_not_ranking, echo_ranking, echo_votes

LIMIT = 75
SOURCE_URL = f"https://www.reddit.com/r/popular.json?limit={LIMIT}"
USER_AGENT = "reddit-cli/1.0 (educational post ranking tracker)"


@click.group()
@click.option(
    "--database",
    envvar="REDDIT_CLI_DATABASE",
    default="reddit.db",
    show_default=True,
    type=click.Path(path_type=Path, dir_okay=False),
)
@click.pass_context
def cli(ctx, database):
    """Track ranking and vote changes in Reddit's public popular feed."""
    database.parent.mkdir(parents=True, exist_ok=True)
    configure_database(database)

    def close_database():
        if not db.is_closed():
            db.close()

    ctx.call_on_close(close_database)


@cli.command()
def initdb():
    """Create the local post database if it does not exist."""
    db.create_tables([Post], safe=True)
    click.echo("Initialized the database")


@cli.command()
@click.option("--source-url", default=SOURCE_URL, hidden=True)
def updatedb(source_url):
    """Fetch Reddit's popular feed and atomically update tracked posts."""
    db.create_tables([Post], safe=True)
    try:
        response = requests.get(
            source_url,
            headers={"User-Agent": USER_AGENT},
            timeout=(3.05, 15),
        )
        response.raise_for_status()
        posts = parse_posts(response.json())
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        raise click.ClickException(f"could not fetch Reddit feed: {exc}") from exc

    now = datetime.now(UTC)
    seen = set()
    events = []
    with db.atomic():
        for ranking, item in enumerate(posts):
            seen.add(item["id"])
            post = Post.get_or_none(Post.reddit_id == item["id"])
            if post is None:
                Post.create(
                    reddit_id=item["id"],
                    title=item["title"],
                    ups=item["ups"],
                    downs=item["downs"],
                    ranking=ranking,
                    created_date=now,
                    modified_date=now,
                )
                events.append(("added", item["id"], item["title"]))
                continue

            delta_votes = item["ups"] - post.ups
            delta_ranking = ranking - post.ranking
            post.title = item["title"]
            post.ups = item["ups"]
            post.downs = item["downs"]
            post.ranking = ranking
            post.delta_votes = delta_votes
            post.delta_ranking = delta_ranking
            post.modified_date = now
            post.save()
            events.append(("ranking", item["id"], delta_ranking))
            events.append(("votes", item["id"], delta_votes))

        dropped = Post.select().where((Post.ranking < LIMIT) & Post.reddit_id.not_in(seen))
        for post in dropped:
            post.delta_ranking = LIMIT - post.ranking
            post.ranking = LIMIT
            post.modified_date = now
            post.save()
            events.append(("dropped", post.reddit_id))

    for kind, *args in events:
        if kind == "added":
            click.echo(f"Post {args[0]} [{args[1]}] added")
        elif kind == "ranking":
            echo_ranking(args[0], args[1], LIMIT)
        elif kind == "votes":
            echo_votes(args[0], args[1])
        else:
            echo_not_ranking(args[0], LIMIT)
    click.echo(f"Updated {len(posts)} posts")


@cli.command()
@click.confirmation_option(prompt="Delete the local Reddit database?")
def dropdb():
    """Permanently remove all locally tracked posts."""
    db.drop_tables([Post], safe=True)
    click.echo("Dropped the database")


def parse_posts(payload):
    children = payload["data"]["children"]
    if not isinstance(children, list):
        raise ValueError("feed children must be a list")

    posts = []
    for child in children:
        item = child["data"]
        post_id = item["id"]
        title = item["title"]
        ups = item["ups"]
        downs = item.get("downs", 0)
        if (
            not isinstance(post_id, str)
            or not post_id
            or not isinstance(title, str)
            or not isinstance(ups, int)
            or ups < 0
            or not isinstance(downs, int)
            or downs < 0
        ):
            raise ValueError("feed contains an invalid post")
        posts.append({"id": post_id, "title": title, "ups": ups, "downs": downs})
    return posts


if __name__ == "__main__":
    cli()
