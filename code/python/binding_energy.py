"""Same-number, total-singlet dissociation thresholds for the four-site model."""
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.linalg import eigh

from lqg_scattering.hamiltonian import build_fixed_number_model, assemble_hamiltonian
from lqg_scattering.preparations import closed_fl_tetrahedron
from lqg_scattering.total_spin import total_spin_operators
from project_paths import RESULTS_ROOT


def singlet_basis(spin_squared, rows):
    """Orthonormal total-spin-zero columns supported on the selected rows."""
    values, vectors = eigh(spin_squared[np.ix_(rows, rows)])
    basis = np.zeros((len(spin_squared), np.count_nonzero(abs(values) < 1e-10)), complex)
    basis[rows] = vectors[:, abs(values) < 1e-10]
    return basis


def ground_readout(hamiltonian, basis):
    """Lowest energy and full-space residual, including possible degeneracy."""
    values, vectors = eigh(basis.conj().T @ (hamiltonian @ basis))
    state = basis @ vectors[:, 0]
    energy = float(values[0])
    residual = float(np.linalg.norm(hamiltonian @ state - energy * state))
    return {"energy": energy, "eigenstate_residual": residual,
            "sector_dimension": basis.shape[1],
            "ground_degeneracy": int(np.count_nonzero(abs(values-energy) < 1e-9))}


def energy_readout(hamiltonian, state):
    mean = float(np.vdot(state, hamiltonian @ state).real)
    return {"mean_energy": mean,
            "energy_std": float(np.linalg.norm(hamiltonian @ state - mean*state))}


def calculate(n_bosons=4, t=1., onsite_values=(0., 1., 5., 20.)):
    graphs = {"complete": tuple(itertools.combinations(range(4), 2)),
              "ring": ((0, 1), (1, 2), (2, 3), (0, 3))}
    records = []
    for graph, edges in graphs.items():
        intact = build_fixed_number_model(4, n_bosons, edges)
        cut_edges = tuple(edge for edge in edges if 3 not in edge)
        separated = build_fixed_number_model(4, n_bosons, cut_edges)
        occupations = intact["occupations"]
        squared = total_spin_operators(occupations, intact["index"], 4)["squared"].toarray()
        full_basis = singlet_basis(squared, np.arange(len(occupations)))
        fourth_number = occupations[:, 6] + occupations[:, 7]
        channels = {n4: singlet_basis(squared, np.flatnonzero(fourth_number == n4))
                    for n4 in range(1, n_bosons)}
        for U in onsite_values:
            h_full = assemble_hamiltonian(intact, t, U)
            h_cut = assemble_hamiltonian(separated, t, U)
            bound = ground_readout(h_full, full_basis)
            thresholds = []
            for n4, basis in channels.items():
                if not basis.shape[1]:
                    continue
                result = ground_readout(h_cut, basis)
                result.update({"fragment_bosons": n_bosons-n4, "isolated_face_bosons": n4,
                               "fragment_total_spin": n4/2, "isolated_face_spin": n4/2,
                               "isolated_face_energy": float(U*n4*(n4-1)/2),
                               "binding_energy": result["energy"]-bound["energy"]})
                result["three_site_fragment_energy"] = result["energy"]-result["isolated_face_energy"]
                thresholds.append(result)
            row = {"graph": graph, "intact_edges": edges, "separated_edges": cut_edges,
                   "n_bosons": n_bosons, "t": t, "U": U, "intact_ground": bound,
                   "dissociation_channels": thresholds,
                   "lowest_nonempty_threshold": min(thresholds, key=lambda r: r["energy"])}
            if n_bosons == 4:
                seed = closed_fl_tetrahedron(intact, area_label=2)
                row["FL_seed_intact"] = energy_readout(h_full, seed)
                row["FL_seed_after_cut"] = energy_readout(h_cut, seed)
            records.append(row)
    return {"schema_version": 1,
            "hamiltonian": "H=-t sum_edges(E_ij+E_ji)+U/2 sum_i n_i(n_i-1)",
            "sector": "fixed total boson number, combined total SU(2) spin zero",
            "binding_definition": "lowest separated channel energy minus intact singlet ground energy",
            "separation": "delete every hopping edge incident on site 3; retain its modes and onsite term",
            "scope": "finite graph detachment energy; no spatial potential or continuum threshold specified",
            "records": records}


if __name__ == "__main__":
    report = calculate()
    output = RESULTS_ROOT / "binding-energy" / "summary.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    for row in report["records"]:
        channel = next(c for c in row["dissociation_channels"] if c["isolated_face_bosons"] == 1)
        print(f'{row["graph"]} U={row["U"]:g}: E_tet={row["intact_ground"]["energy"]:.9f}, '
              f'E_3+1={channel["energy"]:.9f}, binding={channel["binding_energy"]:.9f}')
    print(output)
