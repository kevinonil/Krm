"""Visualize a simple Morris-Thorne wormhole spatial embedding.

This is a visualization of an assumed geometry, not a physical wormhole
simulation and not a model of time travel or closed timelike curves.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def build_embedding(r0: float = 2.0, r_max: float = 10.0, samples: int = 500):
    """Return radial coordinates and the two embedding branches.

    For b(r) = r0**2 / r and Phi(r) = 0, the embedding profile is
    z(r) = +/- r0 * arcosh(r / r0), for r >= r0.
    """
    if r0 <= 0:
        raise ValueError("r0 must be positive")
    if r_max <= r0:
        raise ValueError("r_max must be greater than r0")
    if samples < 10:
        raise ValueError("samples must be at least 10")

    r = np.linspace(r0, r_max, samples)
    z = r0 * np.arccosh(r / r0)
    return r, z


def save_plot(output_dir: Path, r0: float = 2.0) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    r, z = build_embedding(r0=r0)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(r, z, label="Upper embedding branch")
    ax.plot(r, -z, label="Lower embedding branch")
    ax.scatter([r0], [0], color="black", zorder=5, label="Throat")
    ax.set_title("Morris–Thorne Wormhole: Spatial Embedding")
    ax.set_xlabel("Radial coordinate r")
    ax.set_ylabel("Embedding coordinate z")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    output_path = output_dir / "wormhole_embedding.png"
    fig.savefig(output_path, dpi=160)
    plt.close(fig)

    # Export the profile values so the result can also be inspected as data.
    np.savetxt(
        output_dir / "embedding_profile.csv",
        np.column_stack((r, z, -z)),
        delimiter=",",
        header="r,z_upper,z_lower",
        comments="",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="output", help="Directory for generated files")
    parser.add_argument("--throat-radius", type=float, default=2.0)
    args = parser.parse_args()

    image_path = save_plot(Path(args.output_dir), r0=args.throat_radius)

    # Basic numerical sanity checks for b(r) = r0^2/r.
    r, _ = build_embedding(r0=args.throat_radius)
    shape_function_ratio = args.throat_radius**2 / r**2
    assert np.isclose(shape_function_ratio[0], 1.0)
    assert np.all(shape_function_ratio <= 1.0 + 1e-12)

    print(f"Simulation completed. Plot saved to: {image_path}")
    print(f"Minimum r: {r.min():.3f}; maximum r: {r.max():.3f}")
    print("Checked b(r)/r <= 1 on the sampled domain.")


if __name__ == "__main__":
    main()
