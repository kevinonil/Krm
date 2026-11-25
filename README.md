# Wormhole numerical simulation

Educational numerical experiments for an **idealized** Morris–Thorne wormhole. This repository separates three different questions: spatial geometry and photon paths, a simplified kinematic clock-offset criterion, and the quantum-field-theory issues often discussed under chronology protection.

## Install and run everything

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python wormhole_sim.py
python chronology_model.py --beta 0.8 --duration-years 10 --separation-ly 1
python quantum_chronology.py --clock-offset-years 4 --separation-ly 1
```

All generated files are written to `output/`. Open `output/wormhole_3d.html` in a browser; Plotly JavaScript is embedded, so the visualization works offline after generation.

## 1. Spatial geometry and photon geodesic

The first simulation uses the ultrastatic Morris–Thorne metric with `Phi(r)=0` and `b(r)=r0^2/r`, expressed using proper-radial coordinate `l`, where `r(l)=sqrt(l^2+r0^2)`. It numerically integrates an equatorial null geodesic and checks the null constraint.

Change its parameters:

```bash
python wormhole_sim.py --throat-radius 3 --r-max 14 --samples 220 --impact-parameter 1.2
```

The impact parameter must be nonnegative and smaller than the throat radius.

Outputs:
- `wormhole_3d.html`: interactive 3D spatial embedding and computed photon path
- `photon_geodesic.csv`: numerical trajectory
- `photon_geodesic.png`: 2D projection
- `simulation_report.txt`: parameters and numerical validation

In geometrized units (`c=1`), `E=1`, `L=impact parameter`:
```
dl/dlambda = v
dv/dlambda = l L^2/(l^2+r0^2)^2
dphi/dlambda = L/(l^2+r0^2)
```

## 2. Idealized chronology threshold

```bash
python chronology_model.py --beta 0.8 --duration-years 10 --separation-ly 1
```

It estimates the special-relativistic moving-clock lag `Delta t = T(1 - sqrt(1-beta^2))` and compares it with the external light-travel time `D/c`. With the example values, the idealized clock offset is 4 years and the external light-travel time is 1 year. This means only that the simplified inequality is satisfied under its assumptions; it is not a construction of a self-consistent spacetime.

Outputs: `chronology_report.txt`, `chronology_sweep.csv`, `chronology_threshold.png`.

## 3. Quantum chronology / backreaction audit

```bash
python quantum_chronology.py --clock-offset-years 4 --separation-ly 1
```

This step explicitly distinguishes the classical kinematic condition from semiclassical gravity. It reports what information would be needed to calculate a renormalized quantum stress-energy expectation value and its gravitational backreaction.

**Important:** the script does not calculate quantum stress-energy. The existing toy model does not specify a complete evolving spacetime, quantum field, quantum state, boundary conditions, or renormalization prescription. It therefore cannot numerically confirm or refute Hawking's chronology-protection conjecture.

The audit summarizes the scope of relevant ideas:
- Hawking's chronology-protection conjecture is a conjecture, not a universal theorem.
- Quantum effects may become problematic near chronology horizons in some models.
- Kay–Radzikowski–Wald results concern failures of the Hadamard condition at certain base points of compactly generated Cauchy horizons; they are not a proof that every possible time-machine geometry is impossible.

Outputs: `quantum_chronology_report.txt` and `quantum_chronology_audit.json`.

## Tests and continuous integration

`tests/test_simulation.py` checks clock-offset limits, the threshold classification, the explicit non-computation status of the quantum audit, throat geometry, photon throat crossing, and the null constraint. GitHub Actions runs the tests and all three experiments, then uploads the generated `wormhole-results` artifact.

## Scientific scope and references

These are educational numerical models, not observed astrophysical wormholes. The photon solver integrates a test trajectory on a prescribed metric; it does not solve the Einstein field equations or establish that the required matter distribution exists. The chronology scripts do not demonstrate that closed timelike curves (CTCs) can form in nature, nor that they are universally forbidden.

Further reading:
- Morris, Thorne & Yurtsever (1988), *Wormholes, Time Machines, and the Weak Energy Condition*, Physical Review Letters 61, 1446.
- Hawking (1992), *Chronology protection conjecture*, Physical Review D 46, 603.
- Kay, Radzikowski & Wald (1997), *Quantum field theory on spacetimes with a compactly generated Cauchy horizon*, Communications in Mathematical Physics 183, 533.
