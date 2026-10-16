"""Independent saved-observable and free-FL analytic audit; no trajectory rerun."""
import csv,hashlib,json
from pathlib import Path
import numpy as np
from lqg_scattering.intertwiners import evolve_fl_spinors,fl_face_statistics
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/t11-geometric-redistribution'

def main():
    count=0;maximum=0.;minimum_positive_volume=float('inf');free_count=0
    def check(x,tol=2e-8):
        nonlocal count,maximum
        residual=abs(float(x));count+=1;maximum=max(maximum,residual)
        assert residual<tol,(count,residual)
    inputs=json.loads((OUT/'inputs.json').read_text())
    with (OUT/'dynamics.csv').open() as f:
        for row in csv.DictReader(f):
            l=int(row['L']);time=float(row['time']);alpha=float(row['alpha'])
            p=np.array([float(row[f'p_active_{n}']) for n in range(9)])
            area=np.array([float(row[f'area_{i}']) for i in range(l)])
            casimir=np.array([float(row[f'casimir_{i}']) for i in range(l)])
            local=np.array([float(row[f'local_energy_{i}']) for i in range(l)])
            check(p.sum()-1);check(min(0.,p.min()));check(p[l+1:].sum());check(p[:2].sum())
            check(area.sum()-4);check(min(0.,area.min()));check(min(0.,casimir.min()))
            check(p@np.arange(9)-float(row['expected_active']))
            check(area[4:].sum()/4-float(row['receiver_area_fraction']))
            check(local.sum()-float(row['energy']));check(local[4:].sum()-float(row['receiver_local_energy']))
            check(row['norm_error']);check(row['energy_error'])
            if time==0 and row['preparation'].endswith('sharp'):
                check(p[4]-1);check(np.max(abs(area-np.r_[np.ones(4),np.zeros(l-4)])))
                check(np.max(abs(casimir-np.r_[np.full(4,2),np.zeros(l-4)])))
                for i in range(l):check(float(row[f'entropy_{i}'])-(np.log(3) if i<4 else 0))
            if alpha!=0 or row['preparation']!='regular_FL':continue
            entry=inputs[f'L{l}_regular_FL'];z=np.array(entry['spinors_real'])+1j*np.array(entry['spinors_imag'])
            one=np.zeros((l,l));edges=[(i,(i+1)%l) for i in range(l)] if row['graph']=='ring' else [(i,j) for i in range(l) for j in range(i+1,l)]
            weight=.5 if row['graph']=='ring' else 1/(l-1)
            for i,j in edges:one[i,j]=one[j,i]=-weight
            a=fl_face_statistics(4,evolve_fl_spinors(z,one,time))
            check(np.max(abs(a['mean_face_area']-area)));check(a['area_concentration']-float(row['concentration']))
            check(a['expected_active_faces']-float(row['expected_active']));free_count+=1
    geometry=json.loads((OUT/'geometry.json').read_text())
    for row in geometry:
        for key in ['zero_volume_probability','probability_at_least5']:
            check(min(0.,row[key]));check(max(0.,row[key]-1))
        check(min(0.,row['volume_mean']));check(min(0.,row['volume_sd']))
        conditional=row['conditional_volume_at_least5']
        if conditional is not None:
            check(min(0.,conditional));check(max(0.,row['probability_at_least5']*conditional-row['volume_mean']))
            minimum_positive_volume=min(minimum_positive_volume,conditional)
        for pair in row['pairs']:
            p=pair['presence_probability'];check(min(0.,p));check(max(0.,p-1))
            if pair['conditional_angle_mean'] is not None:
                check(max(0.,abs(pair['conditional_angle_mean'])-1));check(min(0.,pair['conditional_angle_sd']))
    provenance=json.loads((OUT/'provenance.json').read_text())
    for name,digest in provenance['source_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    result=dict(comparisons=count,free_FL_frames=free_count,maximum_residual=maximum,
                minimum_sampled_conditional_volume_at_least5=minimum_positive_volume,tolerance=2e-8)
    (OUT/'independent-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)

if __name__=='__main__':main()
