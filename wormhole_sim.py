"""Interactive 3D visualization of a simple Morris-Thorne wormhole.

This visualizes an assumed spatial geometry. It is not a physical wormhole
solver and does not demonstrate that time travel is possible.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go


def validate_parameters(r0: float, r_max: float, samples: int) -> None:
    if not np.isfinite(r0) or r0 <= 0:
        raise ValueError("throat radius must be a finite positive number")
    if not np.isfinite(r_max) or r_max <= r0:
        raise ValueError("r_max must be finite and greater than throat radius")
    if samples < 20 or samples > 1200:
        raise ValueError("samples must be between 20 and 1200")


def build_embedding(r0: float = 2.0, r_max: float = 10.0, samples: int = 180):
    """Return r and z for z(r)=+/-r0*arcosh(r/r0)."""
    validate_parameters(r0, r_max, samples)
    r = np.linspace(r0, r_max, samples)
    z = r0 * np.arccosh(r / r0)
    return r, z


def save_static_outputs(output_dir: Path, r0: float, r_max: float, samples: int) -> None:
    r, z = build_embedding(r0, r_max, samples)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(r, z, label="Upper embedding branch")
    ax.plot(r, -z, label="Lower embedding branch")
    ax.scatter([r0], [0], color="black", zorder=5, label="Throat")
    ax.set(title="Morris–Thorne Wormhole: Spatial Embedding",
           xlabel="Radial coordinate r", ylabel="Embedding coordinate z")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "wormhole_embedding.png", dpi=160)
    plt.close(fig)

    np.savetxt(
        output_dir / "embedding_profile.csv",
        np.column_stack((r, z, -z)),
        delimiter=",",
        header="r,z_upper,z_lower",
        comments="",
    )


def build_3d_figure(r0: float, r_max: float, samples: int) -> go.Figure:
    r, z = build_embedding(r0, r_max, samples)
    theta = np.linspace(0, 2 * np.pi, 100)
    rr, tt = np.meshgrid(r, theta)
    zz = r0 * np.arccosh(rr / r0)
    xx = rr * np.cos(tt)
    yy = rr * np.sin(tt)

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=xx, y=yy, z=zz, name="Upper universe",
        colorscale="Viridis", opacity=0.88, showscale=False,
        hovertemplate="r=%{x:.2f}, z=%{z:.2f}<extra>Upper sheet</extra>",
    ))
    fig.add_trace(go.Surface(
        x=xx, y=yy, z=-zz, name="Lower universe",
        colorscale="Plasma", opacity=0.88, showscale=False,
        hovertemplate="r=%{x:.2f}, z=%{z:.2f}<extra>Lower sheet</extra>",
    ))

    # Illustrative radial light path: approach the throat on one sheet,
    # pass through the throat, and move outward on the other sheet.
    path_x = np.concatenate((r[::-1], r[1:]))
    path_y = np.zeros_like(path_x)
    path_z = np.concatenate((z[::-1], -z[1:]))
    fig.add_trace(go.Scatter3d(
        x=path_x, y=path_y, z=path_z, mode="lines",
        line=dict(color="#ffcc33", width=7), name="Illustrative light path",
    ))
    fig.add_trace(go.Scatter3d(
        x=[path_x[0]], y=[0], z=[path_z[0]], mode="markers",
        marker=dict(size=7, color="#ff5533"),
        name="Light marker",
    ))

    frames = [
        go.Frame(
            name=str(i),
            data=[go.Scatter3d(
                x=[path_x[i]], y=[path_y[i]], z=[path_z[i]],
                mode="markers", marker=dict(size=7, color="#ff5533"),
            )],
            traces=[3],
        )
        for i in range(len(path_x))
    ]
    fig.frames = frames
    fig.update_layout(
        title=f"Interactive Morris–Thorne Wormhole (throat radius r₀={r0:g})",
        scene=dict(
            xaxis_title="x", yaxis_title="y", zaxis_title="z",
            aspectmode="data",
            camera=dict(eye=dict(x=1.7, y=1.7, z=1.15)),
        ),
        margin=dict(l=0, r=0, b=0, t=55),
        legend=dict(orientation="h", yanchor="bottom", y=0.01),
        updatemenus=[dict(
            type="buttons", showactive=False, x=0.02, y=0.98,
            buttons=[
                dict(label="▶ Play", method="animate",
                     args=[None, {"frame": {"duration": 25, "redraw": True},
                                  "fromcurrent": True,
                                  "transition": {"duration": 0}}]),
                dict(label="⏸ Pause", method="animate",
                     args=[[None], {"mode": "immediate",
                                    "frame": {"duration": 0, "redraw": False},
                                    "transition": {"duration": 0}}]),
            ],
        )],
    )
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--throat-radius", type=float, default=2.0)
    parser.add_argument("--r-max", type=float, default=10.0)
    parser.add_argument("--samples", type=int, default=180)
    args = parser.parse_args()

    validate_parameters(args.throat_radius, args.r_max, args.samples)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    save_static_outputs(output_dir, args.throat_radius, args.r_max, args.samples)
    figure = build_3d_figure(args.throat_radius, args.r_max, args.samples)
    html_path = output_dir / "wormhole_3d.html"
    figure.write_html(html_path, include_plotlyjs=True, full_html=True)

    r, _ = build_embedding(args.throat_radius, args.r_max, args.samples)
    ratio = args.throat_radius**2 / r**2
    assert np.isclose(ratio[0], 1.0)
    assert np.all(ratio <= 1.0 + 1e-12)
    assert html_path.stat().st_size > 10_000

    print("3D wormhole visualization generated successfully.")
    print(f"Throat radius: {args.throat_radius:g}")
    print(f"Radial range: [{r.min():.3f}, {r.max():.3f}]")
    print("Checked b(r)/r <= 1 on the sampled domain.")
    print(f"Interactive 3D view: {html_path}")
    print("Static plot: wormhole_embedding.png")
    print("Data table: embedding_profile.csv")


if __name__ == "__main__":
    main()
