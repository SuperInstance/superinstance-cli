"""Tests for superinstance-cli."""

from click.testing import CliRunner

from superinstance_cli import cli


def test_check_in_range():
    runner = CliRunner()
    result = runner.invoke(cli, ["check", "5", "0", "10"])
    assert result.exit_code == 0
    assert "IN RANGE" in result.output
    assert "Margin" in result.output


def test_check_out_of_range():
    runner = CliRunner()
    result = runner.invoke(cli, ["check", "15", "0", "10"])
    assert result.exit_code == 0
    assert "OUT OF RANGE" in result.output


def test_edges_valid():
    runner = CliRunner()
    result = runner.invoke(cli, ["edges", "5"])
    assert result.exit_code == 0
    assert "7" in result.output  # 2*5 - 3 = 7


def test_edges_negative():
    runner = CliRunner()
    result = runner.invoke(cli, ["edges", "1"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_rigid_yes():
    runner = CliRunner()
    result = runner.invoke(cli, ["rigid", "5", "7"])
    assert result.exit_code == 0
    assert "RIGID" in result.output


def test_rigid_no():
    runner = CliRunner()
    result = runner.invoke(cli, ["rigid", "5", "5"])
    assert result.exit_code == 0
    assert "NOT RIGID" in result.output


def test_norm():
    runner = CliRunner()
    result = runner.invoke(cli, ["norm", "3", "5"])
    assert result.exit_code == 0
    # 3² - 3*5 + 5² = 9 - 15 + 25 = 19
    assert "19" in result.output


def test_encode():
    runner = CliRunner()
    result = runner.invoke(cli, ["encode", "1", "0"])
    assert result.exit_code == 0
    assert "sector" in result.output


def test_filter_passed():
    runner = CliRunner()
    result = runner.invoke(cli, ["filter", "10", "5", "2"])
    assert result.exit_code == 0
    assert "PASSED" in result.output


def test_filter_blocked():
    runner = CliRunner()
    result = runner.invoke(cli, ["filter", "5.5", "5", "1"])
    assert result.exit_code == 0
    assert "FILTERED" in result.output


def test_benchmark():
    runner = CliRunner()
    result = runner.invoke(cli, ["benchmark"])
    assert result.exit_code == 0
    assert "ops/s" in result.output


def test_status():
    runner = CliRunner()
    result = runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    assert "SuperInstance" in result.output
    assert "Python" in result.output
