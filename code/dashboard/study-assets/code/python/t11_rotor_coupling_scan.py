"""Larger-ring transfer crossover at variable energy and explicit coupling."""
import csv,hashlib,json,time
from pathlib import Path
import numpy as np
from lqg_scattering.classical_rotors import initial_state,evolve_transfer

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/t11-rotor-coupling'
RATIOS=[2.,4.,6.,8.,10.,12.,14.,16.,18.,20.,25.,30.,50.,100.]


def table(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def run(n,r,seed,coupling=1.,duration=2000.,refinement=1.,kind='scan'):
    packet=r*coupling;q,j=initial_state(n,packet,seed)
    scale=np.sqrt(coupling);step=.01/(scale*np.sqrt(max(1,r/10))*refinement)
    t,d,qf,jf,dt=evolve_transfer(q,j,coupling=coupling,dt=step,duration=duration/scale,sample_interval=.5/scale)
    tau=t*scale;cold=d[:,4]/packet
    drift=float(np.max(abs(d[:,0]/d[0,0]-1)))
    assert drift<1e-4,(n,r,seed,coupling,drift)
    assert d[:,5:8].max()<1e-8
    assert np.max(abs(d[:,8+n:].sum(axis=1)-d[:,1]*d[:,0]))<1e-9
    label=f'{kind}_N{n}_R{r:g}_S{seed}_L{coupling:g}'
    rows=[]
    for end in sorted(set([x for x in [1000.,2000.,10000.] if x<=duration]+[float(duration)])):
        mask=(tau>=200)&(tau<=end)
        rows.append(dict(run=label,kind=kind,N=n,ratio=r,seed=seed,coupling=coupling,packet_energy=packet,
            actual_total_energy=float(d[0,0]),window_end=end,mean_cold_kinetic_fraction=float(cold[mask].mean()),
            max_cold_kinetic_fraction=float(cold[mask].max()),mean_hot_local_fraction=float(d[mask,2].mean()),
            relative_energy_drift=drift,dt=dt,physical_duration=float(t[-1]),
            max_total_J=float(d[:,5].max()),norm_error=float(d[:,6].max()),tangency_error=float(d[:,7].max())))
    # Keep compact, reproducible kinetic and local-energy histories; q/J endpoints.
    np.savez_compressed(OUT/f'{label}.npz',tau=tau,readouts=d,initial_q=q,initial_J=j,final_q=qf,final_J=jf,dt=dt)
    return rows


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    protocol=dict(task='T11',question='How does the finite-time energy-transfer crossover scale with coupling in larger rings?',
        counts=[8,16,32,64],ratios=RATIOS,seeds=[1701,1702,1703],inertia=1.,
        initial='same near-aligned 3D labels and opposite tangent hot-pair momenta; all others initially stationary',
        primary_parameter='r=initial packet kinetic energy/lambda; additional initial potential recorded separately',
        duration_tau=2000.,sample_dtau=.5,late_window_start=200.,
        transfer='mean kinetic energy outside rotors0,1 divided by initial packet kinetic energy; does not count potential energy as transfer',
        thresholds=dict(significant=.1,suppressed=.01,sensitivity=[.005,.01,.02,.05,.1]),
        cutoff='per-seed bracket: largest r with >=10% transfer, and smallest larger r with <=1% transfer and all tested larger ratios also <=1%; no forced sharp transition',
        explicit_coupling_controls=dict(counts=[8,16,32,64],fixed_packet_energy=100.,couplings=[1.,5.,10.],seed=1701,
            comparison='r=100,20,10 respectively; lambda=1 control reuses production run; other couplings directly integrated'),
        scaling='at fixed dimensionless initial labels, r and tau=t*sqrt(lambda/I), E_cut=lambda*r_cut exactly by rescaling; test collapse rather than fit independent scaling exponent',
        refinement='N8,64; seed1701; r12,20 at half-step; full tau2000',
        longer_time='predefined ratios12,16; N8,64; seed1701; tau10000',
        limitations=['finite-time crossover only','three related orientation seeds','special opposite-momentum hot pair','no equilibrium or quantum claim'])
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    rows=[];started=time.monotonic()
    for n in protocol['counts']:
      for r in RATIOS:
       for seed in protocol['seeds']:
        rows.extend(run(n,r,seed));table('summary.csv',rows)
       print(f'N{n} r={r:g} complete, elapsed={time.monotonic()-started:.0f}s',flush=True)
    for n in protocol['counts']:
      for coupling in [5.,10.]:
        rows.extend(run(n,100/coupling,1701,coupling=coupling,kind='physical_coupling'));table('summary.csv',rows)
    for n in [8,64]:
      for r in [12.,20.]:
        rows.extend(run(n,r,1701,refinement=2.,kind='half_step'));table('summary.csv',rows)
      for r in [12.,16.]:
        rows.extend(run(n,r,1701,duration=10000.,kind='long_time'));table('summary.csv',rows)
      print(f'N{n} controls complete, elapsed={time.monotonic()-started:.0f}s',flush=True)
    sources=[Path(__file__),ROOT/'code/classical/rotors.cpp',ROOT/'code/python/lqg_scattering/classical_rotors.py']
    (OUT/'provenance.json').write_text(json.dumps(dict(numpy=np.__version__,elapsed_seconds=time.monotonic()-started,source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')
    print('Complete',len(rows),'window summaries.')

if __name__=='__main__':main()
