from peewee import *

db = SqliteDatabase('reddit.db')


class Post(Model):
    reddit_id = CharField()
    title = CharField()
    ups = IntegerField()
    downs = IntegerField()
    ranking = IntegerField()
    delta_votes = IntegerField()
    delta_ranking = IntegerField()
    created_date = DateField()
    modified_date = DateField()

    class Meta:
        database = db  # This model uses the "posts.db" database.
