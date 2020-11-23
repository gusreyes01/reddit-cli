from click.testing import CliRunner
from cli import cli


def test_initdb():
    runner = CliRunner()
    result = runner.invoke(cli, ['initdb'])
    assert result.exit_code == 0
    assert 'Initialized' in result.output


def test_dropdb():
    runner = CliRunner()
    result = runner.invoke(cli, ['dropdb'])
    assert result.exit_code == 0
    assert 'Dropped' in result.output


def test_updatedb():
    runner = CliRunner()
    result = runner.invoke(cli, ['updatedb'])
    assert result.exit_code == 0
    assert 'added' in result.output
