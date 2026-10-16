"""Classical linear-rotor ring, exact split flows and constrained sampling.

Units: I=lambda=1; q_i^2=1, q_i.J_i=0, sum J_i=0.
A small compiled numerical kernel is built into the system temporary directory.
"""
import ctypes
import hashlib
from pathlib import Path
import subprocess
import tempfile
import numpy as np

SOURCE=Path(__file__).resolve().parents[3]/'code/classical/rotors.cpp'


def kernel():
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()[:16]
    library=Path(tempfile.gettempdir())/f'lqg-rotors-{digest}.dylib'
    if not library.exists():
        subprocess.run(['clang++','-O3','-std=c++17','-dynamiclib',str(SOURCE),'-o',str(library)],check=True,capture_output=True)
    lib=ctypes.CDLL(str(library))
    ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
    lib.rotor_evolve.argtypes=[ctypes.c_int,ptr,ptr,ctypes.c_double,ctypes.c_int,ctypes.c_int,ptr]
    lib.rotor_evolve.restype=None
    lib.rotor_microcanonical.argtypes=[ctypes.c_int,ctypes.c_double,ptr,ctypes.c_ulonglong,ctypes.c_int,ctypes.c_int,ctypes.c_int,ptr]
    lib.rotor_microcanonical.restype=ctypes.c_double
    return lib


def initial_state(n,packet_energy,seed):
    """Nearly aligned, genuinely 3D orientations; tangent opposite momenta."""
    rng=np.random.default_rng(seed)
    q=np.tile([0.,0.,1.],(n,1))+.05*rng.normal(size=(n,3))
    q/=np.linalg.norm(q,axis=1)[:,None]
    axis=np.cross(q[0],q[1]);axis/=np.linalg.norm(axis)
    j=np.zeros_like(q);j[0]=np.sqrt(packet_energy)*axis;j[1]=-j[0]
    return np.ascontiguousarray(q),np.ascontiguousarray(j)


def evolve(q,j,dt,duration,sample_interval=.5):
    if dt<=0 or duration<=0 or sample_interval<dt:raise ValueError('invalid positive time grid')
    # Choose exact divisors, ensuring equal sample times across step refinements.
    stride=int(np.ceil(sample_interval/dt));dt=sample_interval/stride
    frames=int(round(duration/sample_interval));steps=frames*stride
    q=np.ascontiguousarray(q.copy(),dtype=float);j=np.ascontiguousarray(j.copy(),dtype=float)
    data=np.empty((frames+1,len(q)+8))
    kernel().rotor_evolve(len(q),q,j,dt,steps,stride,data)
    return np.arange(frames+1)*sample_interval,data,q,j,dt


def sample_microcanonical(q,energy,seed,burn=2000,samples=2000,thin=4):
    """Orientation weight det(B)^(-1/2) (E-V)^(N-5/2), B=sum(1-qq^T).

    Tangent Gaussian momenta are projected to sum J=0 and scaled to E-V.
    Returns full local-energy samples, not just an assumed equipartition value.
    """
    q=np.ascontiguousarray(q.copy(),dtype=float)
    v=np.sum(1-np.sum(q*np.roll(q,-1,axis=0),axis=1))
    if energy<=v:raise ValueError('starting orientation has no positive kinetic energy')
    data=np.empty((samples,len(q)+8))
    acceptance=kernel().rotor_microcanonical(len(q),energy,q,int(seed),burn,samples,thin,data)
    return data,acceptance


