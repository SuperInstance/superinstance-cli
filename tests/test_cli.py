"""Tests for superinstance_cli."""
import sys
import os
import pytest
from click.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from superinstance_cli import (
    _check_bounds,
    _laman_edges,
    _is_rigid,
    _eisenstein_norm,
    _pythagorean48_encode,
    _deadband_filter,
    cli,
)


# ---------------------------------------------------------------------------
# Core function tests
# ---------------------------------------------------------------------------

class TestCheckBounds:
    def test_in_range(self):
        r = _check_bounds(0.5, 0.0, 1.0)
        assert r["in_range"] is True
        assert r["margin"] > 0

    def test_out_of_range_low(self):
        r = _check_bounds(-1.0, 0.0, 1.0)
        assert r["in_range"] is False

    def test_out_of_range_high(self):
        r = _check_bounds(2.0, 0.0, 1.0)
        assert r["in_range"] is False

    def test_boundary(self):
        assert _check_bounds(0.0, 0.0, 1.0)["in_range"]
        assert _check_bounds(1.0, 0.0, 1.0)["in_range"]


class TestLamanEdges:
    def test_basic(self):
        assert _laman_edges(2) == 1
        assert _laman_edges(4) == 5
        assert _laman_edges(12) == 21

    def test_too_few_vertices(self):
        with pytest.raises(ValueError):
            _laman_edges(1)


class TestIsRigid:
    def test_rigid(self):
        assert _is_rigid(4, 5) is True

    def test_not_rigid(self):
        assert _is_rigid(4, 4) is False

    def test_exact(self):
        assert _is_rigid(2, 1) is True

    def test_too_few_vertices(self):
        with pytest.raises(ValueError):
            _is_rigid(1, 0)

    def test_negative_edges(self):
        with pytest.raises(ValueError):
            _is_rigid(3, -1)


class TestEisensteinNorm:
    def test_basic(self):
        assert _eisenstein_norm(1, 0) == 1.0
        assert _eisenstein_norm(1, 1) == 1.0
        assert _eisenstein_norm(2, 1) == 3.0

    def test_zero(self):
        assert _eisenstein_norm(0, 0) == 0.0

    def test_symmetric(self):
        assert _eisenstein_norm(3, 5) == _eisenstein_norm(5, 3)


class TestPythagorean48:
    def test_east(self):
        assert _pythagorean48_encode(1, 0) == 0

    def test_zero_vector(self):
        result = _pythagorean48_encode(0, 0)
        assert 0 <= result < 48


class TestDeadbandFilter:
    def test_passed(self):
        r = _deadband_filter(1.5, 1.0, 0.1)
        assert r["passed"] is True
        assert r["result"] == 1.5

    def test_filtered(self):
        r = _deadband_filter(1.05, 1.0, 0.1)
        assert r["passed"] is False
        assert r["result"] == 1.0

    def test_exact_threshold(self):
        r = _deadband_filter(1.1, 1.0, 0.1)
        assert r["passed"] is True


# ---------------------------------------------------------------------------
# CLI command tests
# ---------------------------------------------------------------------------

class TestCLI:
    runner = CliRunner()

    def test_check_in_range(self):
        result = self.runner.invoke(cli, ["check", "0.5", "0.0", "1.0"])
        assert result.exit_code == 0
        assert "IN RANGE" in result.output

    def test_check_out_of_range(self):
        result = self.runner.invoke(cli, ["check", "2.0", "0.0", "1.0"])
        assert result.exit_code == 0
        assert "OUT OF RANGE" in result.output

    def test_edges(self):
        result = self.runner.invoke(cli, ["edges", "12"])
        assert result.exit_code == 0
        assert "21" in result.output

    def test_edges_invalid(self):
        result = self.runner.invoke(cli, ["edges", "1"])
        assert result.exit_code == 1

    def test_rigid_yes(self):
        result = self.runner.invoke(cli, ["rigid", "4", "5"])
        assert result.exit_code == 0
        assert "RIGID" in result.output

    def test_rigid_no(self):
        result = self.runner.invoke(cli, ["rigid", "4", "3"])
        assert result.exit_code == 0
        assert "NOT RIGID" in result.output

    def test_norm(self):
        result = self.runner.invoke(cli, ["norm", "3", "5"])
        assert result.exit_code == 0
        assert "19" in result.output  # 9 - 15 + 25 = 19

    def test_encode(self):
        result = self.runner.invoke(cli, ["encode", "1", "0"])
        assert result.exit_code == 0
        assert "sector" in result.output

    def test_filter_passed(self):
        result = self.runner.invoke(cli, ["filter", "1.5", "1.0", "0.1"])
        assert result.exit_code == 0
        assert "PASSED" in result.output

    def test_filter_filtered(self):
        result = self.runner.invoke(cli, ["filter", "1.05", "1.0", "0.1"])
        assert result.exit_code == 0
        assert "FILTERED" in result.output

    def test_benchmark(self):
        result = self.runner.invoke(cli, ["benchmark"])
        assert result.exit_code == 0
        assert "ops/s" in result.output

    def test_status(self):
        result = self.runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "Operational" in result.output

    def test_version(self):
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
