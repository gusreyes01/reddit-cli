# Contributing

Install `requirements-dev.txt`, add tests for behavior changes, and run:

```bash
ruff check .
pytest
pip check
docker build --tag reddit-cli:test .
```

Keep network access mocked in tests and never commit generated SQLite files.
