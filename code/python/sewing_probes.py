"""Small constructive triangle, tetrahedron, and glued-boundary networks."""
import json
import numpy as np
from lqg_scattering.sewing import triangle_tensor, contract_network, trivalent_graph_edges
from project_paths import RESULTS_ROOT

TET_FACES = (('AB', 'BC', 'AC'), ('AB', 'BD', 'AD'),
             ('AC', 'CD', 'AD'), ('BC', 'CD', 'BD'))
PRISM_FACES = (('AB', 'BD', 'AD'), ('AC', 'CD', 'AD'), ('BC', 'CD', 'BD'),
               ('AB', 'BE', 'AE'), ('AC', 'CE', 'AE'), ('BC', 'CE', 'BE'))


def run():
    triangle, spins = triangle_tensor()
    tet, _ = contract_network([triangle]*4, trivalent_graph_edges(TET_FACES))
    # Removing ABC exposes the AB, AC, BC representation legs.
    patch, open_legs = contract_network([triangle]*3, trivalent_graph_edges(TET_FACES[1:]))
    patch_norm = float(np.linalg.norm(patch))
    normalized_patch = patch/patch_norm
    glued, _ = contract_network([normalized_patch]*2,
                               tuple(((0, i), (1, i)) for i in range(3)))
    prism, _ = contract_network([triangle]*6, trivalent_graph_edges(PRISM_FACES))
    output = {
        'triangle': {'pair_powers': [1, 1, 1], 'twice_edge_spins': spins,
                     'tensor_shape': triangle.shape, 'nonzero_entries': int(np.count_nonzero(triangle)),
                     'norm': float(np.linalg.norm(triangle))},
        'single_tetrahedron': {'faces': TET_FACES, 'sewn_edges': 6,
                              'identity_network_evaluation': float(tet)},
        'open_tetrahedron_patch': {'faces': TET_FACES[1:], 'boundary_edges': ['AB', 'AC', 'BC'],
                                  'open_legs': open_legs, 'tensor_shape': patch.shape,
                                  'raw_norm': patch_norm, 'normalized_norm': float(np.linalg.norm(normalized_patch))},
        'two_separate_open_patches': {'norm': float(np.linalg.norm(normalized_patch)**2),
                                     'boundary_tensor_entries': int(normalized_patch.size**2)},
        'glued_patches': {'normalized_boundary_contraction': float(glued),
                         'six_exterior_faces': PRISM_FACES, 'exterior_sewn_edges': 9,
                         'prism_identity_network_evaluation': float(prism)},
        'interpretation': 'Complete contractions are scalar network evaluations, not ket norms or energies. '
                          'Boundary tensors are normalized kets on their unsewn edge spaces. '
                          'Keep link holonomy arguments or physical indices to obtain a nontrivial closed-network state. '
                          'No Hamiltonian or binding energy assigned to these networks.',
    }
    folder = RESULTS_ROOT/'sewing-probes'
    folder.mkdir(parents=True, exist_ok=True)
    (folder/'summary.json').write_text(json.dumps(output, indent=2)+'\n')
    np.savez(folder/'tensors.npz', triangle=triangle, open_patch=normalized_patch)
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    run()
