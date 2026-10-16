"""Audit saved witnesses using dictionary ladder algebra, without matrix builders."""
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/t11-face-connectivity'

def add(out,key,value):out[key]=out.get(key,0j)+value

def unpack(records):return {tuple(r['occupation']):complex(r['amplitude_real'],r['amplitude_imag']) for r in records}

def inner(a,b):return sum(v.conjugate()*b.get(o,0) for o,v in a.items())

def norm(a):return math.sqrt(sum(abs(v)**2 for v in a.values()))

def h_action(state,edges):
    out={}
    for occ,amp in state.items():
        n=[sum(occ[i:i+2]) for i in range(0,len(occ),2)]
        add(out,occ,amp*sum(x*(x+2)/4 for x in n))
        for i,j in edges:
            for source,target in [(i,j),(j,i)]:
                for species in [0,1]:
                    s=2*source+species;d=2*target+species
                    if occ[s]:
                        changed=list(occ);changed[s]-=1;changed[d]+=1
                        add(out,tuple(changed),-amp*math.sqrt(occ[s]*(occ[d]+1)))
    return out

def ladder(state,raising):
    out={}
    for occ,amp in state.items():
        for site in range(len(occ)//2):
            a,b=2*site,2*site+1;s,d=(b,a) if raising else (a,b)
            if occ[s]:
                changed=list(occ);changed[s]-=1;changed[d]+=1
                add(out,tuple(changed),amp*math.sqrt(occ[s]*(occ[d]+1)))
    return out

def squared(state):
    out={o:amp*(sum(occ for occ in o[::2])-sum(occ for occ in o[1::2]))**2/4 for o,amp in state.items()}
    for term in [ladder(ladder(state,False),True),ladder(ladder(state,True),False)]:
        for o,v in term.items():add(out,o,v/2)
    return out

def active(occ):return sum(sum(occ[i:i+2])>0 for i in range(0,len(occ),2))

def main():
    maximum=0.;count=0
    def check(value):
        nonlocal maximum,count
        residual=abs(value);count+=1;maximum=max(maximum,residual)
        assert residual<2e-10,(count,value)
    record=json.loads((OUT/'L6-K3.json').read_text())
    for name,g in record['graphs'].items():
        edges=([(i,(i+1)%6) for i in range(6)] if name=='ring' else
               [(i,j) for i in range(6 if name=='complete' else 4) for j in range(i+1,6 if name=='complete' else 4)])
        for label,w in g['witnesses'].items():
            state=unpack(w['states']['source']);h=h_action(state,edges);h2=h_action(h,edges)
            check(norm({o:v for o,v in h.items() if active(o)==5})-w['norm_P5_H_source'])
            check(norm({o:v for o,v in h2.items() if active(o)==6})-w['norm_P6_H2_source'])
            for target,records in w['states'].items():
                v=unpack(records);check(norm(v)-1)
                j=0 if label=='closed' else 3
                j2=squared(v);res=dict(j2)
                for o,a in v.items():add(res,o,-j*(j+1)*a)
                check(norm(res))
                want=4 if target=='source' else (5 if target=='target5' else 6)
                check(norm({o:a for o,a in v.items() if active(o)!=want}))
        for label,w in g.get('directed_chain',{}).items():
            source=unpack(g['witnesses'][label]['states']['source'])
            target5=unpack(w['target5']);target6=unpack(w['target6'])
            check(inner(target5,h_action(source,edges))+math.sqrt(2))
            check(inner(target6,h_action(target5,edges))+math.sqrt(2))
            check(inner(target6,h_action(h_action(source,edges),edges))-w['H2_target6_source'])
    provenance=json.loads((OUT/'summary.json').read_text())
    for name,digest in provenance['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    result=dict(comparisons=count,maximum_residual=maximum,tolerance=2e-10,method='independent dictionary oscillator and SU(2) ladder algebra on saved full-Fock witnesses')
    (OUT/'independent-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result)

if __name__=='__main__':main()
