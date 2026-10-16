"""Check exported case values against the original CSV/JSON source selectors."""
import csv,json,math,re,hashlib
from pathlib import Path
from curated_t11 import face_connectivity_rows, quantum_planar_rows
root=Path(__file__).resolve().parents[3];base=root/'code/dashboard'
manifest=json.loads((base/'datasets.json').read_text());catalogue=json.loads((base/'studies.json').read_text());cases=0;leaves=0

def same(a,b,label):
 global leaves
 if isinstance(a,dict):
  for k,v in a.items():
   assert k in b,(label,k,'missing');same(v,b[k],label+'.'+k)
 elif isinstance(a,list):
  assert len(a)==len(b),(label,'length')
  for i,(x,y) in enumerate(zip(a,b)):same(x,y,label+f'[{i}]')
 elif isinstance(a,float) and not math.isfinite(a):assert b is None,label
 elif isinstance(a,str) and re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?',a):
  assert float(a)==float(b),(label,a,b);leaves+=1
 elif isinstance(a,(int,float)) and not isinstance(a,bool):assert a==b or str(a)==b,(label,a,b);leaves+=1
 else: assert a==b or (a=='' and b is None) or str(a)==b,(label,a,b)

for ds in manifest['datasets']:
 d=json.loads((base/ds['path']).read_text())
 for run in d['runs']:
  p=run['provenance'];source=root/p['presentationSource'];selector=p['sourceSelector']
  if source.suffix=='.csv':
   with source.open(newline='') as f:raw=list(csv.DictReader(f))[int(selector.rsplit('-',1)[1])-1]
  else:
   raw=json.loads(source.read_text())
   if selector.startswith('studies.'):
    identifier=selector.split('.')[1];raw=next(s for s in raw['studies'] if s['id']==identifier)['table']['rows'][int(re.search(r'\[(\d+)\]',selector)[1])]
   else:
    tokens=re.findall(r'([^\.\[\]]+)|\[(\d+)\]',selector)
    for key,index in tokens:
     if key=='$':continue

     try:
      if index and isinstance(raw,dict):
       count=len(raw['eps']);raw={k:v[int(index)] if isinstance(v,list) else v for k,v in raw.items() if not isinstance(v,list) or len(v)==count}
      else: raw=raw[int(index)] if index else raw[key]
     except Exception: print(run['runId'],selector,key,index,type(raw)); raise
  combined={**run['parameters'],**run['results']}
  same(raw,combined,run['runId']);cases+=1

# Verify hashes against original source files, including intentionally
# un-packaged compact observables used to derive dashboard summary columns.
expected_hashes={}
for study in catalogue['studies']:
 for file in study.get('files',[]):
  expected_hashes[file['source']]=file['sourceSha256']
 for source,digest in study.get('sourceHashes',{}).items():
  if source in expected_hashes and expected_hashes[source]!=digest:
   raise AssertionError((study['id'],source,'conflicting source hashes'))
  expected_hashes[source]=digest
for source,expected in expected_hashes.items():
 actual=hashlib.sha256((root/source).read_bytes()).hexdigest()
 assert actual==expected,(source,expected,actual)

# Independently reconstruct the two compact, source-derived witness tables.
by_id={study['id']:study for study in catalogue['studies']}
same(quantum_planar_rows(root),by_id['t11-quantum-planar-rotors']['table']['rows'],'NS37')
same(face_connectivity_rows(root),by_id['t11-face-connectivity']['table']['rows'],'NS38')
geometry=json.loads((base/'datasets/t11-geometric-redistribution.json').read_text())
assert len(geometry['runs'])==54,('NS39 trajectory count',len(geometry['runs']))
group_sizes={}
for run in geometry['runs']:
 key=run['results']['series'];group_sizes[key]=group_sizes.get(key,0)+1
assert len(group_sizes)==18 and set(group_sizes.values())=={3},('NS39 grouped chart series',group_sizes)
assert len(json.loads((root/'results/t11-geometric-redistribution/geometry.json').read_text()))==270
print(f'PASS: {cases} numerical rows and {leaves} numeric values match saved source records')
print(f'PASS: {len(expected_hashes)} unique original-source SHA-256 hashes match')
print('PASS: NS37 and NS38 summaries reconstruct from saved results; NS39 has 54 rows, 18 groups and 270 geometry samples')
