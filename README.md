# Reddit CLI

A small, local command-line tracker for Reddit's public `/r/popular` feed.
It records post rankings and votes in SQLite, then reports new posts, ranking
changes, vote changes, and posts that leave the top 75.

No Reddit account or API credential is required. The tool stores only public
post metadata.

## Requirements and setup

- Python 3.12+

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install --requirement requirements.txt
```

## Usage

```bash
python src/cli.py initdb
python src/cli.py updatedb
python src/cli.py dropdb
```

The database defaults to `reddit.db`. Select a different location with
`--database PATH` or the `REDDIT_CLI_DATABASE` environment variable.
Updates use explicit connection/read timeouts and one database transaction,
so a failed fetch cannot leave a partial snapshot.

## Docker

The image runs as a non-root user and expects persistent data under `/data`.

```bash
docker build --tag reddit-cli .
docker run --rm -v reddit-data:/data reddit-cli initdb
docker run --rm -v reddit-data:/data reddit-cli updatedb
```

## Quality checks

```bash
python -m pip install --requirement requirements-dev.txt
ruff check .
pytest
pip check
```

GitHub Actions also builds the container on every push and pull request.
Dependabot monitors Python, Docker, and workflow dependencies. See
[CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).
