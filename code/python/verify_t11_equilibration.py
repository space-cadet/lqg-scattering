"""Independent free-FL readout checks and saved trajectory probability audits."""
import csv
import json
from pathlib import Path
import numpy as np
from lqg_scattering.intertwiners import regular_tetrahedron_spinors, evolve_fl_spinors, fl_face_statistics

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/t11-equilibration'


def main():
    maximum=0.;count=0;free_checks=0
    def check(residual):
        nonlocal maximum,count
        maximum=max(maximum,float(abs(residual)));count+=1
        assert abs(residual)<2e-9,(count,residual)
    with (OUT/'dynamics.csv').open() as f:
        for r in csv.DictReader(f):
            l,k=int(r['L']),int(r['K']);time=float(r['time'])
            p=np.array([float(r[f'p_active_{m}']) for m in range(8)])
            check(p.sum()-1)
            check(min(0.,p.min()))
            check(p[min(l,2*k)+1:].sum())
            if float(r['U'])!=0 or abs(time/12.5-round(time/12.5))>1e-9: continue
            z=np.zeros((l,2),complex);z[:4]=regular_tetrahedron_spinors()
            if r['phase']=='phase_shifted':z[:4]*=np.exp(1j*np.arange(4)*np.pi/2)[:,None]
            h=-(np.ones((l,l))-np.eye(l))/(l-1)
            stats=fl_face_statistics(k,evolve_fl_spinors(z,h,time))
            check(float(r['concentration'])-stats['area_concentration'])
            check(float(r['extra_area_fraction'])-sum(stats['mean_face_area'][4:])/k)
            check(p@np.arange(8)-stats['expected_active_faces'])
            free_checks+=3
    result=dict(comparisons=count,free_analytic_comparisons=free_checks,maximum_residual=maximum,tolerance=2e-9)
    (OUT/'independent-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result)


if __name__=='__main__':main()
