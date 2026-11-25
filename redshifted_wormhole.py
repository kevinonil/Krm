"""Non-ultrastatic Morris-Thorne stress-energy and redshift-profile scan.

Metric: ds^2=-exp(2 Phi(r))dt^2 + dr^2/(1-b(r)/r)+r^2 dOmega^2.
G=c=1. This computes Einstein-tensor-implied stresses for a prescribed
static geometry; it does not supply matter dynamics or prove stability.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def validate(r0: float, q: float, alpha: float, rmax: float, samples: int) -> None:
    vals = (r0, q, alpha, rmax)
    if not all(np.isfinite(x) for x in vals):
        raise ValueError("all parameters must be finite")
    if r0 <= 0:
        raise ValueError("throat radius must be positive")
    if q <= -1:
        raise ValueError("shape exponent q must be greater than -1 for asymptotic flatness")
    if abs(alpha) > 5:
        raise ValueError("redshift amplitude alpha must be within [-5, 5]")
    if rmax <= r0:
        raise ValueError("r-max must exceed throat radius")
    if not 20 <= samples <= 5000:
        raise ValueError("samples must be between 20 and 5000")


def stress_energy(r, r0: float, q: float, alpha: float) -> dict[str, np.ndarray]:
    """Orthonormal rho, p_r, p_t for b=r0*(r0/r)^q and Phi=-alpha*r0/r."""
    radius = np.asarray(r, dtype=float)
    if np.any(~np.isfinite(radius)) or np.any(radius < r0) or r0 <= 0 or q <= -1:
        raise ValueError("r must be finite and >= r0; r0>0 and q>-1")
    if not np.isfinite(alpha) or abs(alpha) > 5:
        raise ValueError("alpha must be finite and within [-5, 5]")
    b = r0 * (r0 / radius) ** q
    bp = -q * b / radius
    phi = -alpha * r0 / radius
    phi_p = alpha * r0 / radius**2
    phi_pp = -2.0 * alpha * r0 / radius**3
    one_minus_b_over_r = 1.0 - b / radius

    rho = bp / (8.0 * np.pi * radius**2)
    p_r = (-b / radius**3 + 2.0 * one_minus_b_over_r * phi_p / radius) / (8.0 * np.pi)

    # Algebraically regular at the throat; avoids separate 0/0 factors.
    p_t = (
        one_minus_b_over_r * (phi_pp + phi_p**2 + phi_p / radius)
        - (radius * bp - b) * phi_p / (2.0 * radius**2)
        + (b - radius * bp) / (2.0 * radius**3)
    ) / (8.0 * np.pi)

    return {
        "b_over_r": b / radius,
        "lapse": np.exp(phi),
        "phi": phi,
        "rho": rho,
        "p_r": p_r,
        "p_t": p_t,
        "rho_plus_p_r": rho + p_r,
        "rho_plus_p_t": rho + p_t,
        "rho_plus_p_r_plus_2p_t": rho + p_r + 2.0 * p_t,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--throat-radius", type=float, default=2.0)
    parser.add_argument("--shape-exponent", type=float, default=1.0)
    parser.add_argument("--alpha", type=float, default=0.5,
                        help="redshift amplitude in Phi(r)=-alpha*r0/r")
    parser.add_argument("--r-max", type=float, default=10.0)
    parser.add_argument("--samples", type=int, default=240)
    parser.add_argument("--scan", default="-2,-1,0,0.5,1,2",
                        help="comma-separated alpha values")
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    try:
        validate(args.throat_radius, args.shape_exponent, args.alpha, args.r_max, args.samples)
        alphas = [float(x.strip()) for x in args.scan.split(",") if x.strip()]
        if not alphas:
            raise ValueError("scan must contain at least one alpha")
        for value in alphas:
            validate(args.throat_radius, args.shape_exponent, value, args.r_max, args.samples)
    except ValueError as exc:
        parser.error(str(exc))

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    radius = np.linspace(args.throat_radius, args.r_max, args.samples)
    data = stress_energy(radius, args.throat_radius, args.shape_exponent, args.alpha)

    with (out / "redshifted_energy_conditions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["r", *data.keys()])
        writer.writerows(zip(radius, *(data[k] for k in data)))

    fig, ax = plt.subplots(figsize=(9, 6))
    for alpha in alphas:
        d = stress_energy(radius, args.throat_radius, args.shape_exponent, alpha)
        ax.plot(radius, d["rho_plus_p_r"], label=f"radial NEC, alpha={alpha:g}")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set(xlabel="Areal radius r", ylabel="rho + p_r (G=c=1)",
           title="Radial NEC under redshift-profile variation")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "redshift_nec_scan.png", dpi=160)
    plt.close(fig)

    radial = data["rho_plus_p_r"]
    throat_nec_exact = -(args.shape_exponent + 1.0) / (
        8.0 * np.pi * args.throat_radius**2
    )
    report = (
        "NON-ULTRASTATIC MORRIS-THORNE REDSHIFT / ENERGY AUDIT\n"
        "=====================================================\n"
        f"throat_radius={args.throat_radius:g}\nshape_exponent_q={args.shape_exponent:g}\n"
        f"shape_function=b(r)=r0*(r0/r)^q\n"
        f"redshift_function=Phi(r)=-alpha*r0/r\nalpha={args.alpha:g}\n"
        f"r_max={args.r_max:g}\nsamples={args.samples}\nunits=geometrized (G=c=1)\n"
        f"minimum_lapse={float(np.min(data['lapse'])):.12e}\n"
        f"radial_NEC_at_throat_numeric={float(radial[0]):.12e}\n"
        f"radial_NEC_at_throat_exact={throat_nec_exact:.12e}\n"
        f"radial_NEC_violated_at_throat={bool(radial[0] < 0)}\n"
        f"radial_NEC_max_on_grid={float(np.max(radial)):.12e}\n"
        f"all_profiles_finite={bool(np.all(np.isfinite(np.column_stack(list(data.values())))))}\n"
        "Key result: at the throat, rho+p_r=(b'(r0)-1)/(8*pi*r0^2), "
        "independent of finite Phi'(r0). The flare-out condition b'(r0)<1 "
        "therefore forces radial NEC violation at the throat in this classical "
        "Einstein-gravity, static, traversable Morris-Thorne setup.\n"
        "Changing this finite redshift profile can alter stresses away from the "
        "throat, but does not remove the throat result.\n"
        "This is not a matter model, quantum calculation, or dynamical stability proof.\n"
    )
    (out / "redshifted_energy_report.txt").write_text(report, encoding="utf-8")
    if not np.all(np.isfinite(np.column_stack(list(data.values())))):
        raise RuntimeError("non-finite output")
    if not np.isclose(radial[0], throat_nec_exact, rtol=1e-9, atol=1e-12):
        raise RuntimeError("throat NEC identity check failed")
    print("PASS: non-ultrastatic stress-energy profile is finite")
    print(f"PASS: throat NEC identity = {radial[0]:.6e}")
    print("Generated redshifted_energy_conditions.csv, redshift_nec_scan.png, redshifted_energy_report.txt")


if __name__ == "__main__":
    main()
