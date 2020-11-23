# cli.py

import datetime
from datetime import date
import click
import requests
import peewee

from data import Post
from echo import echo_ranking, echo_votes

db = peewee.SqliteDatabase('reddit.db')
db.connect()

LIMIT = 75
SOURCE_URL = 'https://www.reddit.com/r/popular.json?limit={}'.format(LIMIT)


@click.group()
def cli():
    pass


@click.command()
def initdb():
    # Creates a new database
    db.create_tables([Post])
    click.echo('Initialized the database')


@click.command()
def updatedb():
    # Checks for updates
    api_posts = requests.get(SOURCE_URL, headers={
        'User-agent': 'Robot 0.1'}).json()
    for (ranking, api_post) in enumerate(api_posts['data']['children']):

        api_post_id = api_post['data']['id']
        api_post_title = api_post['data']['title']
        api_post_ups = api_post['data']['ups']
        api_post_downs = api_post['data']['downs']

        db_posts = Post.select().where(Post.reddit_id == api_post_id)

        if db_posts.exists():
            for db_post in db_posts:
                # Post exists, check if it's still ranking.
                # Reddit uses hotness, we'll just fetch their ranking based on the reddit API order
                # https://github.com/reddit-archive/reddit/blob/master/r2/r2/lib/db/_sorts.pyx#L44

                delta_votes = api_post_ups - db_post.ups
                delta_ranking = ranking - db_post.ranking

                db_post.delta_votes = delta_votes
                db_post.delta_ranking = delta_ranking
                db_post.ranking = ranking
                db_post.ups = api_post_ups
                db_post.downs = api_post_downs
                db_post.modified_date = datetime.datetime.now()

                db_post.save()

                echo_ranking(api_post_id, delta_ranking, LIMIT)
                echo_votes(api_post_id, delta_votes)

        else:
            # New Post, save it
            post = Post(reddit_id=api_post_id,
                        title=api_post_title,
                        ups=api_post_ups,
                        downs=api_post_downs,
                        ranking=ranking,
                        delta_votes=0,
                        delta_ranking=0,
                        created_date=datetime.datetime.now(),
                        modified_date=datetime.datetime.now())
            post.save()
            click.echo('Post with id {} added'.format(api_post_id))


@click.command()
def dropdb():
    # WARNING - This command fully deletes the database
    db.drop_tables([Post])
    click.echo('Dropped the database')


cli.add_command(initdb)
cli.add_command(updatedb)
cli.add_command(dropdb)

if __name__ == "__main__":
    cli()
