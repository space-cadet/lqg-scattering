"""Schmidt spectrum of the separately closed four-face area-one reference.

All entropies are dimensionless (S/k_B), with natural logarithms. Multiplicity
counts individual eigenvalues, not a probability assigned to a whole group.
"""
from math import exp, log
import numpy as np
from scipy.special import xlogy
from .thermal_projection import coefficient_parameters, singlet_spectrum as raw_spectrum


def labels(cutoff):
    parts = []
    for k in range(cutoff + 1):
        r, l = np.indices((k + 1, k + 1))
        keep = r + l <= k
        r, l = r[keep], l[keep]
        parts.append(np.column_stack((np.full(len(r), k), r, l)))
    return np.concatenate(parts).astype(int)


def tail_bounds(b, cutoff):
    """Analytic infinite-tail bounds, evaluated in floating point.

    For k>=m=cutoff+1, |c|^2<=B_k=eta^8 exp[-2b(k-1)]L(k)^2,
    L(k)=u k(k+1)+2|v|k+w. d_k B_k has degree-eight positive
    polynomial prefactor, so its successive ratio is <=R below.
    Entropy uses monotonicity of -z log z below 1/e. These are
    truncation bounds, not interval certificates of floating-point error.
    """
    m = cutoff + 1
    eta,x,u,v,w = coefficient_parameters(b)
    log_b = 8*log(eta) - 2*b*(m-1) + 2*log(u*m*(m+1)+2*abs(v)*m+w)
    d = (m+1)*(m+2)**2*(m+3)/12
    ratio = exp(-2*b + 8*np.log1p(1/m))
    if ratio >= 1 or log_b >= -1 or log_b+log(d) >= -1:
        return None
    first = exp(log(d)+log_b)
    z = 1-ratio
    mass = first/z
    entropy = first*((-log_b)/z+2*b*ratio/z**2)
    area_entropy = first*((-log_b-log(d))/z+2*b*ratio/z**2)
    moment1 = first*(m/z+ratio/z**2)
    moment2 = first*(m*m/z+2*m*ratio/z**2+ratio*(1+ratio)/z**3)
    return dict(mass=mass, entropy=entropy, area_entropy=area_entropy,
                moment1=moment1, moment2=moment2, purity=exp(log_b)*mass)


def summarize(b, cutoff):
    indices = labels(cutoff)
    c, raw, d = raw_spectrum(b, indices)
    k = indices[:, 0]
    p = float(d @ raw)
    probabilities = raw/p
    masses = d*probabilities
    pk = np.bincount(k, weights=masses, minlength=cutoff+1)
    entropy = float(-d @ xlogy(probabilities, probabilities))
    area_entropy = float(-np.sum(xlogy(pk, pk)))
    purity = float(d @ (probabilities**2))
    mean = float(masses @ k)
    variance = float(masses @ ((k-mean)**2))
    # Joint singlet creation preserves A_L-A_R=0. Transfer F_L^dagger F_R
    # changes that difference and has exactly zero mean in this state family.
    destination = indices.copy()
    destination[:, 0] += 1
    destination[:, 1] += 1
    next_c = raw_spectrum(b, destination)[0]
    r, l = indices[:, 1], indices[:, 2]
    joint_creation = float(np.sum(d*c*next_c*(r+1)*(k-l+2))/p)
    tail = tail_bounds(b, cutoff)
    if tail is None:
        raise ValueError('cutoff too small for analytic tail envelope')
    pmax = p+tail['mass']
    q = float(-d @ xlogy(raw, raw))
    entropy_lo = q/pmax+log(p)
    entropy_hi = (q+tail['entropy'])/p+log(pmax)
    # Entropy of area masses has the same normalization correction.
    pk_raw = pk*p
    qa = float(-np.sum(xlogy(pk_raw, pk_raw)))
    area_lo = qa/pmax+log(p)
    area_hi = (qa+tail['area_entropy'])/p+log(pmax)
    raw_purity = float(d @ (raw**2))
    purity_lo = raw_purity/pmax**2
    purity_hi = (raw_purity+tail['purity'])/p**2
    row = dict(temperature=1/b, beta_hbar_omega=b, area_cutoff=cutoff,
        projection_probability=p, entropy_nats=max(0., entropy),
        entropy_lower_nats=max(0., entropy_lo), entropy_upper_nats=max(0., entropy_hi),
        area_entropy_nats=max(0., area_entropy),
        area_entropy_lower_nats=max(0.,area_lo), area_entropy_upper_nats=max(0.,area_hi),
        within_area_entropy_nats=max(0., entropy-area_entropy),
        within_area_entropy_lower_nats=max(0., entropy_lo-area_hi),
        within_area_entropy_upper_nats=max(0., entropy_hi-area_lo),
        renyi2_nats=max(0.,-log(purity)), purity=purity, mean_area=mean,
        renyi2_lower_nats=max(0.,-log(purity_hi)), renyi2_upper_nats=max(0.,-log(purity_lo)),
        purity_truncation_bound=max(abs(purity-purity_lo),abs(purity_hi-purity)),
        area_variance=variance, area_covariance_LR=variance,
        conditional_tail_mass_bound=tail['mass']/p,
        entropy_truncation_bound_nats=max(abs(entropy-entropy_lo),abs(entropy_hi-entropy)),
        mean_area_tail_error_bound=(tail['moment1']+mean*tail['mass'])/p,
        second_area_moment_tail_error_bound=(tail['moment2']+(variance+mean**2)*tail['mass'])/p)
    row['joint_F12_creation_real'] = joint_creation
    row['joint_F12_creation_tail_error_bound'] = (tail['moment2']+2*tail['moment1']+
        tail['mass']+abs(joint_creation)*tail['mass'])/p
    row['F12_transfer_real'] = 0.
    sectors = []
    for area, prob in enumerate(pk):
        mask = k == area
        cond = probabilities[mask]/prob if prob > 0 else np.zeros(mask.sum())
        sectors.append(dict(temperature=1/b, K=area, probability=float(prob),
            conditional_entropy_nats=float(-d[mask] @ xlogy(cond, cond)),
            weighted_entropy_nats=float(-prob*(d[mask] @ xlogy(cond, cond)))))
    return row, sectors, (indices, c, probabilities, d)
