"""Separately closed four-face J=1 thermal projection and volume trace data.

The reference is F12^dagger|0>/sqrt(2) in each conjugate-paired copy.
Within a singlet recoupling block the coefficient matrix is diagonal:
C=eta^4 exp[-b(K-1)] [u F12^dagger F12 + v(n1+n2) + w].
"""
from math import sqrt
import numpy as np
from scipy.linalg import eigh_tridiagonal
from .conventions import GAMMA
from .singlets import ZERO_FACTOR


def singlet_volume_diagonals(twice_spins):
    """Diagonal RS moments and kernel weights in the ((12)k,(34)k) singlet basis.

    Uses the tridiagonal triple grasp, independently checked against saved
    oscillator/CG matrices by the thermal projection driver. Return k labels,
    |q012| root diagonal, |q012| diagonal, and its kernel diagonal.
    """
    j1,j2,j3,j4=np.array(twice_spins,dtype=float)/2
    lower=max(abs(j1-j2),abs(j3-j4))
    upper=min(j1+j2,j3+j4)
    k=np.arange(lower,upper+0.1)
    if len(k)==0: return k,k,k,k
    links=k[1:]
    off=np.sqrt(np.maximum(0,(((j1+j2+1)**2-links**2)*(links**2-(j1-j2)**2)
                            *((j3+j4+1)**2-links**2)*(links**2-(j3-j4)**2))))/(4*np.sqrt(4*links**2-1))
    if len(k)==1:
        values=np.zeros(1); vectors=np.ones((1,1))
    else:
        values,vectors=eigh_tridiagonal(np.zeros(len(k)),off)
    cutoff=ZERO_FACTOR*max(1,float(np.max(abs(values))))
    absolute=np.where(abs(values)<=cutoff,0,abs(values))
    weights=vectors**2
    return k,weights@np.sqrt(absolute),weights@absolute,weights@(absolute==0)


def monomials(f,a):
    return np.column_stack((f*f,np.full_like(f,a*a),np.ones_like(f),f*a,f,np.full_like(f,a)))


def sector_trace_data(area):
    """Six polynomial traces for probability, RS moments, kernel and active faces.

    Enumerate pair-internal permutations and pair exchange by multiplicities;
    all four labelled-face assignments are retained. The phase-equivalent
    real-symmetric grasp has the same spectral-function diagonal.
    """
    total=2*area
    trace=np.zeros((5,6))
    dimension=blocks=0
    volume_factor=4*GAMMA**1.5
    for a in range(total+1):
        for j1 in range(a//2+1):
            j2=a-j1
            rest=total-a
            for j3 in range(rest//2+1):
                j4=rest-j3
                if (j1,j2)>(j3,j4): continue
                if max(j1,j2,j3,j4)>area: continue
                k,root,absolute,kernel=singlet_volume_diagonals((j1,j2,j3,j4))
                if not len(k): continue
                multiplicity=(1 if j1==j2 else 2)*(1 if j3==j4 else 2)
                sums=[a] if (j1,j2)==(j3,j4) else [a,rest]
                observables=np.vstack((np.ones(len(k)),volume_factor*root,
                                       volume_factor**2*absolute,kernel,
                                       np.full(len(k),float(min(j1,j2,j3,j4)>0))))
                for pair_sum in sums:
                    f=(pair_sum/2-k)*(pair_sum/2+k+1)
                    trace += multiplicity*(observables@monomials(f,pair_sum))
                    dimension += multiplicity*len(k)
                blocks+=1
    expected=(area+1)*(area+2)**2*(area+3)//12
    assert dimension==expected,(area,dimension,expected)
    return trace,dimension,blocks


def coefficient_weights(b):
    x=np.exp(-b); eta=-np.expm1(-b)
    u,v,w=eta**2/2,-eta*x/2,x*x
    return np.array((u*u,v*v,w*w,2*u*v,2*u*w,2*v*w))


def evaluate_traces(traces,b):
    areas=np.arange(len(traces))
    values=traces@coefficient_weights(b)
    return (-np.expm1(-b))**8*np.exp(-2*b*(areas-1))[:,None]*values


VOLUME_NORM_COEFFICIENT=4*GAMMA**1.5*sqrt(2/9)
# Each q012 is a sum of six spin-component products: ||q||<=6 j1*j2*j3.
# AM-GM then gives ||V_RS||<=VOLUME_NORM_COEFFICIENT * area**(3/2).
