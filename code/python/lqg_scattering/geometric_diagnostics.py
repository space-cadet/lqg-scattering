"""Area-sector and angular readouts for exact singlet density matrices.

Zero entries in angular operators on missing-face sectors are placeholders:
angular readouts must be conditioned on nonzero face spins.
"""
import itertools
import numpy as np


def mean(rho, operator):
    return float(np.real(np.einsum('ij,ji->', rho, operator)))


def condition(rho, mask, min_probability=1e-14):
    """Project both sides without dephasing within the selected subspace."""
    mask = np.asarray(mask, dtype=bool)
    probability = float(np.real(np.diag(rho)[mask].sum()))
    if probability <= min_probability:
        return probability, None
    return probability, rho * mask[:, None] * mask[None, :] / probability


def moments(rho, operators):
    """Means and symmetrized covariance of possibly noncommuting operators."""
    means = np.asarray([mean(rho, op) for op in operators])
    covariance = np.empty((len(operators), len(operators)))
    for i, left in enumerate(operators):
        for j, right in enumerate(operators[:i+1]):
            value = mean(rho, (left@right+right@left)/2)-means[i]*means[j]
            covariance[i,j] = covariance[j,i] = value
    return means, covariance


def angular_operators(numbers, pair_dots):
    """Normalize separately in each area assignment; never divide means."""
    spins = np.asarray(numbers, dtype=float)/2
    casimir = spins*(spins+1)
    pairs = tuple(itertools.combinations(range(spins.shape[1]), 2))
    operators = []
    for i,j in pairs:
        denominator = np.sqrt(casimir[:,i]*casimir[:,j])
        inverse = np.divide(1., denominator, out=np.zeros_like(denominator),
                            where=denominator>0)
        operator = np.asarray(pair_dots[i,j])*inverse[None,:]
        if np.max(abs(operator-operator.conj().T))>2e-10:
            raise ValueError('pair dot does not preserve local area sectors')
        operators.append(operator)
    return pairs, operators


def summarize(rho, numbers, pair_dots, volume, q):
    """Read full area/volume moments and four-active-face angular moments."""
    trace = np.trace(rho)
    if abs(trace-1)>2e-10 or np.max(abs(rho-rho.conj().T))>2e-10:
        raise ValueError('expected a normalized Hermitian density matrix')
    numbers = np.asarray(numbers)
    area_operators = [np.diag(numbers[:,i]/2) for i in range(numbers.shape[1])]
    areas, area_cov = moments(rho, area_operators)
    pairs, angles = angular_operators(numbers,pair_dots)
    p4, conditional = condition(rho,np.all(numbers>0,axis=1))
    volume_mean = mean(rho,volume)
    result = dict(area_means=areas.tolist(),area_covariance=area_cov.tolist(),
        four_face_probability=p4,volume_mean=volume_mean,
        volume_variance=max(0.,mean(rho,volume@volume)-volume_mean**2),
        signed_q_mean=mean(rho,q),q_second_moment=mean(rho,q@q),
        pair_dot_means=[mean(rho,pair_dots[p]) for p in pairs],
        active_face_probabilities={str(n):float(np.real(np.diag(rho)[np.count_nonzero(numbers,axis=1)==n].sum()))
                                   for n in range(1,numbers.shape[1]+1)})
    if conditional is not None:
        m,c = moments(conditional,angles)
        result.update(conditional_angle_means=m.tolist(),conditional_angle_covariance=c.tolist(),
                      conditional_volume_mean=mean(conditional,volume))
    return result
