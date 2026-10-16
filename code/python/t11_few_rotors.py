"""Few-rotor transfer: exact planar pair and zero-total-J 3D controls."""
import csv,hashlib,json
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from lqg_scattering.classical_rotors import evolve_graph,initial_state

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/t11-few-rotors'


def save(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def energies(q,j,edges,coupling,inertia=1.):
    kinetic=np.sum(j*j,axis=-1)/(2*inertia);local=kinetic.copy();potential=np.zeros(len(q))
    for i,k in edges:
        bond=coupling*(1-np.sum(q[:,i]*q[:,k],axis=1));potential+=bond;local[:,i]+=bond/2;local[:,k]+=bond/2
    return kinetic,local,kinetic.sum(axis=1)+potential


def pair_bound(r):
    if r<4:return 1.
    if r==4:return .25  # supremum on separatrix, approached asymptotically
    return ((1-np.sqrt(1-4/r))/2)**2


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    protocol=dict(question='Explain parameter dependence of energy transfer with the fewest rotors.',
        pair='two planar rotors, one undirected bond; theta0=theta1=0; J0=sqrt(2*T0) ez, J1=0; nonzero total J',
        pair_ratios=[1.,3.9,4.1,10.,100.],fixed_T0_couplings=[.1,.3,1.,2.4,2.5,2.6,3.,10.,30.],
        fixed_T0=10.,dimensionless_duration=200.,sample_dtau=.02,
        planar_reduction='P=p1+p2, p=(p1-p2)/2, phi=theta1-theta2; H=P^2/(4I)+p^2/I+lambda(1-cos phi)',
        exact_transfer='r=T0/lambda. r<4: full transfer; r>4: max(K2/T0)=[(1-sqrt(1-4/r))/2]^2. r=4: supremum1/4, infinite approach time.',
        zero_J_controls=dict(graphs=['triangle','four_open','four_ring'],packet_energy=100.,couplings=[.1,.3,1.,3.,10.,30.,100.],seeds=[1701,1702,1703],
            initial='same generic 3D orientation labels and equal-opposite hot pair as main study',
            duration_tau=200.,warning='few-rotor energy exchange is not thermalization'),
        symmetric_control='three planar triangle rotors, identical initial orientations, momenta+p,-p,0; exact cancellation of torque on third',
        validation='independent planar DOP853; norm, tangency, total-J, energy; half-step controls; exact coupling/time scaling',
        inertia=1.,scope='mechanism benchmark; planar-pair formulas are not asserted for general 3D motion')
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    pairs=[];few=[];validation={};arrays={}
    cases=[(f'ratio_{r:g}',r,1.) for r in protocol['pair_ratios']]+[(f'lambda_{g:g}',10.,g) for g in protocol['fixed_T0_couplings']]
    for label,T,g in cases:
        q=np.tile([1.,0.,0.],(2,1));j=np.zeros((2,3));j[0,2]=np.sqrt(2*T)
        scale=np.sqrt(g);t,qq,jj,dt=evolve_graph(q,j,[(0,1)],g,dt=.003/max(np.sqrt(g),np.sqrt(2*T)),duration=200/scale,sample_interval=.02/scale)
        kinetic,local,e=energies(qq,jj,[(0,1)],g)
        ratio=T/g;bound=pair_bound(ratio)
        phi=np.unwrap(np.arctan2(qq[:,0,1],qq[:,0,0]))-np.unwrap(np.arctan2(qq[:,1,1],qq[:,1,0]))
        rel_momentum=(jj[:,0,2]-jj[:,1,2])/2
        pairs.append(dict(case=label,T0=T,coupling=g,ratio=ratio,regime='libration' if ratio<4 else ('rotation' if ratio>4 else 'separatrix'),
            exact_max_receiver_fraction=bound,sampled_max_receiver_fraction=float(kinetic[:,1].max()/T),
            mean_receiver_fraction=float(np.mean(kinetic[t*scale>=20,1])/T),relative_energy_drift=float(np.max(abs(e/e[0]-1))),
            dt=dt,physical_duration=t[-1]))
        # Independent scalar pendulum equations, comparison at short physical time.
        end=min(1.,t[-1]);P=np.sqrt(2*T)
        sol=solve_ivp(lambda time,y:[2*y[1],-g*np.sin(y[0])],[0,end],[0.,P/2],rtol=1e-12,atol=1e-13,method='DOP853')
        _,sq,sj,_=evolve_graph(q,j,[(0,1)],g,dt=min(dt,.0005),duration=end,sample_interval=end)
        ph=float(np.arctan2(sq[-1,0,1],sq[-1,0,0])-np.arctan2(sq[-1,1,1],sq[-1,1,0]))
        phase_error=abs(np.angle(np.exp(1j*(ph-sol.y[0,-1]))))
        momentum_error=abs((sj[-1,0,2]-sj[-1,1,2])/2-sol.y[1,-1])
        validation[label]=dict(phase_error=float(phase_error),momentum_error=float(momentum_error),
            energy=float(np.max(abs(e/e[0]-1))),total_J=float(np.max(abs(jj.sum(axis=1)-j.sum(axis=0)))))
        assert phase_error<2e-5 and momentum_error<2e-5,validation[label]
        assert validation[label]['energy']<5e-5
        assert validation[label]['total_J']<1e-9
        if abs(ratio-4)>.01:assert abs(bound-pairs[-1]['sampled_max_receiver_fraction'])<.005,(label,pairs[-1])
        np.savez_compressed(OUT/f'pair_{label}.npz',tau=t*scale,q=qq,J=jj,kinetic=kinetic,phi=phi,relative_momentum=rel_momentum)
    graphs={'triangle':(3,[(0,1),(1,2),(0,2)]),'four_open':(4,[(0,1),(1,2),(2,3)]),'four_ring':(4,[(0,1),(1,2),(2,3),(0,3)])}
    for graph,(n,edges) in graphs.items():
      for seed in [1701,1702,1703]:
       q,j=initial_state(n,100.,seed)
       for g in protocol['zero_J_controls']['couplings']:
        label=f'{graph}_S{seed}_lambda{g:g}';scale=np.sqrt(g)
        t,qq,jj,dt=evolve_graph(q,j,edges,g,dt=.003/max(10.,np.sqrt(g)),duration=200/scale,sample_interval=.02/scale)
        kinetic,local,e=energies(qq,jj,edges,g);mask=t*scale>=20
        cold=local[:,2:].sum(axis=1)/e[0];cold_kinetic=kinetic[:,2:].sum(axis=1)/100.
        row=dict(graph=graph,seed=seed,coupling=g,packet_energy=100.,ratio=100/g,total_energy=float(e[0]),
            maximum_cold_local_fraction=float(cold.max()),mean_cold_local_fraction=float(cold[mask].mean()),
            maximum_cold_kinetic_over_initial_packet=float(cold_kinetic.max()),mean_cold_kinetic_over_initial_packet=float(cold_kinetic[mask].mean()),
            initial_cold_local_fraction=float(cold[0]),physical_duration=float(t[-1]),dt=dt,
            relative_energy_drift=float(np.max(abs(e/e[0]-1))),max_total_J=float(np.linalg.norm(jj.sum(axis=1),axis=1).max()),
            norm_error=float(np.max(abs(np.sum(qq*qq,axis=2)-1))),tangency_error=float(np.max(abs(np.sum(qq*jj,axis=2)))))
        assert row['relative_energy_drift']<5e-5 and row['max_total_J']<1e-9 and row['norm_error']<1e-10 and row['tangency_error']<1e-10,row
        few.append(row)
        if seed==1701 and g in [1.,100.]:
            ft,fq,fj,fdt=evolve_graph(q,j,edges,g,dt=dt/2,duration=200/scale,sample_interval=.02/scale)
            fk,fl,fe=energies(fq,fj,edges,g)
            validation[label+'_refinement']=dict(coarse_dt=dt,fine_dt=fdt,
                coarse_drift=row['relative_energy_drift'],fine_drift=float(np.max(abs(fe/fe[0]-1))),
                coarse_cold_kinetic_mean=row['mean_cold_kinetic_over_initial_packet'],
                fine_cold_kinetic_mean=float(np.mean(fk[mask,2:].sum(axis=1))/100))
        np.savez_compressed(OUT/f'{label}.npz',tau=t*scale,kinetic=kinetic,local_energy=local,energy=e,initial_q=q,initial_J=j,final_q=qq[-1],final_J=jj[-1])
      print('Completed',graph,flush=True)
    # Special symmetric planar triangle: third rotor must stay stationary.
    q=np.tile([0.,0.,1.],(3,1));j=np.array([[10.,0,0],[-10.,0,0],[0.,0,0]])
    t,qq,jj,dt=evolve_graph(q,j,graphs['triangle'][1],1.,duration=200.,dt=.0003,sample_interval=.02)
    validation['symmetric_triangle']=dict(max_cold_kinetic=float(np.max(np.sum(jj[:,2]**2,axis=1)/2)),max_orientation_motion=float(np.max(abs(qq[:,2]-q[2]))))
    assert max(validation['symmetric_triangle'].values())<1e-10
    # Coupling equivalence under time/momentum rescaling, not an additional parameter.
    q,j=initial_state(4,100,1701);edges=graphs['four_open'][1]
    a,aq,aj,_=evolve_graph(q,j,edges,10.,dt=.0003,duration=20/np.sqrt(10),sample_interval=.02/np.sqrt(10))
    b,bq,bj,_=evolve_graph(q,j/np.sqrt(10),edges,1.,dt=.0003*np.sqrt(10),duration=20.,sample_interval=.02)
    validation['scaling']=dict(q_error=float(np.max(abs(aq-bq))),J_error=float(np.max(abs(aj/np.sqrt(10)-bj))))
    assert max(validation['scaling'].values())<1e-8
    save('pair-summary.csv',pairs);save('few-summary.csv',few)
    (OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    sources=[Path(__file__),ROOT/'code/classical/rotors.cpp',ROOT/'code/python/lqg_scattering/classical_rotors.py']
    (OUT/'provenance.json').write_text(json.dumps(dict(numpy=np.__version__,source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')
    print('Completed',len(pairs),'planar-pair and',len(few),'generic 3D runs; analytic, symmetry and scaling checks pass.')

if __name__=='__main__':main()
