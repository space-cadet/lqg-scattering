"""Threshold-explicit crossover brackets, scale tests, and independent audits."""
import csv,json
import numpy as np
from t11_rotor_coupling_scan import OUT,RATIOS,table


def main():
    (OUT/'analysis-protocol.json').write_text(json.dumps(dict(
        predefined_primary='per-seed significant>=10%, suppressed<=1% mean cold kinetic energy / initial packet; grid brackets only',
        secondary_added_after_inspection='half-response location, relative to each seed/N mean transfer at r2,4,6,8,10; separates main drop from weak tails',
        windows=[1000,2000],sensitivity_thresholds=[.005,.01,.02,.05,.1],
        interpolation='none; no fitted critical exponent or assumed phase transition',
        coupling_scale='E_packet bracket=lambda*r bracket for dimensionless time and matched initial dimensionless data',
        control_comparison='direct lambda5,10 runs at fixed packet100 versus normalized r20,10; compare early trajectories and late means separately'),indent=2)+'\n')
    rows=list(csv.DictReader((OUT/'summary.csv').open()));groups=[];brackets=[];cuts=[];comparisons=[];audit={};count=0
    scan=[r for r in rows if r['kind']=='scan']
    for end in [1000.,2000.]:
      for n in [8,16,32,64]:
       for ratio in RATIOS:
        a=[float(r['mean_cold_kinetic_fraction']) for r in scan if int(r['N'])==n and float(r['ratio'])==ratio and float(r['window_end'])==end]
        groups.append(dict(N=n,ratio=ratio,window_end=end,mean=float(np.mean(a)),minimum=min(a),maximum=max(a)))
       for seed in [1701,1702,1703]:
        s={float(r['ratio']):float(r['mean_cold_kinetic_fraction']) for r in scan if int(r['N'])==n and int(r['seed'])==seed and float(r['window_end'])==end}
        significant=max((r for r in RATIOS if s[r]>=.1),default=None)
        suppressed=next((r for r in RATIOS if significant is not None and r>significant and all(s[k]<=.01 for k in RATIOS if k>=r)),None)
        baseline=np.mean([s[r] for r in [2.,4.,6.,8.,10.]])
        half_above=max((r for r in RATIOS if s[r]>=baseline/2),default=None)
        half_below=next((r for r in RATIOS if half_above is not None and r>half_above and s[r]<baseline/2),None)
        brackets.append(dict(N=n,seed=seed,window_end=end,last_significant_ratio=significant,first_persistent_suppressed_ratio=suppressed,
            baseline_cold_fraction=baseline,half_response_lower=half_above,half_response_upper=half_below))
        for threshold in [.005,.01,.02,.05,.1]:
            last_above=max((r for r in RATIOS if s[r]>threshold),default=None)
            first_below=next((r for r in RATIOS if last_above is not None and r>last_above and all(s[k]<=threshold for k in RATIOS if k>=r)),None)
            cuts.append(dict(N=n,seed=seed,window_end=end,transfer_threshold=threshold,last_above=last_above,first_persistently_below=first_below))
    for n in [8,16,32,64]:
      for g in [5.,10.]:
       r=100/g
       direct=next(x for x in rows if x['kind']=='physical_coupling' and int(x['N'])==n and float(x['coupling'])==g and float(x['window_end'])==2000)
       base=next(x for x in scan if int(x['N'])==n and int(x['seed'])==1701 and float(x['ratio'])==r and float(x['window_end'])==2000)
       a=np.load(OUT/f'{direct["run"]}.npz');b=np.load(OUT/f'{base["run"]}.npz');early=a['tau']<=2
       x=a['readouts'][:,4]/100;y=b['readouts'][:,4]/r
       comparisons.append(dict(N=n,coupling=g,packet_energy=100,ratio=r,
            direct_mean=float(direct['mean_cold_kinetic_fraction']),normalized_mean=float(base['mean_cold_kinetic_fraction']),
            early_max_transfer_error=float(np.max(abs(x[early]-y[early]))),late_mean_error=abs(float(direct['mean_cold_kinetic_fraction'])-float(base['mean_cold_kinetic_fraction']))))
    refinements=[]
    for row in rows:
      if row['kind']=='half_step' and float(row['window_end'])==2000:
       b=next(x for x in scan if x['N']==row['N'] and x['ratio']==row['ratio'] and x['seed']==row['seed'] and x['window_end']==row['window_end'])
       refinements.append(dict(N=row['N'],ratio=row['ratio'],coarse_dt=b['dt'],fine_dt=row['dt'],coarse_transfer=b['mean_cold_kinetic_fraction'],fine_transfer=row['mean_cold_kinetic_fraction'],difference=abs(float(b['mean_cold_kinetic_fraction'])-float(row['mean_cold_kinetic_fraction'])),energy_drift_ratio=float(b['relative_energy_drift'])/float(row['relative_energy_drift'])))
    physical_rows=[]
    for n in [8,64]:
      for g in [1.,5.,10.]:
        candidates=[x for x in rows if int(x['N'])==n and x['seed']=='1701' and
            ((g==1 and x['kind']=='scan' and float(x['ratio'])==100) or
             (g!=1 and x['kind']=='fixed_physical' and float(x['coupling'])==g))]
        row=max(candidates,key=lambda x:float(x['window_end']))
        ar=np.load(OUT/f'{row["run"]}.npz');physical_t=ar['tau']/np.sqrt(g)
        mask=(physical_t>=200)&(physical_t<=2000)
        physical_rows.append(dict(N=n,coupling=g,packet_energy=100,seed=1701,
            window_start=200,window_end_actual=float(physical_t[mask][-1]),
            mean_cold_kinetic_fraction=float(np.mean(ar['readouts'][mask,4])/100)))
    table('fixed-physical-summary.csv',physical_rows)
    def check(name,x,tol):
        nonlocal count
        value=float(np.max(abs(x)));audit[name]=max(audit.get(name,0),value);count+=np.size(x);assert value<=tol,(name,value,tol)
    for path in OUT.glob('*.npz'):
        ar=np.load(path);d=ar['readouts'];n=(d.shape[1]-8)//2
        check('local_energy_sum',d[:,8:8+n].sum(axis=1)-d[:,0],2e-9)
        check('kinetic_sum',d[:,8+n:].sum(axis=1)-d[:,1]*d[:,0],2e-9)
        check('cold_kinetic_sum',d[:,8+n+2:].sum(axis=1)-d[:,4],2e-9)
        check('nonnegative_kinetic',np.minimum(d[:,8+n:],0),1e-14)
        # Independent endpoint Hamiltonian including explicit physical coupling.
        g=float(path.stem.split('_L')[-1])
        for prefix,idx in [('initial',0),('final',-1)]:
            q=ar[prefix+'_q'];j=ar[prefix+'_J']
            energy=np.sum(j*j)/2+g*np.sum(1-np.sum(q*np.roll(q,-1,axis=0),axis=1))
            check('endpoint_energy',energy-d[idx,0],2e-9)
            check('endpoint_kinetic',np.sum(j*j,axis=1)/2-d[idx,8+n:],2e-9)
            check('unit_orientation',np.sum(q*q,axis=1)-1,1e-9)
            check('tangency',np.sum(q*j,axis=1),1e-9)
            check('total_J',j.sum(axis=0),1e-8)
    table('grouped-scan.csv',groups);table('crossover-brackets.csv',brackets);table('threshold-sensitivity.csv',cuts)
    table('coupling-comparison.csv',comparisons);table('step-refinement.csv',refinements)
    (OUT/'independent-validation.json').write_text(json.dumps(dict(comparisons=int(count),maximum_residuals=audit),indent=2)+'\n')
    print('Saved explicit threshold brackets and coupling controls; audited',count,'scalar quantities.')

if __name__=='__main__':main()
