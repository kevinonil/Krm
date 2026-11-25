"""Toy chronology-condition calculator for an idealized wormhole time shift.

All times are in years and distances in light-years (so c=1 ly/year).
This evaluates a textbook kinematic threshold, not a self-consistent
spacetime solution or a physically buildable time machine.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def time_shift(beta: float, duration_years: float) -> float:
    if not np.isfinite(beta) or not 0 <= beta < 1:
        raise ValueError("beta must be in [0, 1)")
    if not np.isfinite(duration_years) or duration_years < 0:
        raise ValueError("duration must be finite and nonnegative")
    gamma = 1.0 / np.sqrt(1.0 - beta * beta)
    return duration_years * (1.0 - 1.0 / gamma)

def classify(delta_t: float, separation_ly: float) -> str:
    if not np.isfinite(separation_ly) or separation_ly <= 0:
        raise ValueError("mouth separation must be finite and positive")
    threshold = separation_ly  # c=1 ly/year
    if np.isclose(delta_t, threshold, rtol=1e-10, atol=1e-12):
        return "threshold (closed null curve in idealized model)"
    return "CTC condition met in idealized model" if delta_t > threshold else "below CTC threshold"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--beta",type=float,default=0.8,help="moving-mouth speed as fraction of c")
    p.add_argument("--duration-years",type=float,default=10.0)
    p.add_argument("--separation-ly",type=float,default=1.0)
    p.add_argument("--output-dir",default="output")
    a=p.parse_args()
    if not 0 <= a.beta < 1: p.error("--beta must be in [0, 1)")
    if a.duration_years < 0: p.error("--duration-years must be nonnegative")
    if a.separation_ly <= 0: p.error("--separation-ly must be positive")
    out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    delta=time_shift(a.beta,a.duration_years)
    threshold=a.separation_ly
    result=classify(delta,threshold)
    betas=np.linspace(0,0.99,300)
    shifts=np.array([time_shift(float(b),a.duration_years) for b in betas])
    with (out/"chronology_sweep.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["beta_v_over_c","duration_years","time_shift_years","outside_light_travel_years"])
        w.writerows((float(b),a.duration_years,float(dt),threshold) for b,dt in zip(betas,shifts))
    fig,ax=plt.subplots(figsize=(9,6))
    ax.plot(betas,shifts,label="Idealized mouth-clock offset")
    ax.axhline(threshold,linestyle="--",label="Outside light-travel time D/c")
    ax.axvline(a.beta,linestyle=":",label=f"Selected beta={a.beta:g}")
    ax.scatter([a.beta],[delta],zorder=4)
    ax.set(xlabel="Moving-mouth speed β = v/c",ylabel="Time difference (years)",
           title="Idealized wormhole chronology threshold")
    ax.grid(True,alpha=.3); ax.legend(); fig.tight_layout()
    fig.savefig(out/"chronology_threshold.png",dpi=160); plt.close(fig)
    report=(
      "IDEALIZED CHRONOLOGY THRESHOLD — NOT A PHYSICAL TIME-MACHINE MODEL\n"
      f"beta={a.beta}\nduration_years={a.duration_years}\n"
      f"mouth_separation_light_years={a.separation_ly}\n"
      f"calculated_clock_offset_years={delta:.12g}\n"
      f"outside_light_travel_time_years={threshold:.12g}\n"
      f"classification={result}\n"
      "Assumptions: special-relativistic twin-clock estimate; c=1 ly/year; "
      "instantaneous/idealized wormhole identification.\n"
      "This ignores wormhole construction, stress-energy, quantum effects, "
      "backreaction, mouth dynamics and global spacetime consistency.\n"
      "The inequality is a conditional result in a hypothetical geometry, "
      "not evidence that CTCs can exist in nature.\n"
    )
    (out/"chronology_report.txt").write_text(report,encoding="utf-8")
    assert delta >= 0 and shifts[0] == 0
    assert np.all(np.diff(shifts) >= -1e-12)
    print("PASS: time-shift calculation and monotonicity checks")
    print(f"Clock offset: {delta:.6f} years")
    print(f"Outside light-travel threshold: {threshold:.6f} years")
    print(f"Result: {result}")
    print("Generated chronology_report.txt, chronology_sweep.csv, chronology_threshold.png")

if __name__=="__main__": main()
