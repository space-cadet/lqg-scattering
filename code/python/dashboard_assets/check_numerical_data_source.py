"""Check exported case values against the original CSV/JSON source selectors."""
import csv,json,math,re
from pathlib import Path
root=Path(__file__).resolve().parents[3];base=root/'code/dashboard'
manifest=json.loads((base/'datasets.json').read_text());cases=0;leaves=0

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
print(f'PASS: {cases} numerical rows and {leaves} numeric values match saved source records')
