import click


def echo_ranking(post_id, delta_ranking, limit):
    if delta_ranking == 0:
        click.echo(f"Post {post_id} is still in the top {limit}")
    elif delta_ranking < 0:
        click.echo(f"Post {post_id} climbed {-delta_ranking} places")
    else:
        click.echo(f"Post {post_id} dropped {delta_ranking} places")


def echo_not_ranking(post_id, limit):
    click.echo(f"Post {post_id} is no longer in the top {limit}")


def echo_votes(post_id, delta_votes):
    if delta_votes > 0:
        click.echo(f"Post {post_id} gained {delta_votes} votes")
    elif delta_votes < 0:
        click.echo(f"Post {post_id} lost {-delta_votes} votes")
