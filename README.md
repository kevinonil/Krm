# Wormhole Geometry Demo

A small Python project that visualizes the spatial embedding diagram for a
simple Morris–Thorne wormhole metric.

## Model

This demo uses

- redshift function: \(\Phi(r)=0\)
- shape function: \(b(r)=r_0^2/r\)
- throat radius: \(r_0=2\) by default

The embedding profile is

\[
z(r)=\pm r_0\,\operatorname{arcosh}(r/r_0), \qquad r\ge r_0.
\]

## Run locally

```bash
python -m pip install -r requirements.txt
python wormhole_sim.py
```

The program writes `output/wormhole_embedding.png` and
`output/embedding_profile.csv`.

## GitHub Actions

Every push runs the simulation on a GitHub-hosted runner. The generated plot
and CSV are uploaded as a workflow artifact named `wormhole-results`.

Open the repository's **Actions** tab, select the latest run, and download
the artifact from its summary page.

## Scientific scope and limitations

This is a numerical visualization of a chosen spatial geometry. It does not
solve the full Einstein field equations, establish that traversable wormholes
exist, model the exotic matter/energy conditions needed to support one, or
simulate time travel and closed timelike curves. A successful run only checks
that this particular visualization script executes and produces its outputs.