def evolve_graph(q,j,edges,coupling=1.,inertia=1.,dt=.005,duration=200.,sample_interval=.05):
    """General undirected graph; each edge counted once, arbitrary total J.

    Returns times, orientation and momentum histories, and actual step.
    Unlike the ring helper, two sites here have a single bond.
    """
    q=np.ascontiguousarray(q,dtype=float).copy();j=np.ascontiguousarray(j,dtype=float).copy()
    if q.ndim!=2 or q.shape[1]!=3 or j.shape!=q.shape or not np.all(np.isfinite(q)) or not np.all(np.isfinite(j)):
        raise ValueError('finite q and J arrays must have shape (N,3)')
    if np.max(abs(np.sum(q*q,axis=1)-1))>1e-10 or np.max(abs(np.sum(q*j,axis=1)))>1e-10:
        raise ValueError('rotor norm or tangency constraint violated')
    if inertia<=0 or dt<=0 or duration<=0 or sample_interval<dt or not np.isfinite([coupling,inertia,dt,duration,sample_interval]).all():
        raise ValueError('invalid time, inertia or coupling')
    pairs=[tuple(e) for e in edges]
    if any(len(e)!=2 or any(not isinstance(i,(int,np.integer)) or not 0<=i<len(q) for i in e) or e[0]==e[1] for e in pairs):
        raise ValueError('invalid edges')
    if len(set(tuple(sorted(e)) for e in pairs))!=len(pairs):raise ValueError('duplicate undirected edge')
    edges=np.ascontiguousarray(pairs,dtype=np.int32).reshape(-1,2)
    weights=np.full(len(edges),coupling,dtype=float)
    stride=int(np.ceil(sample_interval/dt));dt=sample_interval/stride
    frames=int(round(duration/sample_interval))
    if abs(frames*sample_interval-duration)>1e-10:raise ValueError('duration must divide sample interval')
    out=np.empty((frames+1,2,len(q),3))
    lib=kernel();ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
    iptr=np.ctypeslib.ndpointer(dtype=np.int32,flags='C_CONTIGUOUS')
    lib.rotor_graph_evolve.argtypes=[ctypes.c_int,ctypes.c_int,iptr,ptr,ptr,ptr,ctypes.c_double,ctypes.c_double,ctypes.c_int,ctypes.c_int,ptr]
    lib.rotor_graph_evolve.restype=None
    lib.rotor_graph_evolve(len(q),len(edges),edges,weights,q,j,inertia,dt,frames*stride,stride,out)
    return np.arange(frames+1)*sample_interval,out[:,0],out[:,1],dt


def evolve_transfer(q,j,coupling=1.,inertia=1.,dt=.005,duration=2000.,sample_interval=.5):
    """Ring readouts with explicit physical parameters and per-site kinetic energy.

    Columns 0..3 and 5..7 match evolve; column 4 is cold kinetic energy.
    Columns 8..8+N are local total energies; final N columns are kinetic energies.
    """
    q=np.ascontiguousarray(q,dtype=float).copy();j=np.ascontiguousarray(j,dtype=float).copy()
    if q.ndim!=2 or q.shape[1]!=3 or j.shape!=q.shape or len(q)<3 or not np.all(np.isfinite(q)) or not np.all(np.isfinite(j)):
        raise ValueError('finite q/J must have matching (N,3) shapes, N>=3')
    if coupling<=0 or inertia<=0 or dt<=0 or duration<=0 or sample_interval<dt or not np.isfinite([coupling,inertia,dt,duration,sample_interval]).all():
        raise ValueError('invalid positive model or time parameters')
    if np.max(abs(np.sum(q*q,axis=1)-1))>1e-10 or np.max(abs(np.sum(q*j,axis=1)))>1e-9:raise ValueError('invalid rotor constraints')
    stride=int(np.ceil(sample_interval/dt));dt=sample_interval/stride
    frames=int(round(duration/sample_interval))
    if abs(frames*sample_interval-duration)>1e-9:raise ValueError('duration must divide sample interval')
    data=np.empty((frames+1,8+2*len(q)))
    lib=kernel();ptr=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
    lib.rotor_ring_transfer.argtypes=[ctypes.c_int,ptr,ptr,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_int,ctypes.c_int,ptr]
    lib.rotor_ring_transfer.restype=None
    lib.rotor_ring_transfer(len(q),q,j,coupling,inertia,dt,frames*stride,stride,data)
    return np.arange(frames+1)*sample_interval,data,q,j,dt
