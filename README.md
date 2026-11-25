# Wormhole numerical simulation

Educational numerical experiment on an idealized ultrastatic Morris-Thorne
wormhole with Phi(r)=0 and b(r)=r0^2/r.

## Features
- Two-sheet spatial embedding in proper-radial coordinate l, with r(l)=sqrt(l^2+r0^2).
- Numerical integration of an equatorial photon null geodesic using scipy.solve_ivp.
- Null-constraint consistency check.
- Interactive self-contained 3D HTML, trajectory CSV, PNG projection, and text report.

## Run
```bash
python -m pip install -r requirements.txt
python wormhole_sim.py
```
Open `output/wormhole_3d.html` in a browser. Plotly JavaScript is embedded,
so the HTML works offline after generation.

Change parameters:
```bash
python wormhole_sim.py --throat-radius 3 --r-max 14 --samples 220 --impact-parameter 1.2
```
The impact parameter must be nonnegative and smaller than the throat radius.

## Outputs
- `wormhole_3d.html`: interactive 3D embedding and computed photon path
- `photon_geodesic.csv`: numerical trajectory samples
- `photon_geodesic.png`: 2D projection
- `simulation_report.txt`: parameters and numerical validation

## Equations and scope
In geometrized units (c=1), E=1, L=impact parameter:
```
dl/dlambda = v
dv/dlambda = l L^2/(l^2+r0^2)^2
dphi/dlambda = L/(l^2+r0^2)
```
This integrates a test photon on a prescribed metric. It does not solve the
Einstein field equations, establish that the required matter distribution
exists, or demonstrate a physical wormhole, time travel, or closed timelike
curves. Passing tests confirms numerical execution and internal consistency only.
