"""Version-4 research-frontier audits: scalar matter, f(R), and stability.

These are transparent algebraic/requirements audits, not a self-consistent
wormhole solution. All quantities are illustrative and use G=c=1.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def scalar_null_contraction(null_gradient: float, kind: str = "canonical") -> float:
    """Return T_ab k^a k^b for a minimally coupled scalar.

    For a null vector k, the potential term drops out. A canonical scalar gives
    +(k.grad(phi))^2; a phantom-sign kinetic term gives the negative.
    """
    if not math.isfinite(null_gradient):
        raise ValueError("null_gradient must be finite")
    if kind not in {"canonical", "phantom"}:
        raise ValueError("kind must be 'canonical' or 'phantom'")
    sign = 1.0 if kind == "canonical" else -1.0
    return sign * null_gradient**2


def fr_effective_null(f_ricci_derivative: float, matter_null: float,
                      derivative_term: float) -> float:
    """Algebraic f(R) null projection: (T_kk + k.k.grad.grad F / 8pi)/F.

    Inputs are local illustrative values, not obtained from a solved geometry.
    """
    if not all(math.isfinite(x) for x in
               (f_ricci_derivative, matter_null, derivative_term)):
        raise ValueError("f(R) audit inputs must be finite")
    if f_ricci_derivative <= 0:
        raise ValueError("F=df/dR must be positive for this diagnostic")
    return (matter_null + derivative_term / (8.0 * math.pi)) / f_ricci_derivative


def build_audit() -> dict:
    gradient = 0.25
    canonical = scalar_null_contraction(gradient, "canonical")
    phantom = scalar_null_contraction(gradient, "phantom")
    derivative_terms = (-0.5, 0.0, 0.5)
    fr_cases = [
        {
            "F=df_dR": 1.0,
            "matter_Tkk": 0.01,
            "k_k_nabla_nabla_F": term,
            "effective_Rkk_over_8pi": fr_effective_null(1.0, 0.01, term),
            "interpretation": "illustrative local algebra only; not a field-equation solution",
        }
        for term in derivative_terms
    ]
    return {
        "version": 4,
        "units": "geometrized (G=c=1)",
        "scope": "research-frontier audit; not a self-consistent wormhole construction",
        "scalar_matter": {
            "null_gradient_example": gradient,
            "canonical_Tkk": canonical,
            "phantom_Tkk": phantom,
            "canonical_respects_null_energy_condition": canonical >= 0,
            "phantom_violates_null_energy_condition_for_nonzero_gradient": phantom < 0,
            "warning": "phantom kinetic sign carries a ghost/negative-kinetic-energy problem; this is not a viable matter proposal",
        },
        "modified_gravity_f_R": {
            "projected_equation": "F R_ab k^a k^b = 8*pi*T_ab k^a k^b + k^a k^b nabla_a nabla_b F",
            "cases": fr_cases,
            "warning": "effective geometric NEC is frame/decomposition dependent; cases do not solve the metric and scalar equations or establish viability",
        },
        "dynamical_stability": {
            "computed": False,
            "status": "NOT COMPUTED",
            "reason": "No dynamical action, matter equations of motion, complete background solution, perturbation boundary conditions, or gauge-fixed linear operator is specified.",
            "required_inputs": [
                "a covariant gravitational action (including any f(R) or scalar-tensor terms)",
                "a matter Lagrangian and its perturbation equations",
                "a self-consistent static or evolving background solving all field equations",
                "regular throat and asymptotic perturbation boundary conditions",
                "gauge choice and constraint elimination before constructing the eigenvalue problem",
            ],
        },
        "scientific_conclusion": [
            "A minimally coupled canonical scalar cannot provide negative null contraction; its potential does not change this null-projected result.",
            "A phantom-sign scalar can violate the NEC algebraically, but introduces a ghost-like kinetic instability concern and is not a demonstrated physical source.",
            "In metric f(R) gravity, derivatives of F=df/dR enter the null-projected field equation; a sign change in an effective geometric contribution is not by itself a viable wormhole solution.",
            "No stability eigenvalues or stability claim are produced in this version.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    audit = build_audit()
    (out / "research_frontier_v4.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = [
        "WORMHOLE RESEARCH FRONTIER — VERSION 4",
        "======================================",
        "Scope: algebraic research audit, not a self-consistent solution.",
        "",
        "SCALAR MATTER",
        f"Canonical scalar T_kk example: {audit['scalar_matter']['canonical_Tkk']:.8g}",
        f"Phantom scalar T_kk example:   {audit['scalar_matter']['phantom_Tkk']:.8g}",
        audit["scalar_matter"]["warning"],
        "",
        "MODIFIED GRAVITY (METRIC f(R))",
        audit["modified_gravity_f_R"]["projected_equation"],
    ]
    for case in audit["modified_gravity_f_R"]["cases"]:
        lines.append(
            "F={F:.3g}, Tkk={T:.3g}, kknabla_nablaF={D:.3g}, "
            "effective null projection={E:.8g}".format(
                F=case["F=df_dR"], T=case["matter_Tkk"],
                D=case["k_k_nabla_nabla_F"], E=case["effective_Rkk_over_8pi"]
            )
        )
    lines += [
        audit["modified_gravity_f_R"]["warning"],
        "",
        "DYNAMICAL STABILITY",
        "NOT COMPUTED",
        audit["dynamical_stability"]["reason"],
        "",
        "CONCLUSION",
        *[f"- {item}" for item in audit["scientific_conclusion"]],
    ]
    (out / "research_frontier_v4_report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("PASS: scalar null-contraction identities")
    print("PASS: f(R) projected-equation diagnostic inputs and finite outputs")
    print("PASS: stability status explicitly marked NOT COMPUTED")
    print("Generated research_frontier_v4.json and research_frontier_v4_report.txt")


if __name__ == "__main__":
    main()
