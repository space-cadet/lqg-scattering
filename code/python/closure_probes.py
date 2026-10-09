"""Compare closed and open Schwinger initial states under graph hopping.

Run from the repository root. Saves reproducible energies, face populations,
total-spin probabilities, closure readouts, and finite-time unitary evolution
for a closed FL tetrahedron, a single face, and a missing-face product state.
The open-state runs are operator probes; no open-state geometric volume is
assigned.
"""
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import expm_multiply

from lqg_scattering.conventions import GAMMA
from lqg_scattering.hamiltonian import assemble_hamiltonian, build_fixed_number_model
from lqg_scattering.preparations import closed_fl_tetrahedron, coherent_face_product
from lqg_scattering.spinors import spinors_from_normals
from lqg_scattering.total_spin import closure_diagnostics, total_spin_operators
from lqg_scattering.tetrahedra import TETRAHEDRON_NORMALS
from project_paths import RESULTS_ROOT


TIMES = (0., .1, .25, .5, 1.)
T = 1.
U = 5.


def build_probe_states():
    """Use one FL singlet, one j=1 face, and three j=1/2 tetrahedral faces."""
    normals = TETRAHEDRON_NORMALS
    spinors = spinors_from_normals(normals)
    definitions = (
        ("closed_fl_tetrahedron", 4,
         lambda model: closed_fl_tetrahedron(model, area_label=2),
         "Four-face regular FL coherent intertwiner, total area label 2; exact singlet."),
        ("single_face_j1", 2,
         lambda model: coherent_face_product(model, (2, 0, 0, 0),
                                             np.vstack((spinors[0], np.tile([1., 0.], (3, 1)))),),
         "One j=1 face aligned with tetrahedron face 0; remaining sites empty."),
        ("three_faces_missing_fourth", 3,
         lambda model: coherent_face_product(model, (1, 1, 1, 0),
                                             np.vstack((spinors[0], spinors[1], spinors[2], [1., 0.]))),
         "Product of three j=1/2 coherent faces along tetrahedron normals 0,1,2; face 3 absent."),
    )
    return definitions, spinors


def run(output_dir):
    definitions, spinors = build_probe_states()
    records = []
    for graph, edges in (
        ("complete", tuple(itertools.combinations(range(4), 2))),
        ("ring", ((0, 1), (1, 2), (2, 3), (0, 3))),
    ):
        for name, bosons, prepare, state_definition in definitions:
            model = build_fixed_number_model(4, bosons, edges)
            state = prepare(model)
            spin = total_spin_operators(model["occupations"], model["index"], 4)
            hamiltonian = assemble_hamiltonian(model, T, U)
            initial = closure_diagnostics(state, spin)
            local_numbers = model["occupations"][:, ::2] + model["occupations"][:, 1::2]
            rows = []
            for time in TIMES:
                current = state if time == 0 else expm_multiply(-1j * time * hamiltonian, state)
                probabilities = abs(current) ** 2
                readout = closure_diagnostics(current, spin)
                rows.append({
                    "time": time,
                    "norm": float(np.vdot(current, current).real),
                    "mean_face_bosons": (probabilities @ local_numbers).tolist(),
                    "mean_face_areas_project_units": (GAMMA * probabilities @ local_numbers).tolist(),
                    "mean_onsite_pair_count": float(probabilities @ model["onsite"].diagonal().real),
                    "mean_total_spin_squared": readout["mean_total_spin_squared"],
                    "spin_sector_probabilities": {str(j): p for j, p in readout["total_spin_probabilities"].items()},
                    "rms_closure_defect": readout["rms_closure_defect"],
                })
            records.append({
                "state": name,
                "description": state_definition,
                "graph": graph,
                "n_sites": 4,
                "fixed_boson_number": bosons,
                "hilbert_dimension": model["metadata"]["dimension"],
                "hopping_t": T,
                "onsite_U": U,
                "initial_energy": float(np.vdot(state, hamiltonian @ state).real),
                "initial_energy_std": float(np.sqrt(max(0.,
                    np.vdot(state, hamiltonian @ (hamiltonian @ state)).real
                    - np.vdot(state, hamiltonian @ state).real**2))),
                "initial_closure": initial,
                "evolution": rows,
            })
    report = {
        "schema_version": 1,
        "model": "Four-site two-component Schwinger Bose-Hubbard hopping plus onsite repulsion",
        "hamiltonian": "H=-t*sum_edges(E_ij+E_ji)+U/2*sum_i n_i(n_i-1)",
        "units": {"hbar": 1., "gamma": GAMMA, "face_area_project_units": "gamma*<n_a+n_b>"},
        "initial_state_conventions": {
            "closed": "Existing fixed-area Freidel-Livine intertwiner at area label 2, embedded in the fixed four-boson sector.",
            "single_face": "Spin-coherent j=1 state on site 0, other sites empty.",
            "missing_face": "Spin-coherent j=1/2 product on sites 0,1,2 using the corresponding outward normals of the regular tetrahedron; site 3 empty.",
            "open_state_volume": "No geometric volume is assigned to non-singlets.",
        },
        "times": list(TIMES),
        "records": records,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "summary.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    return path


if __name__ == "__main__":
    print(run(RESULTS_ROOT / "state-space-probes"))
