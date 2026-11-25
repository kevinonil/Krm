"""Semiclassical chronology-protection audit for the toy wormhole model.

This module deliberately does NOT fabricate a quantum stress-energy estimate.
A kinematic clock offset is insufficient to determine <T_ab>, its backreaction,
or whether a self-consistent spacetime develops a Cauchy horizon.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import math


def classical_threshold(offset_years: float, separation_ly: float) -> dict:
    """Return the idealized kinematic comparison, with c=1 ly/year."""
    if not math.isfinite(offset_years) or offset_years < 0:
        raise ValueError("offset_years must be finite and nonnegative")
    if not math.isfinite(separation_ly) or separation_ly <= 0:
        raise ValueError("separation_ly must be finite and positive")
    margin = offset_years - separation_ly
    if math.isclose(margin, 0.0, rel_tol=1e-10, abs_tol=1e-12):
        status = "threshold"
    elif margin > 0:
        status = "kinematic_ctc_condition"
    else:
        status = "below_threshold"
    return {
        "clock_offset_years": offset_years,
        "external_light_travel_years": separation_ly,
        "margin_years": margin,
        "status": status,
    }


def quantum_audit() -> dict:
    """Describe what can and cannot be inferred without a QFT-in-curved-space model."""
    return {
        "quantum_backreaction_computed": False,
        "reason": (
            "The toy model supplies no quantum field, quantum state, renormalization "
            "prescription, complete spacetime metric, or boundary conditions."
        ),
        "required_inputs": [
            "A globally specified spacetime metric and its evolution near the would-be chronology horizon",
            "A quantum field model (field content, masses, and couplings)",
            "A physically specified quantum state and boundary/initial conditions",
            "A renormalization prescription for the stress-energy expectation value",
            "A self-consistent semiclassical Einstein equation including backreaction",
        ],
        "interpretation": [
            "The classical inequality is only a kinematic condition in an idealized construction.",
            "Hawking's chronology-protection idea is a conjecture, not a universally proven theorem.",
            "Quantum stress-energy may become large or ill-behaved near a chronology horizon in some settings.",
            "Kay-Radzikowski-Wald results show failures of the Hadamard condition at certain base points of compactly generated Cauchy horizons; they do not prove every conceivable wormhole time-machine model impossible.",
            "No conclusion that a real CTC forms or is universally forbidden follows from this script.",
        ],
    }


def build_report(offset_years: float, separation_ly: float) -> tuple[dict, str]:
    classical = classical_threshold(offset_years, separation_ly)
    quantum = quantum_audit()
    payload = {"classical_kinematic_check": classical, "semiclassical_audit": quantum}
    lines = [
        "QUANTUM CHRONOLOGY / BACKREACTION AUDIT",
        "========================================",
        "",
        "1. IDEALIZED CLASSICAL KINEMATIC CHECK",
        f"Clock offset: {offset_years:.12g} years",
        f"External light-travel time: {separation_ly:.12g} years (c=1 ly/year)",
        f"Margin (offset - travel time): {classical['margin_years']:.12g} years",
        f"Classification: {classical['status']}",
        "",
        "2. SEMICLASSICAL / QUANTUM CHECK",
        "Quantum stress-energy and metric backreaction: NOT COMPUTED.",
        quantum["reason"],
        "",
        "Required ingredients for a real calculation:",
        *[f"- {item}" for item in quantum["required_inputs"]],
        "",
        "Interpretation and limitations:",
        *[f"- {item}" for item in quantum["interpretation"]],
        "",
        "3. REFERENCES FOR FURTHER STUDY",
        "Morris, Thorne & Yurtsever (1988), Wormholes, Time Machines, and the Weak Energy Condition, Physical Review Letters 61, 1446.",
        "Kay, Radzikowski & Wald (1997), Quantum field theory on spacetimes with a compactly generated Cauchy horizon, Communications in Mathematical Physics 183, 533.",
        "Hawking (1992), Chronology protection conjecture, Physical Review D 46, 603.",
        "",
        "This is an educational diagnostic, not a numerical quantum-field calculation,",
        "a proof of chronology protection, or evidence that a traversable wormhole exists.",
    ]
    return payload, "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clock-offset-years", type=float, default=4.0)
    parser.add_argument("--separation-ly", type=float, default=1.0)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()
    try:
        payload, report = build_report(args.clock_offset_years, args.separation_ly)
    except ValueError as exc:
        parser.error(str(exc))
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "quantum_chronology_audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output / "quantum_chronology_report.txt").write_text(report, encoding="utf-8")
    print("PASS: classical threshold validated; quantum backreaction explicitly marked NOT COMPUTED")
    print(f"Classical classification: {payload['classical_kinematic_check']['status']}")
    print("Generated quantum_chronology_audit.json and quantum_chronology_report.txt")


if __name__ == "__main__":
    main()
