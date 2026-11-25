"""Regression tests for the educational wormhole simulation."""
import math
import unittest

from chronology_model import classify, time_shift
from quantum_chronology import classical_threshold, quantum_audit
from wormhole_sim import embedding, integrate_photon, validate
from energy_conditions import stress_energy, validate as validate_energy
from photon_bundle import run_bundle


class ChronologyTests(unittest.TestCase):
    def test_twin_clock_default_example(self):
        self.assertAlmostEqual(time_shift(0.8, 10.0), 4.0, places=12)
        self.assertEqual(classify(4.0, 1.0), "CTC condition met in idealized model")

    def test_clock_shift_limits(self):
        self.assertEqual(time_shift(0.0, 10.0), 0.0)
        self.assertGreater(time_shift(0.9, 10.0), time_shift(0.5, 10.0))

    def test_invalid_speed_rejected(self):
        with self.assertRaises(ValueError):
            time_shift(1.0, 10.0)

    def test_quantum_audit_does_not_claim_calculation(self):
        audit = quantum_audit()
        self.assertFalse(audit["quantum_backreaction_computed"])
        self.assertGreaterEqual(len(audit["required_inputs"]), 4)

    def test_classical_threshold_margin(self):
        result = classical_threshold(4.0, 1.0)
        self.assertEqual(result["status"], "kinematic_ctc_condition")
        self.assertAlmostEqual(result["margin_years"], 3.0)

    def test_exact_threshold(self):
        self.assertEqual(classical_threshold(1.0, 1.0)["status"], "threshold")


class GeodesicTests(unittest.TestCase):
    def test_embedding_throat(self):
        r, z = embedding(0.0, 2.0)
        self.assertAlmostEqual(r, 2.0)
        self.assertAlmostEqual(z, 0.0)

    def test_invalid_geometry_rejected(self):
        with self.assertRaises(ValueError):
            validate(2.0, 2.0, 100, 1.0)

    def test_photon_crosses_throat_and_null_constraint(self):
        tau, l, v, phi, x, y, z = integrate_photon(2.0, 10.0, 1.0, 180)
        self.assertLess(l[0], 0.0)
        self.assertGreater(l[-1], 0.0)
        r = (l*l + 2.0**2)**0.5
        residual = v*v + 1.0**2/r**2 - 1.0
        self.assertLess(float(abs(residual).max()), 2e-6)
        self.assertTrue(all(math.isfinite(float(value)) for value in (tau[-1], phi[-1], x[-1], y[-1], z[-1])))


class ResearchV2Tests(unittest.TestCase):
    def test_morris_thorne_radial_nec_is_violated(self):
        data = stress_energy(2.0, throat_radius=2.0, exponent=1.0)
        self.assertAlmostEqual(float(data["rho_plus_p_r"]), -1.0 / (16.0 * math.pi), places=12)
        self.assertLess(float(data["rho_plus_p_r"]), 0.0)

    def test_transverse_nec_and_sec_identity_at_throat(self):
        data = stress_energy(2.0, throat_radius=2.0, exponent=1.0)
        self.assertAlmostEqual(float(data["rho_plus_p_t"]), 0.0, places=12)
        self.assertAlmostEqual(float(data["rho_plus_p_r_plus_2p_t"]), 0.0, places=12)

    def test_energy_model_rejects_non_asymptotically_flat_exponent(self):
        with self.assertRaises(ValueError):
            validate_energy(2.0, -1.0, 10.0, 100)

    def test_photon_bundle_crosses_for_each_impact(self):
        paths = run_bundle(2.0, 10.0, [0.0, 0.5, 1.0], 60)
        self.assertEqual(len(paths), 3)
        self.assertTrue(all(path["l"][0] < 0 < path["l"][-1] for path in paths))
        self.assertLess(max(path["max_null_residual"] for path in paths), 2e-6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
