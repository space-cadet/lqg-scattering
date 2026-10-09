"""Fixed-number Bose–Hubbard operators and the four-site singlet pilot.

The full-space builder accepts a fixed boson number and an undirected graph.
The existing singlet/volume pilot retains its validated four-site scope.
Graph and interaction sampling, tables, plots, and file output live in drivers.
"""
import itertools
import math
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse import csr_matrix, diags
from .fixed_k import fixed_number_basis
from .labels import (compositions as weak_compositions, enumerate_total_area,
                     fixed_face_dimension, positive_face_dimension)
from .singlets import (ABS_TOL, GAMMA, canonical_data, closure_residual,
                       coupling_basis, root_abs)

SITES = 4
TRIPLES = tuple(itertools.combinations(range(SITES), 3))


def build_fixed_number_model(n_sites, n_bosons, edges):
    """Build sparse hopping and onsite terms without a spin projection.

    All 2*n_sites Schwinger occupations with sum n_bosons are included.
    Edges are undirected, unique, and have unit hopping weight. Odd boson
    numbers and the vacuum are supported. Volume is not built here.
    """
    for name, value, minimum in (("n_sites", n_sites, 1),
                                  ("n_bosons", n_bosons, 0)):
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    n_sites, n_bosons = int(n_sites), int(n_bosons)
    selected = []
    for edge in edges:
        if len(edge) != 2:
            raise ValueError("each edge must contain two site indices")
        i, j = edge
        if any(isinstance(v, (bool, np.bool_)) or not isinstance(v, (int, np.integer))
               or not 0 <= v < n_sites for v in edge) or i == j:
            raise ValueError(f"invalid hopping edge: {edge}")
        selected.append(tuple(sorted((int(i), int(j)))))
    if len(set(selected)) != len(selected):
        raise ValueError("duplicate undirected hopping edges")
    selected = tuple(sorted(selected))
    occupations, _ = fixed_number_basis(n_sites, n_bosons)
    # Tuple keys avoid narrowing occupation numbers and match hopping_matrix.
    index = {tuple(int(x) for x in state): row for row, state in enumerate(occupations)}
    numbers = occupations[:, ::2] + occupations[:, 1::2]
    onsite_values = 0.5 * np.sum(numbers * (numbers - 1), axis=1)
    return {
        "occupations": occupations,
        "index": index,
        "edges": selected,
        "bonds": {edge: hopping_matrix(occupations, index, edge) for edge in selected},
        "onsite": diags(onsite_values, format="csr", dtype=complex),
        "metadata": {
            "available_sites": n_sites,
            "fixed_boson_number": n_bosons,
            "dimension": len(occupations),
            "spin_restriction": "none",
            "mode_order": "(a0,b0,a1,b1,...)",
        },
    }


def assemble_hamiltonian(model, t, U):
    """Return H=-t*sum_edges(E_ij+E_ji)+U*onsite as a CSR matrix."""
    for name, value in (("t", t), ("U", U)):
        if np.ndim(value) != 0 or not np.isrealobj(value) or not np.isfinite(value):
            raise ValueError(f"{name} must be a finite real scalar")
    onsite = csr_matrix(model["onsite"])
    hopping = sum((csr_matrix(bond) for bond in model["bonds"].values()),
                  csr_matrix(onsite.shape, dtype=complex))
    return (-float(t) * hopping + float(U) * onsite).tocsr()


def magnetic_basis(k):
    """All four-site occupation states with N_a=N_b=K."""
    rows = []
    for aa in weak_compositions(k, SITES):
        for bb in weak_compositions(k, SITES):
            rows.append(tuple(x for pair in zip(aa, bb) for x in pair))
    return rows


def connected_triples(edges):
    edge_set = {tuple(sorted(edge)) for edge in edges}
    selected = []
    for triple in TRIPLES:
        induced_edges = sum(
            tuple(sorted(pair)) in edge_set for pair in itertools.combinations(triple, 2)
        )
        if induced_edges >= len(triple) - 1:
            selected.append(triple)
    return tuple(selected)


def hopping_matrix(occupations, index, edge):
    """Matrix of E_ij+E_ji in an occupation basis closed under hopping."""
    i, j = edge
    rows, cols, data = [], [], []
    for col, state in enumerate(occupations):
        for source, target in ((i, j), (j, i)):
            for species in (0, 1):
                source_slot, target_slot = 2 * source + species, 2 * target + species
                if state[source_slot] == 0:
                    continue
                changed = list(state)
                amplitude = math.sqrt((state[target_slot] + 1) * state[source_slot])
                changed[target_slot] += 1
                changed[source_slot] -= 1
                row = index[tuple(changed)]
                rows.append(row)
                cols.append(col)
                data.append(amplitude)
    return coo_matrix((data, (rows, cols)), shape=(len(occupations),) * 2).tocsr()


def expected_closed_dimension(k):
    return fixed_face_dimension(SITES, k)


def infinite_temperature_counts(k):
    total = expected_closed_dimension(k)
    return [{
        "K": k,
        "active_sites": n,
        "closed_states_for_labelled_active_sites": positive_face_dimension(n, k),
        "site_placements": math.comb(SITES, n),
        "total_states": math.comb(SITES, n) * positive_face_dimension(n, k),
        "probability": (math.comb(SITES, n) * positive_face_dimension(n, k) / total),
    } for n in range(1, SITES + 1)]


