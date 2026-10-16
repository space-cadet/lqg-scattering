"""Planar quantum rotors in an exact total-momentum sector; hbar=I=lambda=1 by default."""
from itertools import product
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import expm_multiply


def momentum_basis(n, cutoff, total=0):
    """Local |m_i| <= cutoff, with sum m_i = total, without a full tensor product."""
    if n < 2 or cutoff < 0 or int(cutoff) != cutoff:
        raise ValueError('need n>=2 and a nonnegative integer cutoff')
    rows = []
    for head in product(range(-cutoff, cutoff+1), repeat=n-1):
        last = total-sum(head)
        if abs(last) <= cutoff:
            rows.append((*head, last))
    return np.asarray(rows, dtype=int).reshape(-1, n)


def hamiltonian(basis, edges, epsilon=1., coupling=1.):
    """Dimensionless H: epsilon^2 sum m_i^2/2 + coupling sum(1-cos(theta_i-theta_j)).

    Evolution is i epsilon dpsi/dtau = H psi. Missing cutoff transitions are
    discarded (Galerkin projection), never wrapped around.
    """
    if epsilon <= 0 or coupling < 0:
        raise ValueError('epsilon must be positive and coupling nonnegative')
    n = basis.shape[1]
    bonds = [tuple(sorted(e)) for e in edges]
    if len(set(bonds)) != len(bonds) or any(i < 0 or j >= n or i == j for i,j in bonds):
        raise ValueError('invalid or duplicate edge')
    index = {tuple(row): k for k,row in enumerate(basis)}
    dim = len(basis)
    rows = list(range(dim)); cols = list(range(dim))
    data = list(epsilon**2*np.sum(basis**2, axis=1)/2+coupling*len(bonds))
    for col, state in enumerate(basis):
        for i,j in bonds:
            for step in (-1,1):
                other = state.copy(); other[i] += step; other[j] -= step
                row = index.get(tuple(other))
                if row is not None:
                    rows.append(row); cols.append(col); data.append(-coupling/2)
    return coo_matrix((data,(rows,cols)),shape=(dim,dim)).tocsr()


def momentum_state(basis, momenta):
    match = np.flatnonzero(np.all(basis == momenta, axis=1))
    if len(match) != 1:
        raise ValueError('initial momentum outside basis')
    psi = np.zeros(len(basis),complex); psi[match[0]] = 1
    return psi


def evolve_readouts(h, basis, psi, times, epsilon=1.):
    """Stream equal-time evolution to avoid storing all state vectors.

    Exact fixed total momentum makes each one-rotor reduced density matrix
    diagonal in m. Its entropy is consequently the momentum-marginal entropy.
    """
    times = np.asarray(times,float)
    if len(times)<2 or times[0]!=0 or not np.allclose(np.diff(times),times[1]):
        raise ValueError('times must be equally spaced, beginning at zero')
    cutoff = int(np.max(abs(basis)))
    kinetic = epsilon**2*basis**2/2
    generator = -1j*h/epsilon
    trace = generator.diagonal().sum()
    energy0 = float(np.vdot(psi,h@psi).real)
    out = []
    seed = psi.copy()
    boundary = np.any(abs(basis)==cutoff,axis=1)
    for k,t in enumerate(times):
        if k:
            psi = expm_multiply(generator*times[1],psi,traceA=trace*times[1])
        prob = abs(psi)**2
        entropy=[]
        for site in range(basis.shape[1]):
            marginal=np.bincount(basis[:,site]+cutoff,weights=prob,minlength=2*cutoff+1)
            positive=marginal[marginal>0]
            entropy.append(float(-np.sum(positive*np.log(positive))))
        out.append(dict(time=float(t),kinetic=(prob@kinetic).tolist(),
                        mean_momentum=(prob@(epsilon*basis)).tolist(),entropy=entropy,
                        return_probability=float(abs(np.vdot(seed,psi))**2),
                        norm_error=float(abs(prob.sum()-1)),
                        energy_error=float(abs(np.vdot(psi,h@psi).real-energy0)),
                        boundary_probability=float(prob[boundary].sum())))
    return out


def classical_ensemble(theta, momenta, edges, times, dt=.005):
    """Vectorized velocity Verlet; I=1. Equal times start at zero; lambda=1.

    Returns ensemble means and standard errors, plus conservation diagnostics.
    Initial angle samples can be reused for paired step-refinement controls.
    """
    theta=np.array(theta,float,copy=True); p=np.array(momenta,float,copy=True)
    def torque(q):
        force=np.zeros_like(q)
        for i,j in edges:
            s=np.sin(q[:,i]-q[:,j]); force[:,i]-=s; force[:,j]+=s
        return force
    def energy(q,p):
        return np.sum(p*p,axis=1)/2+sum(1-np.cos(q[:,i]-q[:,j]) for i,j in edges)
    e0=energy(theta,p); p0=p.sum(axis=1)
    stride=int(np.ceil((times[1]-times[0])/dt)); step=(times[1]-times[0])/stride
    out=[]
    for k,t in enumerate(times):
        if k:
            for _ in range(stride):
                p+=.5*step*torque(theta); theta+=step*p; p+=.5*step*torque(theta)
        kin=p*p/2
        out.append(dict(time=float(t),kinetic=kin.mean(axis=0).tolist(),
                        kinetic_standard_error=(kin.std(axis=0,ddof=1)/np.sqrt(len(p))).tolist(),
                        max_energy_error=float(np.max(abs(energy(theta,p)-e0))),
                        max_total_momentum_error=float(np.max(abs(p.sum(axis=1)-p0)))))
    return out
