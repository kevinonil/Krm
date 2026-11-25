# Wormhole Geometry Demo

An educational Python visualization of the spatial embedding for a simple
Morris–Thorne wormhole metric.

## Model

- Redshift function: `Phi(r) = 0`
- Shape function: `b(r) = r0^2 / r`
- Default throat radius: `r0 = 2`
- Embedding profile: `z(r) = +/- r0 * arcosh(r/r0)`, for `r >= r0`

The two embedding sheets are rendered as interactive 3D surfaces. An
illustrative radial path and a moving marker show a route approaching,
crossing, and leaving the throat in the diagram.

## Run locally

```bash
python -m pip install -r requirements.txt
python wormhole_sim.py
```

Open `output/wormhole_3d.html` in a modern browser. It is self-contained
(includes Plotly JavaScript), so the interactive view works offline after
generation. Drag to rotate, scroll to zoom, and use Play/Pause to animate the
illustrative marker.

You can change the throat radius and plot range:

```bash
python wormhole_sim.py --throat-radius 3 --r-max 14 --samples 220
```

The program also writes:
- `output/wormhole_embedding.png` — static profile
- `output/embedding_profile.csv` — numerical profile data

## GitHub Actions

Every push runs the simulation on a GitHub-hosted runner and uploads all
generated files as the `wormhole-results` artifact. Open the repository's
**Actions** tab, select the latest run, and download the artifact.

## Scientific scope and limitations

This is a visualization of an assumed spatial geometry, not a solution of
the full Einstein field equations. The moving marker is an illustrative
animation, not a numerically integrated photon geodesic. The project does
not establish that traversable wormholes exist, model the exotic matter or
energy conditions that might be required to support one, or demonstrate
time travel or closed timelike curves. A successful workflow only confirms
that this visualization code runs and produces its files.
