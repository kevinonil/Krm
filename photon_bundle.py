"""Trace a bundle of null geodesics through the same idealized wormhole."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

from wormhole_sim import integrate_photon, validate


def run_bundle(throat_radius: float, r_max: float, impacts: list[float], samples: int):
    validate(throat_radius, r_max, samples, 0.0)
    if not impacts:
        raise ValueError("at least one impact parameter is required")
    trajectories = []
    for impact in impacts:
        validate(throat_radius, r_max, samples, impact)
        result = integrate_photon(throat_radius, r_max, impact, samples)
        tau, l, v, phi, x, y, z = result
        r = np.sqrt(l*l + throat_radius*throat_radius)
        residual = v*v + impact*impact/(r*r) - 1.0
        if not (l[0] < 0 < l[-1]) or not np.all(np.isfinite(residual)):
            raise RuntimeError(f"invalid trajectory for impact parameter {impact}")
        trajectories.append({
            "impact": impact, "tau": tau, "l": l, "v": v, "phi": phi,
            "x": x, "y": y, "z": z,
            "max_null_residual": float(np.max(np.abs(residual))),
        })
    return trajectories


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--throat-radius", type=float, default=2.0)
    parser.add_argument("--r-max", type=float, default=10.0)
    parser.add_argument("--samples", type=int, default=160)
    parser.add_argument("--impacts", default="0,0.5,1,1.5",
                        help="comma-separated impact parameters, each smaller than throat radius")
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    try:
        impacts = [float(item.strip()) for item in args.impacts.split(",") if item.strip()]
        trajectories = run_bundle(args.throat_radius, args.r_max, impacts, args.samples)
    except ValueError as exc:
        parser.error(str(exc))

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    fig = go.Figure()
    rows = []
    for item in trajectories:
        label = f"impact={item['impact']:g}"
        fig.add_trace(go.Scatter3d(x=item["x"], y=item["y"], z=item["z"],
                                   mode="lines", name=label))
        rows.extend((item["impact"], *values) for values in zip(
            item["tau"], item["l"], item["phi"], item["x"], item["y"], item["z"],
            item["v"]))
    fig.update_layout(
        title="Null-geodesic bundle in an idealized ultrastatic wormhole",
        scene=dict(xaxis_title="x", yaxis_title="y", zaxis_title="embedding z",
                   aspectmode="data"),
        margin=dict(l=0, r=0, b=0, t=55))
    fig.write_html(out / "photon_bundle_3d.html", include_plotlyjs=True, full_html=True)

    with (out / "photon_bundle.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["impact_parameter", "affine_parameter", "l", "phi", "x", "y", "z", "dl_dlambda"])
        writer.writerows(rows)

    fig2, ax = plt.subplots(figsize=(9, 6))
    for item in trajectories:
        ax.plot(item["x"], item["z"], label=f"impact={item['impact']:g}")
    ax.scatter([0], [0], label="throat", zorder=4)
    ax.set(xlabel="x", ylabel="Embedding z", title="Photon bundle: x-z projection")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig2.tight_layout()
    fig2.savefig(out / "photon_bundle.png", dpi=160)
    plt.close(fig2)

    report = [
        "NULL GEODESIC BUNDLE REPORT",
        "===========================",
        f"throat_radius={args.throat_radius:g}",
        f"r_max={args.r_max:g}",
        f"trajectory_count={len(trajectories)}",
        "impact_parameters=" + ",".join(f"{v:g}" for v in impacts),
        "all_trajectories_cross_throat=True",
        f"max_null_constraint_residual={max(t['max_null_residual'] for t in trajectories):.6e}",
        "All paths are test rays on a prescribed metric; no backreaction is included.",
    ]
    (out / "photon_bundle_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("PASS: all photon trajectories crossed the throat")
    print(f"Maximum null-constraint residual: {max(t['max_null_residual'] for t in trajectories):.3e}")
    print("Generated photon_bundle_3d.html, photon_bundle.csv, photon_bundle.png, photon_bundle_report.txt")


if __name__ == "__main__":
    main()