def build_fixed_k(k):
    """Build the complete singlet basis, hopping terms, onsite term, and V_tau."""
    occupations_m0 = magnetic_basis(k)
    mag_index = {state: row for row, state in enumerate(occupations_m0)}
    expected_m0 = math.comb(k + SITES - 1, SITES - 1) ** 2
    if len(occupations_m0) != expected_m0:
        raise AssertionError("M=0 occupation count disagrees with stars-and-bars")

    assignments = enumerate_total_area(k)["sectors"]
    dimension = sum(len(record["intermediateTwiceK"]) for record in assignments)
    if dimension != expected_closed_dimension(k):
        raise AssertionError("closed singlet dimension disagrees with the exact formula")

    basis = np.zeros((len(occupations_m0), dimension), dtype=complex)
    sector_labels = []
    site_spins = np.zeros((dimension, SITES), dtype=np.int16)
    active_sites = np.zeros(dimension, dtype=np.int8)
    onsite_diag = np.zeros(len(occupations_m0), dtype=float)
    volume_by_triple = {triple: np.zeros((dimension, dimension), complex) for triple in TRIPLES}
    spin_dot_blocks = {pair: np.zeros((dimension, dimension), complex)
                       for pair in itertools.combinations(range(SITES), 2)}
    max_closure = 0.0
    col_start = 0

    for block_index, assignment in enumerate(assignments):
        spins = tuple(assignment["twiceSpins"])
        twice_ks = tuple(assignment["intermediateTwiceK"])
        canonical_spins = tuple(sorted(spins))
        canonical_occupations, canonical_dots, _ = canonical_data(canonical_spins)
        block_occupations, block_basis, inverse = coupling_basis(
            spins, twice_ks, canonical_occupations
        )
        block_dimension = len(twice_ks)
        col_stop = col_start + block_dimension
        block_rows = np.asarray([mag_index[state] for state in block_occupations], dtype=int)
        basis[np.ix_(block_rows, np.arange(col_start, col_stop))] = block_basis
        max_closure = max(max_closure, closure_residual(block_occupations, block_basis))
        if np.max(abs(block_basis.conj().T @ block_basis - np.eye(block_dimension))) > ABS_TOL:
            raise AssertionError(f"non-orthonormal coupling basis in block {block_index}")

        for col in range(col_start, col_stop):
            site_spins[col, :] = np.asarray(spins, dtype=np.int16)
            active_sites[col] = sum(value > 0 for value in spins)
        for state in block_occupations:
            onsite_diag[mag_index[state]] = 0.5 * sum(
                (state[2 * site] + state[2 * site + 1])
                * (state[2 * site] + state[2 * site + 1] - 1)
                for site in range(SITES)
            )

        dots = {
            pair: canonical_dots[tuple(sorted((inverse[pair[0]], inverse[pair[1]])))]
            for pair in itertools.combinations(range(SITES), 2)
        }
        small_dots = {pair: block_basis.conj().T @ (matrix @ block_basis)
                      for pair, matrix in dots.items()}
        for pair, matrix in small_dots.items():
            spin_dot_blocks[pair][col_start:col_stop, col_start:col_stop] = matrix
        for triple in TRIPLES:
            i, j, ell = triple
            q = 1j * (small_dots[i, j] @ small_dots[j, ell]
                      - small_dots[j, ell] @ small_dots[i, j])
            q = (q + q.conj().T) / 2
            block_volume, _ = root_abs(q)
            volume_by_triple[triple][col_start:col_stop, col_start:col_stop] = (
                GAMMA ** 1.5 * block_volume
            )

        sector_labels.extend({
            "state_index": col + 1,
            "block": block_index,
            "n0": spins[0], "n1": spins[1], "n2": spins[2], "n3": spins[3],
            "twice_k_pair": twice_k,
            "active_sites": sum(value > 0 for value in spins),
        } for col, twice_k in zip(range(col_start, col_stop), twice_ks))
        col_start = col_stop

    gram_residual = float(np.max(abs(basis.conj().T @ basis - np.eye(dimension))))
    if gram_residual > ABS_TOL:
        raise AssertionError("coupled singlets are not an orthonormal M=0 subspace")

    onsite = basis.conj().T @ (onsite_diag[:, None] * basis)
    bonds = {}
    for edge in itertools.combinations(range(SITES), 2):
        mag_hop = hopping_matrix(occupations_m0, mag_index, edge)
        bonds[edge] = basis.conj().T @ (mag_hop @ basis)
        residual = float(np.max(abs(bonds[edge] - bonds[edge].conj().T)))
        if residual > ABS_TOL:
            raise AssertionError(f"projected hopping term is not Hermitian for edge {edge}")

    metadata = {
        "K": k,
        "fixed_boson_number": 2 * k,
        "available_sites": SITES,
        "magnetic_M0_dimension": len(occupations_m0),
        "M0_rows_with_singlet_support": int(np.count_nonzero(np.linalg.norm(basis, axis=1) > ABS_TOL)),
        "closed_singlet_dimension": dimension,
        "singlet_basis_orthogonality_max_abs": gram_residual,
        "singlet_closure_max_abs": float(max_closure),
        "active_site_counts": {str(n): int(np.count_nonzero(active_sites == n))
                                for n in range(1, SITES + 1)},
    }
    return {
        "occupations_m0": occupations_m0,
        "basis": basis,
        "labels": sector_labels,
        "site_spins": site_spins,
        "active_sites": active_sites,
        "onsite": onsite,
        "bonds": bonds,
        "spin_dots": spin_dot_blocks,
        "volume_by_triple": volume_by_triple,
        "metadata": metadata,
    }

