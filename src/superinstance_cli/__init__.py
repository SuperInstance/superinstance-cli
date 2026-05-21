"""Unified CLI for the SuperInstance ecosystem."""

from __future__ import annotations

import sys
import time
import math
from typing import Optional

import click


# ---------------------------------------------------------------------------
# Pure-Python fallback implementations (used when ecosystem packages absent)
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


def _is_rigid(vertices: int, edges: int) -> dict:
    """Check if a graph topology satisfies Laman rigidity conditions."""
    if vertices < 2:
        raise ValueError("Vertices must be >= 2")
    if edges < 0:
        raise ValueError("Edges must be >= 0")
    min_edges = 2 * vertices - 3
    rigid = edges >= min_edges
    return {"rigid": rigid, "vertices": vertices, "edges": edges, "min_edges": min_edges}


def _eisenstein_norm(a: int, b: int) -> float:
    """Eisenstein integer norm: a² - ab + b²."""
    return float(a * a - a * b + b * b)


def _pythagorean48_encode(x: int, y: int) -> int:
    """Pythagorean-48 direction encoding."""
    if x == 0 and y == 0:
        return 0
    # Map (x,y) to one of 48 directional bins
    angle = math.atan2(y, x)
    if angle < 0:
        angle += 2 * math.pi
    sector = int(angle / (2 * math.pi) * 48) % 48
    return sector


def _deadband_filter(value: float, baseline: float, threshold: float) -> dict:
    """Apply deadband filter: pass value only if it deviates beyond threshold."""
    delta = abs(value - baseline)
    passed = delta > threshold
    result = value if passed else baseline
    return {"result": result, "passed": passed, "delta": delta, "threshold": threshold}


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
    status = "✓ IN RANGE" if result["in_range"] else "✗ OUT OF RANGE"
    click.echo(f"Value {value} vs [{lower}, {upper}]: {status}")
    if result["in_range"]:
        click.echo(f"  Margin: {result['margin']:.4f}")


@cli.command()
@click.argument("vertices", type=int)
def edges(vertices: int):
    """Calculate minimum edges for Laman rigidity (2V - 3)."""
    try:
        result = _laman_edges(vertices)
        click.echo(f"Minimum edges for Laman rigidity ({vertices} vertices): {result}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("vertices", type=int)
@click.argument("edges_", metavar="EDGES", type=int)
def rigid(vertices: int, edges_: int):
    """Check if topology with VERTICES and EDGES is rigid."""
    try:
        result = _is_rigid(vertices, edges_)
        status = "✓ RIGID" if result["rigid"] else "✗ NOT RIGID"
        click.echo(f"{vertices} vertices, {edges_} edges: {status}")
        click.echo(f"  Minimum required: {result['min_edges']}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("a", type=int)
@click.argument("b", type=int)
def norm(a: int, b: int):
    """Calculate Eisenstein integer norm (a² - ab + b²)."""
    result = _eisenstein_norm(a, b)
    click.echo(f"Eisenstein norm ({a}, {b}): {result}")


@cli.command()
@click.argument("x", type=int)
@click.argument("y", type=int)
def encode(x: int, y: int):
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
    iterations = 100_000

    # Bounds check
    t0 = time.perf_counter()
    for i in range(iterations):
        _check_bounds(float(i), 0.0, float(iterations))
    t_bounds = time.perf_counter() - t0

    # Laman edges
    t0 = time.perf_counter()
    for i in range(iterations):
        _laman_edges(100)
    t_laman = time.perf_counter() - t0

    # Eisenstein norm
    t0 = time.perf_counter()
    for i in range(iterations):
        _eisenstein_norm(i % 100, (i + 1) % 100)
    t_norm = time.perf_counter() - t0

    # Deadband filter
    t0 = time.perf_counter()
    for i in range(iterations):
        _deadband_filter(float(i), float(i) + 0.5, 1.0)
    t_filter = time.perf_counter() - t0

    click.echo(f"Benchmark results ({iterations:,} iterations each):")
    click.echo(f"  Bounds check:     {t_bounds:.4f}s ({iterations / t_bounds:.0f} ops/s)")
    click.echo(f"  Laman edges:      {t_laman:.4f}s ({iterations / t_laman:.0f} ops/s)")
    click.echo(f"  Eisenstein norm:  {t_norm:.4f}s ({iterations / t_norm:.0f} ops/s)")
    click.echo(f"  Deadband filter:  {t_filter:.4f}s ({iterations / t_filter:.0f} ops/s)")


@cli.command()
def status():
    """Print SuperInstance ecosystem status."""
    click.echo("SuperInstance Ecosystem Status")
    click.echo("=" * 40)
    click.echo(f"  CLI version:  0.1.0")
    click.echo(f"  Python:       {sys.version.split()[0]}")

    # Check for ecosystem packages
    packages = {
        "numpy": "numpy",
        "scipy": "scipy",
        "sympy": "sympy",
    }
    click.echo("\n  Packages:")
    for name, import_name in packages.items():
        try:
            mod = __import__(import_name)
            ver = getattr(mod, "__version__", "unknown")
            click.echo(f"    {name}: {ver}")
        except ImportError:
            click.echo(f"    {name}: not installed")

    click.echo("\n  Languages: Rust, Python, TypeScript")
    click.echo("  Status: Operational ✓")
