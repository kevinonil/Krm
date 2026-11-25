"""Numerical null-geodesic demo for an idealized Morris-Thorne wormhole."""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import solve_ivp

def validate(r0, rmax, samples, impact):
    if not np.isfinite(r0) or r0 <= 0: raise ValueError("throat radius must be finite and positive")
    if not np.isfinite(rmax) or rmax <= r0: raise ValueError("r-max must exceed throat radius")
    if not 30 <= samples <= 1200: raise ValueError("samples must be between 30 and 1200")
    if not np.isfinite(impact) or not 0 <= impact < r0: raise ValueError("impact parameter must satisfy 0 <= impact < throat radius")

def embedding(l, r0):
    r = np.sqrt(l*l + r0*r0)
    z = np.sign(l) * r0 * np.arccosh(r/r0)
    return r, z

def integrate_photon(r0, rmax, impact, samples):
    # Equatorial null geodesic; E=c=1, L=impact, affine parameter lambda.
    def rhs(_lam, y):
        l, v, phi = y
        d = l*l + r0*r0
        return [v, l*impact**2/d**2, impact/d]
    l0 = -rmax
    v0 = np.sqrt(1.0 - impact**2/(l0*l0+r0*r0))
    def finish(_lam, y): return y[0]-rmax
    finish.terminal, finish.direction = True, 1
    sol = solve_ivp(rhs, (0, 5*rmax), [l0, v0, 0.0],
                    t_eval=np.linspace(0, 5*rmax, samples*3),
                    events=finish, rtol=1e-9, atol=1e-11, max_step=0.04)
    if not sol.success or len(sol.t) < 10: raise RuntimeError(sol.message)
    l, v, phi = sol.y
    r, z = embedding(l, r0)
    return sol.t, l, v, phi, r*np.cos(phi), r*np.sin(phi), z

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",default="output")
    p.add_argument("--throat-radius",type=float,default=2.0)
    p.add_argument("--r-max",type=float,default=10.0)
    p.add_argument("--samples",type=int,default=180)
    p.add_argument("--impact-parameter",type=float,default=1.0)
    a=p.parse_args()
    validate(a.throat_radius,a.r_max,a.samples,a.impact_parameter)
    out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    tau,l,v,phi,x,y,z=integrate_photon(a.throat_radius,a.r_max,a.impact_parameter,a.samples)
    r,_=embedding(l,a.throat_radius)
    axis=np.linspace(-a.r_max,a.r_max,a.samples)
    theta=np.linspace(0,2*np.pi,100)
    ll,tt=np.meshgrid(axis,theta)
    rr,zz=embedding(ll,a.throat_radius)
    xx,yy=rr*np.cos(tt),rr*np.sin(tt)
    fig=go.Figure()
    fig.add_trace(go.Surface(x=xx,y=yy,z=zz,surfacecolor=ll,colorscale="Viridis",
                             opacity=.78,showscale=False,name="Wormhole spatial slice"))
    fig.add_trace(go.Scatter3d(x=x,y=y,z=z,mode="lines",
                               line=dict(color="#ffcc33",width=7),
                               name="Numerically integrated null geodesic"))
    fig.add_trace(go.Scatter3d(x=[x[0]],y=[y[0]],z=[z[0]],mode="markers",
                               marker=dict(size=5,color="#ff5533"),name="Photon start"))
    fig.update_layout(title=f"Photon null geodesic | throat r0={a.throat_radius:g}",
                      scene=dict(xaxis_title="x",yaxis_title="y",zaxis_title="z",aspectmode="data"),
                      margin=dict(l=0,r=0,b=0,t=55))
    html=out/"wormhole_3d.html"
    fig.write_html(html,include_plotlyjs=True,full_html=True)
    f,ax=plt.subplots(figsize=(9,6))
    ax.plot(x,z,label="Integrated photon path (x-z projection)")
    ax.scatter([0],[0],label="Throat",zorder=4)
    ax.set(title="Photon null geodesic through idealized wormhole",xlabel="x",ylabel="Embedding z")
    ax.grid(True,alpha=.3); ax.legend(); f.tight_layout()
    f.savefig(out/"photon_geodesic.png",dpi=160); plt.close(f)
    np.savetxt(out/"photon_geodesic.csv",np.column_stack((tau,l,r,phi,x,y,z,v)),
               delimiter=",",header="affine_parameter,l,r,phi,x,y,z,dl_dlambda",comments="")
    residual=v*v+a.impact_parameter**2/r**2-1
    err=float(np.max(np.abs(residual)))
    assert l[0]<0<l[-1] and np.all(np.isfinite(np.column_stack((tau,l,phi,x,y,z))))
    assert err<2e-6, f"Null constraint residual too large: {err}"
    (out/"simulation_report.txt").write_text(
        "Morris-Thorne ultrastatic wormhole: numerical null geodesic\n"
        f"throat_radius={a.throat_radius}\nr_max={a.r_max}\nimpact_parameter={a.impact_parameter}\n"
        f"trajectory_points={len(tau)}\nmax_null_constraint_residual={err:.3e}\n"
        "units: geometrized (c=1); idealized metric, not an observed object\n",encoding="utf-8")
    print("PASS: photon crossed the throat")
    print(f"PASS: null-constraint max residual = {err:.3e}")
    print("Generated:",html,"photon_geodesic.csv photon_geodesic.png simulation_report.txt")

if __name__=="__main__": main()
