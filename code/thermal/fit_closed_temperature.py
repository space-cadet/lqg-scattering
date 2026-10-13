"""Fit closed-projection temperature curves and derive their area asymptote.

Consumes saved sector traces; keeps fitting artifacts next to their source data.
The six exact probability traces are independently derived as finite sums.
"""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np
import sympy as sp
from lqg_scattering.thermal_projection import evaluate_traces

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/thermal-closed-projection'


def exact_probability_traces():
    K,r,l=sp.symbols('K r l',integer=True,nonnegative=True)
    multiplicity=(K-r-l+1)**2
    f=r*(K-l+1)
    a=K+r-l
    polynomials=[]
    for expression in [f*f,a*a,1,f*a,f,a]:
        inner=sp.summation(sp.expand(multiplicity*expression),(l,0,K-r))
        polynomial=sp.expand(sp.summation(sp.expand(inner),(r,0,K)))
        polynomials.append(polynomial)
    return K,polynomials


def linear_fit(t,y):
    slope,intercept=np.polyfit(t,y,1)
    residual=slope*t+intercept-y
    return dict(slope=float(slope),intercept=float(intercept),
        r_squared=float(1-np.dot(residual,residual)/np.sum((y-y.mean())**2)),
        max_relative_residual=float(np.max(abs(residual)/y)),
        through_origin_slope=float(np.dot(t,y)/np.dot(t,t)))


def main():
    source=OUT/'singlet_sector_traces.npz'
    traces=np.load(source)['traces']
    temperatures=np.linspace(1,2,1001)
    areas=np.arange(len(traces))
    values=[]
    for t in temperatures:
        sectors=evaluate_traces(traces,1/t)
        probability=sectors[:,0].sum()
        values.append([np.dot(areas,sectors[:,0])/probability,sectors[:,1].sum()/probability])
    values=np.array(values)
    fits={key:linear_fit(temperatures,values[:,i]) for i,key in enumerate(['area','rs_volume'])}
    for i,key in enumerate(['area','rs_volume']):
        fits[key]['endpoint_local_slopes']=np.gradient(values[:,i],temperatures)[[0,-1]].tolist()
    K,polynomials=exact_probability_traces()
    maximum=0.0
    for k in range(len(traces)):
        for col,p in enumerate(polynomials):
            expected=float(p.subs(K,k)); actual=float(traces[k,0,col])
            error=abs(expected-actual)/max(1,abs(expected))
            maximum=max(maximum,error)
            assert error<2e-12
    leading_weights=[sp.Rational(1,4),sp.Rational(1,4),sp.Integer(1),-sp.Rational(1,2),sp.Integer(1),-sp.Integer(1)]
    probability_terms=[]; area_terms=[]
    # b=1/T*, eta~b, x~1. Each column contributes b^3 to p_closed.
    for polynomial,weight in zip(polynomials,leading_weights):
        degree=sp.degree(polynomial,K)
        term=weight*polynomial.coeff(K,degree)*sp.factorial(degree)/2**(degree+1)
        probability_terms.append(term)
        area_terms.append(term*sp.Rational(degree+1,2))
    coefficient=sp.simplify(sum(area_terms)/sum(probability_terms))
    assert coefficient==sp.Rational(57,14)
    report=dict(temperature_variable='T*=kBT/(hbar omega); b=beta hbar omega=1/T*',
        fit_interval=[1,2],uniform_fit_points=len(temperatures),fits=fits,
        exact_probability_trace_polynomials=[str(p) for p in polynomials],
        trace_sum='sum_{r=0}^K sum_{l=0}^{K-r} (K-r-l+1)^2 times [f^2,a^2,1,fa,f,a]; f=r(K-l+1), a=K+r-l',
        high_temperature_area_over_T_exact=str(coefficient),
        high_temperature_area_over_T=float(coefficient),
        high_temperature_projection_probability_over_b_cubed=str(sp.simplify(sum(probability_terms))),
        max_probability_trace_relative_error=maximum,
        source_data_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        source_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/'temperature_fit.json').write_text(json.dumps(report,indent=2)+'\n')
    with (OUT/'temperature_fit_grid.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['temperature_kBT_over_hbar_omega','mean_area','mean_rs_volume'])
        w.writerows((t,*v) for t,v in zip(temperatures,values))
    for key,fit in fits.items(): print(key,fit)
    print('Exact high-temperature area coefficient:',coefficient,'=',float(coefficient))
    print('PASS: finite-sum traces match all saved sectors; maximum relative error',maximum)


if __name__=='__main__':main()
