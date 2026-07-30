from unittest.mock import Mock

import pytest
import requests
from click.testing import CliRunner

import cli as cli_module
from cli import LIMIT, cli, parse_posts
from data import Post, configure_database, db


def feed(*posts):
    return {"data": {"children": [{"data": post} for post in posts]}}


def post(post_id="abc", title="Example", ups=10, downs=1):
    return {"id": post_id, "title": title, "ups": ups, "downs": downs}


def response(payload):
    result = Mock()
    result.json.return_value = payload
    result.raise_for_status.return_value = None
    return result


def invoke(runner, database, *args, **kwargs):
    return runner.invoke(cli, ["--database", str(database), *args], **kwargs)


def test_init_and_drop_database(tmp_path):
    runner = CliRunner()
    database = tmp_path / "reddit.db"

    initialized = invoke(runner, database, "initdb")
    dropped = invoke(runner, database, "dropdb", input="y\n")

    assert initialized.exit_code == 0
    assert "Initialized" in initialized.output
    assert dropped.exit_code == 0
    assert "Dropped" in dropped.output


def test_update_creates_posts_and_uses_network_guards(tmp_path, monkeypatch):
    get = Mock(return_value=response(feed(post())))
    monkeypatch.setattr(cli_module.requests, "get", get)

    result = invoke(CliRunner(), tmp_path / "reddit.db", "updatedb")

    assert result.exit_code == 0
    assert "Post abc [Example] added" in result.output
    assert "Updated 1 posts" in result.output
    get.assert_called_once()
    assert get.call_args.kwargs["timeout"] == (3.05, 15)
    assert "reddit-cli" in get.call_args.kwargs["headers"]["User-Agent"]


def test_update_reports_vote_and_ranking_changes(tmp_path, monkeypatch):
    database = tmp_path / "reddit.db"
    payloads = [
        feed(post("other"), post("abc", ups=10)),
        feed(post("abc", ups=14), post("other")),
    ]
    monkeypatch.setattr(
        cli_module.requests,
        "get",
        Mock(side_effect=[response(payloads[0]), response(payloads[1])]),
    )
    runner = CliRunner()

    assert invoke(runner, database, "updatedb").exit_code == 0
    updated = invoke(runner, database, "updatedb")

    assert updated.exit_code == 0
    assert "Post abc climbed 1 places" in updated.output
    assert "Post abc gained 4 votes" in updated.output


def test_update_marks_posts_that_drop_out(tmp_path, monkeypatch):
    database = tmp_path / "reddit.db"
    monkeypatch.setattr(
        cli_module.requests,
        "get",
        Mock(side_effect=[response(feed(post("abc"))), response(feed(post("other")))]),
    )
    runner = CliRunner()
    invoke(runner, database, "updatedb")

    result = invoke(runner, database, "updatedb")

    assert result.exit_code == 0
    assert f"Post abc is no longer in the top {LIMIT}" in result.output
    configure_database(database)
    try:
        assert Post.get(Post.reddit_id == "abc").ranking == LIMIT
    finally:
        db.close()


def test_update_turns_network_errors_into_cli_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(
        cli_module.requests,
        "get",
        Mock(side_effect=requests.Timeout("slow upstream")),
    )

    result = invoke(CliRunner(), tmp_path / "reddit.db", "updatedb")

    assert result.exit_code != 0
    assert "could not fetch Reddit feed" in result.output


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"data": {"children": "wrong"}},
        feed({"id": "", "title": "Bad", "ups": 1}),
        feed({"id": "x", "title": 3, "ups": 1}),
        feed({"id": "x", "title": "Bad", "ups": "many"}),
        feed({"id": "x", "title": "Bad", "ups": -1}),
        feed({"id": "x", "title": "Bad", "ups": 1, "downs": -1}),
    ],
)
def test_parse_posts_rejects_malformed_feeds(payload):
    with pytest.raises((KeyError, ValueError)):
        parse_posts(payload)


def test_parse_posts_allows_missing_downvotes():
    assert parse_posts(feed({"id": "x", "title": "Valid", "ups": 3})) == [
        {"id": "x", "title": "Valid", "ups": 3, "downs": 0}
    ]
