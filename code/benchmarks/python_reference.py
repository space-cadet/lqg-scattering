"""Matched T11 reference and timing harness; no plotting or production-result edits."""
import argparse, itertools, json, os, platform, resource, statistics, sys, time
from pathlib import Path
import numpy as np
import scipy
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'python'))
from hamiltonian_studies import build_fixed_k, GRAPH_EDGES, BETA_VALUES, thermal_weights
OUT=Path(__file__).resolve().parents[2]/'results/python-vs-ts'
def timed(fn, repeats):
    fn()  # warm caches and numerical libraries
    samples=[]
    for _ in range(repeats):
        start=time.perf_counter(); value=fn(); samples.append((time.perf_counter()-start)*1000)
    return value, {'median_ms':statistics.median(samples),'samples_ms':samples}
def pack(a):
    a=np.asarray(a); return {'re':a.real.tolist(),'im':a.imag.tolist()}
def calculate(h,v,active):
    e,u=np.linalg.eigh(h); ve,vu=np.linalg.eigh(v)
    vp=np.real(np.diag(u.conj().T@v@u)); v2p=np.real(np.diag(u.conj().T@(v@v)@u))
    outcome=np.abs(vu.conj().T@u)**2
    nprob=np.array([np.sum(abs(u[active==n,:])**2,axis=0) for n in range(1,5)])
    rows=[]
    for beta in (*BETA_VALUES,float('inf')):
        w,logz=thermal_weights(e,beta); mean=float(w@e)
        rows.append({'beta':'inf' if np.isinf(beta) else beta,'energy':mean,'entropy':float(-sum(w[w>0]*np.log(w[w>0]))),'volume':float(w@vp),'volume2':float(w@v2p),'active_probabilities':(nprob@w).tolist(),'zero_volume_probability':float((outcome[abs(ve)<=2e-10,:]@w).sum()),'logZ':logz,'heat_capacity':0. if np.isinf(beta) else float(beta**2*max(0.,w@(e*e)-mean*mean))})
    comm=h@v-v@h
    return {'energies':e.tolist(),'volume_eigenvalues':ve.tolist(),'commutator_frobenius':float(np.linalg.norm(comm)),'rows':rows}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--ks',type=int,nargs='+',default=[2,3,4]); ap.add_argument('--repeats',type=int,default=3); args=ap.parse_args()
    data={'settings':{'ks':args.ks,'repeats':args.repeats,'gamma':.2375,'U':5.,'t':1.,'absolute_tolerance':2e-9,'matvec_iterations':100,'thread_environment':{k:os.getenv(k) for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']}},'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform(),'blas':str(np.__config__.get_info('blas_opt_info'))},'cases':[]}
    for k in args.ks:
        model,construction=timed(lambda:build_fixed_k(k),args.repeats)
        v=sum(model['volume_by_triple'].values()); d=len(model['active_sites'])
        case={'K':k,'dimension':d,'magnetic_dimension':len(model['occupations_m0']),'construction':construction,'occupations':model['occupations_m0'],'basis':pack(model['basis']),'site_spins':model['site_spins'].tolist(),'active':model['active_sites'].tolist(),'onsite':pack(model['onsite']),'bonds':{f'{i}{j}':pack(x) for (i,j),x in model['bonds'].items()},'dots':{f'{i}{j}':pack(x) for (i,j),x in model['spin_dots'].items()},'volume':pack(v),'graphs':{}}
        for graph,edges in GRAPH_EDGES.items():
            h=5*model['onsite']-sum(model['bonds'][edge] for edge in edges)
            results,pipeline=timed(lambda:calculate(h,v,model['active_sites']),args.repeats)
            from scipy.sparse import csr_matrix
            sparse=csr_matrix(h); x=np.arange(1,d+1,dtype=float).astype(complex); x/=np.linalg.norm(x)
            def matvec():
                y=x
                for _ in range(100): y=sparse@y; y/=np.linalg.norm(y)
                return y
            y,apply=timed(matvec,args.repeats)
            _,eigen=timed(lambda:np.linalg.eigh(h),args.repeats)
            case['graphs'][graph]={'H':pack(h),'reference':results,'pipeline':pipeline,'eigendecomposition':eigen,'sparse_apply_100':apply,'final_state':pack(y)}
        triples=list(model['volume_by_triple']); pair01=model['spin_dots'][(0,1)]; pair12=model['spin_dots'][(1,2)]; q=1j*(pair01@pair12-pair12@pair01)
        def root():
            vals,_=np.linalg.eigh(q); tol=64*np.finfo(float).eps*max(1.,max(abs(vals))); vals,u=np.linalg.eigh(q); roots=np.sqrt(np.where(abs(vals)<=tol,0.,abs(vals))); return (u*roots)@u.conj().T
        r,rt=timed(root,args.repeats); case['root']={'Q':pack(q),'matrix':pack(r),'timing':rt}
        data['cases'].append(case)
        print(f'Python K={k}: dimension={d}, construction={construction["median_ms"]:.2f}ms',flush=True)
    data['environment']['process_peak_rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'python-reference.json').write_text(json.dumps(data,allow_nan=False))
if __name__=='__main__':main()
