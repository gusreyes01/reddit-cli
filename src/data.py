from peewee import (
    CharField,
    DateTimeField,
    IntegerField,
    Model,
    SqliteDatabase,
)

db = SqliteDatabase(None)


def configure_database(path):
    if not db.is_closed():
        db.close()
    db.init(path, pragmas={"foreign_keys": 1, "journal_mode": "wal"})
    db.connect(reuse_if_open=True)


class Post(Model):
    reddit_id = CharField(unique=True, index=True)
    title = CharField()
    ups = IntegerField()
    downs = IntegerField()
    ranking = IntegerField()
    delta_votes = IntegerField(default=0)
    delta_ranking = IntegerField(default=0)
    created_date = DateTimeField()
    modified_date = DateTimeField()

    class Meta:
        database = db
