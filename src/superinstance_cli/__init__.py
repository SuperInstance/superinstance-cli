"""Unified CLI for the SuperInstance ecosystem."""

from __future__ import annotations

import sys
import time
import math
from typing import Optional

import click


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def _check_bounds(value: float, lower: float, upper: float) -> dict:
    """Eisenstein-math inspired bounds check."""
    in_range = lower <= value <= upper
    margin = min(value - lower, upper - value) if in_range else 0.0
    return {"in_range": in_range, "value": value, "lower": lower, "upper": upper, "margin": margin}


def _laman_edges(vertices: int) -> int:
    """Minimum edges for Laman rigidity: 2V - 3."""
    if vertices < 2:
        raise ValueError("Vertices must be >= 2")
    return 2 * vertices - 3


def _is_rigid(vertices: int, edges: int) -> bool:
    """Check if a graph topology satisfies Laman rigidity conditions."""
    if vertices < 2:
        raise ValueError("Vertices must be >= 2")
    if edges < 0:
        raise ValueError("Edges must be >= 0")
    return edges >= 2 * vertices - 3


def _eisenstein_norm(a: float, b: float) -> float:
    """Eisenstein integer norm: a² - ab + b²."""
    return a * a - a * b + b * b


def _pythagorean48_encode(x: float, y: float) -> int:
    """Pythagorean-48 direction encoding."""
    angle = math.atan2(y, x)
    sector = int(round(angle / (2 * math.pi) * 48)) % 48
    return sector


def _deadband_filter(value: float, baseline: float, threshold: float) -> dict:
    """Apply deadband filter: pass value only if it deviates beyond threshold."""
    delta = abs(value - baseline)
    passed = delta >= threshold
    return {"passed": passed, "value": value, "baseline": baseline, "delta": delta, "threshold": threshold, "result": value if passed else baseline}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group()
@click.version_option("0.1.0")
def cli():
    """Unified CLI for the SuperInstance ecosystem."""
    pass


@cli.command()
@click.argument("value", type=float)
@click.argument("lower", type=float)
@click.argument("upper", type=float)
def check(value: float, lower: float, upper: float):
    """Check if VALUE is within [LOWER, UPPER] bounds (Eisenstein math)."""
    result = _check_bounds(value, lower, upper)
    if result["in_range"]:
        click.echo(f"✓ IN RANGE: Value {value} vs [{lower}, {upper}]")
        click.echo(f"  Margin: {result['margin']:.4f}")
    else:
        click.echo(f"✗ OUT OF RANGE: Value {value} vs [{lower}, {upper}]")


@cli.command("edges")
@click.argument("vertices", type=int)
def edges_(vertices: int):
    """Calculate minimum edges for Laman rigidity (2V - 3)."""
    try:
        result = _laman_edges(vertices)
        click.echo(f"Minimum edges for Laman rigidity ({vertices} vertices): {result}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("vertices", type=int)
@click.argument("edges_", type=int)
def rigid(vertices: int, edges_: int):
    """Check if topology with VERTICES and EDGES is rigid."""
    try:
        result = _is_rigid(vertices, edges_)
        min_edges = _laman_edges(vertices)
        if result:
            click.echo(f"✓ RIGID: {vertices} vertices, {edges_} edges")
        else:
            click.echo(f"✗ NOT RIGID: {vertices} vertices, {edges_} edges")
            click.echo(f"  Minimum required: {min_edges}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("a", type=float)
@click.argument("b", type=float)
def norm(a: float, b: float):
    """Calculate Eisenstein integer norm (a² - ab + b²)."""
    result = _eisenstein_norm(a, b)
    click.echo(f"Eisenstein norm ({a}, {b}): {result}")


@cli.command()
@click.argument("x", type=float)
@click.argument("y", type=float)
def encode(x: float, y: float):
    """Encode direction (X, Y) as Pythagorean-48 sector."""
    result = _pythagorean48_encode(x, y)
    click.echo(f"Pythagorean-48 encoding ({x}, {y}): sector {result}")


@cli.command("filter")
@click.argument("value", type=float)
@click.argument("baseline", type=float)
@click.argument("threshold", type=float)
def filter_(value: float, baseline: float, threshold: float):
    """Apply deadband filter to VALUE against BASELINE with THRESHOLD."""
    result = _deadband_filter(value, baseline, threshold)
    status = "PASSED" if result["passed"] else "FILTERED"
    click.echo(f"{status}: {value} (baseline={baseline}, δ={result['delta']:.4f}, threshold={threshold})")
    click.echo(f"  Output: {result['result']}")


@cli.command()
def benchmark():
    """Run quick benchmarks of core operations."""
    iterations = 100000
    t0 = time.time()
    for _ in range(iterations):
        _check_bounds(0.5, 0.0, 1.0)
    t_bounds = time.time() - t0

    t0 = time.time()
    for _ in range(iterations):
        _laman_edges(100)
    t_laman = time.time() - t0

    t0 = time.time()
    for _ in range(iterations):
        _eisenstein_norm(0.5, 1.0)
    t_norm = time.time() - t0

    t0 = time.time()
    for _ in range(iterations):
        _deadband_filter(0.5, 1.0, 0.1)
    t_filter = time.time() - t0

    click.echo(f"Benchmark results ({iterations:,} iterations each):")
    click.echo(f"  Bounds check:     {t_bounds:.4f}s ({iterations / t_bounds:.0f} ops/s)")
    click.echo(f"  Laman edges:      {t_laman:.4f}s ({iterations / t_laman:.0f} ops/s)")
    click.echo(f"  Eisenstein norm:  {t_norm:.4f}s ({iterations / t_norm:.0f} ops/s)")
    click.echo(f"  Deadband filter:  {t_filter:.4f}s ({iterations / t_filter:.0f} ops/s)")


@cli.command()
def status():
    """Print SuperInstance ecosystem status."""
    click.echo("SuperInstance Ecosystem Status")
    click.echo("========================================")
    click.echo(f"  CLI version:  0.1.0")
    click.echo(f"  Python:       {sys.version.split()[0]}")
    packages = {}
    for pkg in ["numpy", "scipy", "sympy"]:
        try:
            mod = __import__(pkg)
            packages[pkg] = getattr(mod, "__version__", "unknown")
        except ImportError:
            packages[pkg] = "not installed"
    click.echo("\n  Packages:")
    for pkg, ver in packages.items():
        click.echo(f"    {pkg}: {ver}")
    click.echo("\n  Languages: Rust, Python, TypeScript")
    click.echo("  Status: Operational ✓")
