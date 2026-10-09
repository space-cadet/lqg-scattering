"""Independent analytic limits and eigenstate checks for dissociation."""
import unittest
import numpy as np
from binding_energy import calculate


class BindingEnergyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = calculate(onsite_values=(0., 5.))["records"]

    def test_free_limit_from_one_particle_orbitals(self):
        # A four-boson singlet occupies at least two orbital modes, two each.
        # The spin-1/2 three-boson fragment occupies the two modes 2+1.
        expected = {"complete": (-4., -3.), "ring": (-4., -2*np.sqrt(2))}
        for row in self.records:
            if row["U"] != 0:
                continue
            channel = row["dissociation_channels"][0]
            full, cut = expected[row["graph"]]
            self.assertAlmostEqual(row["intact_ground"]["energy"], full, places=10)
            self.assertAlmostEqual(channel["energy"], cut, places=10)

    def test_all_reported_ground_states_are_full_space_eigenstates(self):
        for row in self.records:
            self.assertLess(row["intact_ground"]["eigenstate_residual"], 1e-10)
            for channel in row["dissociation_channels"]:
                self.assertLess(channel["eigenstate_residual"], 1e-10)
                self.assertEqual(channel["fragment_bosons"]+channel["isolated_face_bosons"], 4)
                self.assertAlmostEqual(channel["energy"], channel["three_site_fragment_energy"]
                                       +channel["isolated_face_energy"], places=12)

    def test_positive_binding_and_lowest_allocation(self):
        for row in self.records:
            self.assertGreater(row["lowest_nonempty_threshold"]["binding_energy"], 0)
            if row["U"] == 5:
                self.assertEqual(row["lowest_nonempty_threshold"]["isolated_face_bosons"], 1)

    def test_no_hopping_has_no_detachment_cost(self):
        for row in calculate(t=0., onsite_values=(5.,))["records"]:
            self.assertAlmostEqual(row["intact_ground"]["energy"], 0., places=10)
            self.assertAlmostEqual(row["lowest_nonempty_threshold"]["binding_energy"], 0., places=10)


if __name__ == '__main__':
    unittest.main()
