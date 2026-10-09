"""F-pair triangle tensors and oriented SU(2) edge sewing.

All magnetic indices use increasing m, equivalently increasing a occupation.
Full contraction evaluates a network at identity; it is not a normalized
many-body ket. Uncontracted legs remain explicit tensor indices.
"""
import math
import numpy as np


def triangle_tensor(powers=(1, 1, 1)):
    """Normalized (F12†)^p12 (F23†)^p23 (F31†)^p31 vacuum.

    Return a tensor on the three edge representation spaces and their 2j.
    The creator amplitudes are evaluated in normalized oscillator Fock states.
    """
    powers = tuple(powers)
    if len(powers) != 3 or any(isinstance(p, bool) or not isinstance(p, int) or p < 0 for p in powers):
        raise ValueError('powers must be three nonnegative integers')
    state = {(0,)*6: 1.}
    for (i, j), power in zip(((0, 1), (1, 2), (2, 0)), powers):
        for _ in range(power):
            out = {}
            for occ, amp in state.items():
                for slots, sign in (((2*i, 2*j+1), 1), ((2*j, 2*i+1), -1)):
                    changed = list(occ)
                    factor = sign*amp
                    for slot in slots:
                        factor *= math.sqrt(changed[slot]+1)
                        changed[slot] += 1
                    key = tuple(changed)
                    out[key] = out.get(key, 0.)+factor
            state = out
    p, q, r = powers
    twice_spins = (p+r, p+q, q+r)
    tensor = np.zeros(tuple(n+1 for n in twice_spins))
    for occ, amp in state.items():
        tensor[occ[0], occ[2], occ[4]] = amp
    norm = np.linalg.norm(tensor)
    if norm == 0:
        raise ValueError('triangle polynomial vanishes')
    return tensor/norm, twice_spins


def singlet_metric(twice_spin):
    """Normalized invariant bra on two equal-spin copies, with fixed orientation."""
    if isinstance(twice_spin, bool) or not isinstance(twice_spin, int) or twice_spin < 0:
        raise ValueError('twice_spin must be a nonnegative integer')
    n = twice_spin
    metric = np.zeros((n+1, n+1))
    for a in range(n+1):
        metric[a, n-a] = (-1.)**(n-a)/math.sqrt(n+1)
    return metric


def contract_network(tensors, edges, edge_transports=None):
    """Sew pairs ((vertex,leg),(vertex,leg)); leave other legs open.

    Open output axes follow vertex order then local leg order. Edge ordering
    fixes the orientation of the invariant bra. No occupations are added.
    Optional spin-j representation matrices retain link holonomy dependence:
    each link contracts with metric @ D(g), rather than metric alone.
    """
    labels, next_label = {}, 0
    arguments = []
    for v, tensor in enumerate(tensors):
        tensor = np.asarray(tensor)
        local = []
        for leg in range(tensor.ndim):
            labels[v, leg] = next_label
            local.append(next_label)
            next_label += 1
        arguments.extend((tensor, local))
    edges = tuple(edges)
    if edge_transports is not None and len(edge_transports) != len(edges):
        raise ValueError('one transport matrix is required per sewn edge')
    sewn = set()
    for edge_index, (left, right) in enumerate(edges):
        left, right = tuple(left), tuple(right)
        if left == right or left in sewn or right in sewn:
            raise ValueError('each leg may be sewn only once')
        if left not in labels or right not in labels:
            raise ValueError('unknown leg')
        dl = np.asarray(tensors[left[0]]).shape[left[1]]
        dr = np.asarray(tensors[right[0]]).shape[right[1]]
        if dl != dr:
            raise ValueError('shared edge copies must have equal spin')
        kernel = singlet_metric(dl-1)
        if edge_transports is not None:
            transport = np.asarray(edge_transports[edge_index])
            if transport.shape != (dl, dl) or not np.all(np.isfinite(transport)):
                raise ValueError('transport dimensions must match the shared spin')
            kernel = kernel @ transport
        arguments.extend((kernel, [labels[left], labels[right]]))
        sewn.update((left, right))
    open_legs = tuple(leg for leg in labels if leg not in sewn)
    arguments.append([labels[leg] for leg in open_legs])
    return np.einsum(*arguments, optimize='greedy'), open_legs


def trivalent_graph_edges(vertex_edges):
    """Translate ordered geometric edge names at each triangle to sewn legs."""
    occurrences = {}
    for v, names in enumerate(vertex_edges):
        if len(names) != 3 or len(set(names)) != 3:
            raise ValueError('each triangle needs three distinct edge names')
        for leg, name in enumerate(names):
            occurrences.setdefault(name, []).append((v, leg))
    if any(len(legs) > 2 for legs in occurrences.values()):
        raise ValueError('an edge may have at most two face copies')
    return tuple(tuple(legs) for legs in occurrences.values() if len(legs) == 2)
