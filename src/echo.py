import click


def is_now_ranking(post_id, LIMIT):
    click.echo(
        'Post with id {} is now ranking on the top {}'.format(post_id, LIMIT))


def is_still_ranking(post_id, LIMIT):
    click.echo(
        'Post with id {} is still ranking on the top {}'.format(post_id, LIMIT))


def is_not_ranking(post_id, LIMIT):
    click.echo(
        'Post with id {} is not ranking anymore on the top {}'.format(post_id, LIMIT))


def votes_have_increased(post_id, delta):
    click.echo(
        'Post with id {} increased votes by {} votes'.format(post_id, delta))


def votes_have_decreased(post_id, delta):
    click.echo(
        'Post with id {} decreased votes by {} votes'.format(post_id, delta))


def echo_ranking(post_id, delta_ranking, LIMIT):
    if delta_ranking == 0:
        is_still_ranking(post_id, LIMIT)
    elif delta_ranking < 0:
        is_not_ranking(post_id, LIMIT)
    else:
        is_now_ranking(post_id, LIMIT)


def echo_votes(post_id, delta_votes):
    if delta_votes < 0:
        votes_have_increased(post_id, delta_votes)
    elif delta_votes > 0:
        votes_have_decreased(post_id, delta_votes)
