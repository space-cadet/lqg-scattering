"""Equilibrium-calibrated analysis and long-time step-refinement controls."""
import csv,json
from pathlib import Path
import numpy as np
from scipy.stats import ks_2samp
from lqg_scattering.classical_rotors import evolve
from t11_classical_rotors import OUT,write_csv


def observables(data,n):
    return np.column_stack([data[:,2],data[:,1],1/(n*data[:,3])])


def main():
    (OUT/'analysis-protocol.json').write_text(json.dumps(dict(
        reason='Equilibrium has finite instantaneous fluctuations; fixed tolerance alone is insufficient.',
        frozen_before_analysis=True,
        equilibrium_region='90th percentile of max absolute deviations of hot fraction, kinetic fraction and participation from MC means',
        expected_reference_residence=.9,
        equilibrium_distribution_comparison='two-sample KS distance, statistic only; no IID p values for correlated samples',
        refinement='seed1701, N=8,32,64, ratios10 and100, both scalings; N8 duplicate omitted; same duration2000 with dt/2',
        ensemble='conditional microcanonical at same total energy and total angular momentum zero',
        notes='region residence is one diagnostic and cannot establish ergodicity'),indent=2)+'\n')
    old=list(csv.DictReader((OUT/'summary.csv').open()));rows=[];refined=[]
    for r in old:
        if float(r['window_end'])!=2000:continue
        label=r['run'];n=int(r['N']);ar=np.load(OUT/f'{label}.npz')
        data=ar['readouts'];t=ar['times'];mask=t>=200
        obs=observables(data,n);mc=ar['microcanonical_readouts'].reshape(-1,n+8);mobs=observables(mc,n)
        target=mobs.mean(axis=0);eqdist=np.max(abs(mobs-target),axis=1);threshold=float(np.quantile(eqdist,.9))
        dist=np.max(abs(obs-target),axis=1)
        row=dict(r)
        row.update(equilibrium_region90_radius=threshold,residence_region90=float(np.mean(dist[mask]<=threshold)),
            equilibrium_residence90=float(np.mean(eqdist<=threshold)),
            hot_mean_in_equilibrium_SD=float((obs[mask,0].mean()-2/n)/mobs[:,0].std()),
            kinetic_KS=float(ks_2samp(obs[mask,1],mobs[:,1]).statistic),
            hot_fraction_KS=float(ks_2samp(obs[mask,0],mobs[:,0]).statistic),
            participation_KS=float(ks_2samp(obs[mask,2],mobs[:,2]).statistic),
            early_region90=float(np.mean(dist[(t>=200)&(t<=1000)]<=threshold)))
        rows.append(row)
        if int(r['seed'])==1701 and n in [8,32,64] and float(r['ratio']) in [10,100] and not(n==8 and r['scaling']=='fixed_density'):
            tt,dd,qq,jj,dt=evolve(ar['initial_q'],ar['initial_J'],float(ar['dt'])/2,2000)
            oo=observables(dd,n);mm=tt>=200
            fine=dict(run=label,coarse_dt=float(ar['dt']),fine_dt=dt,
                coarse_relative_energy_drift=float(np.max(abs(data[:,0]/data[0,0]-1))),
                fine_relative_energy_drift=float(np.max(abs(dd[:,0]/dd[0,0]-1))),
                coarse_hot_mean=float(obs[mask,0].mean()),fine_hot_mean=float(oo[mm,0].mean()),
                coarse_kinetic_mean=float(obs[mask,1].mean()),fine_kinetic_mean=float(oo[mm,1].mean()),
                coarse_participation_mean=float(obs[mask,2].mean()),fine_participation_mean=float(oo[mm,2].mean()),
                coarse_residence90=row['residence_region90'],fine_residence90=float(np.mean(np.max(abs(oo[mm]-target),axis=1)<=threshold)))
            refined.append(fine)
            np.savez_compressed(OUT/f'{label}_refined.npz',times=tt,readouts=dd,dt=dt)
            print(label,'hot coarse/fine',fine['coarse_hot_mean'],fine['fine_hot_mean'],flush=True)
        write_csv(OUT/'equilibrium-analysis.csv',rows);write_csv(OUT/'step-refinement.csv',refined)
    groups=[]
    for n in [8,16,32,64]:
      for ratio in [1.,10.,100.]:
       for scaling in ['fixed_packet','fixed_density']:
        selected=[r for r in rows if int(r['N'])==n and float(r['ratio'])==ratio and r['scaling']==scaling]
        row=dict(N=n,ratio=ratio,scaling=scaling,seeds=len(selected),equilibrium_hot=2/n)
        for name in ['mean_hot_fraction','mean_participation_fraction','reference_participation_fraction','residence_region90','kinetic_KS','hot_fraction_KS','participation_KS']:
            a=np.array([float(r[name]) for r in selected]);row[name+'_mean']=float(a.mean());row[name+'_min']=float(a.min());row[name+'_max']=float(a.max())
        groups.append(row)
    write_csv(OUT/'grouped-summary.csv',groups)

if __name__=='__main__':main()
