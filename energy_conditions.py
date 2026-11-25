"""Stress-energy diagnostics inferred from an ultrastatic Morris-Thorne metric.

Metric: ds^2 = -dt^2 + dr^2/(1-b(r)/r) + r^2 dOmega^2.
Units: G=c=1.  The stress tensor is inferred from Einstein's equation;
no material source or dynamical stability model is supplied.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def validate(throat_radius: float, exponent: float, r_max: float, samples: int) -> None:
    if not np.isfinite(throat_radius) or throat_radius <= 0:
        raise ValueError("throat radius must be finite and positive")
    if not np.isfinite(exponent) or exponent <= -1:
        raise ValueError("shape exponent must be finite and greater than -1")
    if not np.isfinite(r_max) or r_max <= throat_radius:
        raise ValueError("r-max must exceed throat radius")
    if not 20 <= samples <= 5000:
        raise ValueError("samples must be between 20 and 5000")


def stress_energy(r: np.ndarray | float, throat_radius: float, exponent: float) -> dict[str, np.ndarray]:
    """Return orthonormal-frame rho, p_r, p_t and energy-condition sums.

    Shape function b(r)=r0*(r0/r)^exponent, with Phi=0.
    """
    validate(throat_radius, exponent, max(float(np.max(np.asarray(r))), throat_radius + 1e-9), 20)
    radius = np.asarray(r, dtype=float)
    if np.any(~np.isfinite(radius)) or np.any(radius < throat_radius):
        raise ValueError("r must be finite and at least the throat radius")
    b = throat_radius * (throat_radius / radius) ** exponent
    bp = -exponent * b / radius
    rho = bp / (8.0 * np.pi * radius**2)
    radial_pressure = -b / (8.0 * np.pi * radius**3)
    tangential_pressure = (b - radius * bp) / (16.0 * np.pi * radius**3)
    return {
        "b_over_r": b / radius,
        "rho": rho,
        "p_r": radial_pressure,
        "p_t": tangential_pressure,
        "rho_plus_p_r": rho + radial_pressure,
        "rho_plus_p_t": rho + tangential_pressure,
        "rho_plus_p_r_plus_2p_t": rho + radial_pressure + 2.0 * tangential_pressure,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--throat-radius", type=float, default=2.0)
    parser.add_argument("--shape-exponent", type=float, default=1.0,
                        help="q in b(r)=r0*(r0/r)^q; q>-1")
    parser.add_argument("--r-max", type=float, default=10.0)
    parser.add_argument("--samples", type=int, default=240)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    try:
        validate(args.throat_radius, args.shape_exponent, args.r_max, args.samples)
    except ValueError as exc:
        parser.error(str(exc))

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    radius = np.linspace(args.throat_radius, args.r_max, args.samples)
    data = stress_energy(radius, args.throat_radius, args.shape_exponent)
    columns = ["r", *data.keys()]
    with (out / "energy_conditions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(zip(radius, *(data[key] for key in data)))

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(radius, data["rho_plus_p_r"], label="rho + p_r (radial NEC)")
    ax.plot(radius, data["rho_plus_p_t"], label="rho + p_t (transverse NEC)")
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set(xlabel="Areal radius r", ylabel="Energy-condition combination (geometrized units)",
           title=f"Energy-condition diagnostics (q={args.shape_exponent:g}, r0={args.throat_radius:g})")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "energy_conditions.png", dpi=160)
    plt.close(fig)

    radial_nec = data["rho_plus_p_r"]
    transverse_nec = data["rho_plus_p_t"]
    report = (
        "ULTRASTATIC MORRIS-THORNE STRESS-ENERGY DIAGNOSTIC\n"
        "==================================================\n"
        f"throat_radius={args.throat_radius:g}\nshape_exponent_q={args.shape_exponent:g}\n"
        f"shape_function=b(r)=r0*(r0/r)^q\nr_max={args.r_max:g}\nsamples={args.samples}\n"
        "redshift_function=Phi(r)=0\nunits=geometrized (G=c=1)\n"
        f"radial_NEC_violated_at_all_sampled_r={bool(np.all(radial_nec < 0))}\n"
        f"radial_NEC_max={float(np.max(radial_nec)):.12e}\n"
        f"transverse_NEC_min={float(np.min(transverse_nec)):.12e}\n"
        f"rho_min={float(np.min(data['rho'])):.12e}\n"
        f"rho_max={float(np.max(data['rho'])):.12e}\n"
        "Interpretation: these components are inferred from the Einstein tensor "
        "for the prescribed static metric, not from a specified material model.\n"
        "A negative radial rho+p_r indicates violation of the radial null energy "
        "condition (NEC) in this classical GR model.\n"
        "This is not a quantum-field calculation, matter construction, or "
        "dynamical stability analysis.\n"
    )
    (out / "energy_conditions_report.txt").write_text(report, encoding="utf-8")
    if not np.all(np.isfinite(np.column_stack(list(data.values())))):
        raise RuntimeError("non-finite stress-energy output")
    print("PASS: finite stress-energy profiles generated")
    print(f"Radial NEC violated throughout sampled range: {bool(np.all(radial_nec < 0))}")
    print("Generated energy_conditions.csv, energy_conditions.png, energy_conditions_report.txt")


if __name__ == "__main__":
    main()
