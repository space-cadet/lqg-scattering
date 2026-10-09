// @ts-nocheck
/** Research benchmark adapter. Uses the freshly built ts-quantum package;
 * occupation enumeration/projection are explicit additions above its API. */
const fs = require('fs');
const path = require('path');
const { performance } = require('perf_hooks');
const root = process.env.TS_QUANTUM_ROOT || '/Users/deepak/code/ts-quantum';
const math = require(path.join(root, 'node_modules/mathjs'));
const { StateVector, MatrixOperator, SparseOperator, clebschGordan, matrixFunction } = require(path.join(root, 'dist/index.js'));
const c = (r, i=0) => math.complex(r,i);
const zero = n => Array.from({length:n},()=>Array.from({length:n},()=>c(0)));
const key = a => a.join(',');
const pairs = [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]];
const triples = [[0,1,2],[0,1,3],[0,2,3],[1,2,3]];
const graphs = {complete:pairs,ring:[[0,1],[1,2],[2,3],[0,3]]};
function compositions(n,p) { if(p===1)return [[n]];const out=[];for(let i=0;i<=n;i++)for(const tail of compositions(n-i,p-1))out.push([i,...tail]);return out; }
function occupationModel(K) {
 const comp=compositions(K,4);const occupations=[];
 for(const a of comp)for(const b of comp)occupations.push(a.flatMap((x,i)=>[x,b[i]]));
 const index=new Map(occupations.map((o,i)=>[key(o),i]));const states=[],labels=[],blocks=[];
 for(const spins of compositions(2*K,4)) {
  if(Math.max(...spins)>K)continue;
  const channels=[];for(let k=Math.abs(spins[0]-spins[1]);k<=spins[0]+spins[1];k+=2)
   if(k>=Math.abs(spins[2]-spins[3])&&k<=spins[2]+spins[3]&&(k-Math.abs(spins[2]-spins[3]))%2===0)channels.push(k);
  if(!channels.length)continue;
  const start=states.length;
  for(const k of channels){
   const amps=Array.from({length:occupations.length},()=>c(0));
   for(let row=0;row<occupations.length;row++){
    const o=occupations[row];if(spins.some((s,i)=>s!==o[2*i]+o[2*i+1]))continue;
    const m=spins.map((s,i)=>o[2*i]-o[2*i+1]),p=m[0]+m[1];
    if(Math.abs(p)>k)continue;
    const a=clebschGordan(spins[0]/2,m[0]/2,spins[1]/2,m[1]/2,k/2,p/2).re;
    const b=clebschGordan(spins[2]/2,m[2]/2,spins[3]/2,m[3]/2,k/2,-p/2).re;
    amps[row]=c(a*b*((k-p)/2%2===0?1:-1)/Math.sqrt(k+1));
   }
   states.push(new StateVector(occupations.length,amps,'four-site M=0'));labels.push({spins,k});
  }
  blocks.push([start,states.length]);
 }
 const rowSupport=occupations.map((_,r)=>states.flatMap((s,j)=>Math.abs(s.amplitudes[r].re)>1e-14?[[j,s.amplitudes[r].re]]:[]));
 return {K,occupations,index,states,labels,blocks,rowSupport};
}
function magneticOperator(model,pair,kind){
 const [i,j]=pair,entries=[];
 for(let col=0;col<model.occupations.length;col++){
  const o=model.occupations[col];
  if(kind==='dot'){
   const diag=(o[2*i]-o[2*i+1])*(o[2*j]-o[2*j+1])/4;
   if(diag)entries.push({row:col,col,value:c(diag)});
   for(const [u,v] of [[i,j],[j,i]])if(o[2*u+1]&&o[2*v]){
    const t=o.slice();t[2*u]++;t[2*u+1]--;t[2*v]--;t[2*v+1]++;
    entries.push({row:model.index.get(key(t)),col,value:c(.5*Math.sqrt((o[2*u]+1)*o[2*u+1]*o[2*v]*(o[2*v+1]+1)))});
   }
  }else for(const [u,v] of [[i,j],[j,i]])for(let s=0;s<2;s++)if(o[2*u+s]){
   const t=o.slice();t[2*u+s]--;t[2*v+s]++;
   entries.push({row:model.index.get(key(t)),col,value:c(Math.sqrt(o[2*u+s]*(o[2*v+s]+1)))});
  }
 }
 return new SparseOperator({rows:model.occupations.length,cols:model.occupations.length,entries,nnz:entries.length},'general');
}
function project(model,op){
 const matrix=zero(model.states.length);
 for(let col=0;col<model.states.length;col++){
  const y=op.apply(model.states[col]);
  for(let r=0;r<y.dimension;r++)if(Math.abs(y.amplitudes[r].re)>1e-14)
   for(const [row,a] of model.rowSupport[r])matrix[row][col].re+=a*y.amplitudes[r].re;
 }
 return new MatrixOperator(matrix,'general');
}
function positiveRoot(op){const vals=op.eigensystem().values.map(x=>x.re);const tol=64*Number.EPSILON*Math.max(1,...vals.map(Math.abs));return new MatrixOperator(matrixFunction(op.toMatrix(),x=>c(Math.abs(x.re)<=tol?0:Math.sqrt(Math.abs(x.re)))),'general');}
function build(K){
 const model=occupationModel(K),d=model.states.length;
 const onsite=zero(d);model.labels.forEach((l,i)=>onsite[i][i]=c(l.spins.reduce((s,n)=>s+n*(n-1)/2,0)));
 const bonds={},dots={};for(const p of pairs){bonds[p.join('')]=project(model,magneticOperator(model,p,'hop'));dots[p.join('')]=project(model,magneticOperator(model,p,'dot'));}
 const volume=zero(d);
 for(const [start,stop] of model.blocks)for(const [i,j,k] of triples){
  const small=op=>new MatrixOperator(op.toMatrix().slice(start,stop).map(row=>row.slice(start,stop)),'general');
  const a=small(dots[`${i}${j}`]),b=small(dots[`${j}${k}`]);
  const q=a.compose(b).add(b.compose(a).scale(c(-1))).scale(c(0,1));const r=positiveRoot(q).toMatrix();
  for(let x=start;x<stop;x++)for(let y=start;y<stop;y++)volume[x][y]=math.add(volume[x][y],math.multiply(Math.pow(.2375,1.5),r[x-start][y-start]));
 }
 return {...model,onsite:new MatrixOperator(onsite,'general'),bonds,dots,volume:new MatrixOperator(volume,'general'),active:model.labels.map(l=>l.spins.filter(x=>x>0).length)};
}
function decode(p){return new MatrixOperator(p.re.map((row,i)=>row.map((x,j)=>c(x,p.im[i][j]))),'general');}
function maxError(a,b){if(Array.isArray(a))return Math.max(0,...a.map((x,i)=>maxError(x,b[i])));if(a&&typeof a==='object')return Math.hypot(a.re-b.re,a.im-b.im);return Math.abs(a-b);}
function timed(fn,repeats){fn();const samples=[];let value;for(let i=0;i<repeats;i++){const t=performance.now();value=fn();samples.push(performance.now()-t);}const sorted=samples.slice().sort((a,b)=>a-b);return {value,timing:{median_ms:sorted[Math.floor(sorted.length/2)],samples_ms:samples}};}
function calculate(h,v,active){
 const eig=h.eigensystem(),ve=v.eigensystem();const energies=eig.values.map(x=>x.re),vvals=ve.values.map(x=>x.re);
 const vp=[],v2p=[],np=[],zp=[];
 eig.vectors.forEach(s=>{
  const vs=v.apply(s);vp.push(s.innerProduct(vs).re);v2p.push(vs.innerProduct(vs).re);
  np.push([1,2,3,4].map(n=>s.amplitudes.reduce((sum,a,i)=>sum+(active[i]===n?a.re*a.re+a.im*a.im:0),0)));
  zp.push(ve.vectors.reduce((sum,u,i)=>sum+(Math.abs(vvals[i])<=2e-10?Math.pow(math.abs(u.innerProduct(s)),2):0),0));
 });
 const rows=[0,.1,.25,.5,1,2,4,8,16,Infinity].map(beta=>{
  const raw=energies.map(e=>beta===Infinity?(Math.abs(e-energies[0])<=2e-10?1:0):Math.exp(-beta*(e-energies[0]))),z=raw.reduce((a,b)=>a+b,0),w=raw.map(x=>x/z);
  const mean=energies.reduce((s,e,i)=>s+w[i]*e,0),dot=a=>a.reduce((s,x,i)=>s+w[i]*x,0);
  return {beta:beta===Infinity?'inf':beta,energy:mean,entropy:-w.reduce((s,x)=>s+(x>0?x*Math.log(x):0),0),volume:dot(vp),volume2:dot(v2p),active_probabilities:[0,1,2,3].map(n=>dot(np.map(a=>a[n]))),zero_volume_probability:dot(zp),logZ:beta===Infinity?null:-beta*energies[0]+Math.log(z),heat_capacity:beta===Infinity?0:beta*beta*Math.max(0,dot(energies.map(e=>e*e))-mean*mean)};
 });
 const comm=h.compose(v).add(v.compose(h).scale(c(-1))).toMatrix();
 return {energies,volume_eigenvalues:vvals,commutator_frobenius:Math.sqrt(comm.flat().reduce((s,x)=>s+x.re*x.re+x.im*x.im,0)),rows};
}
function main(){
 const input=process.argv[2],output=process.argv[3];const reference=JSON.parse(fs.readFileSync(input,'utf8')),repeats=reference.settings.repeats,tol=reference.settings.absolute_tolerance;
 const result={settings:reference.settings,environment:{node:process.version,platform:process.platform,arch:process.arch,ts_quantum_version:require(path.join(root,'package.json')).version,built_package:path.join(root,'dist/index.js')},cases:[]};
 const selected=reference.cases.filter(fixture=>!process.argv[4]||fixture.K===Number(process.argv[4]));
 for(const fixture of selected){
  const {value:m,timing:construction}=timed(()=>build(fixture.K),repeats),d=m.states.length;
  // Coupled-state phases are conventional. Require identical normalized columns
  // up to a single real phase, then transform every operator consistently.
  const phases=m.states.map((s,j)=>{const overlap=s.amplitudes.reduce((sum,a,r)=>sum+a.re*fixture.basis.re[r][j],0);if(Math.abs(Math.abs(overlap)-1)>tol)throw Error('Coupling basis mismatch');return overlap<0?-1:1;});
  const align=op=>new MatrixOperator(op.toMatrix().map((row,i)=>row.map((z,j)=>math.multiply(phases[i]*phases[j],z))));
  m.states=m.states.map((s,j)=>s.scale(c(phases[j])));m.onsite=align(m.onsite);m.volume=align(m.volume);
  for(const p of pairs)for(const name of ['bonds','dots'])m[name][p.join('')]=align(m[name][p.join('')]);
  const errors={basis:maxError(m.occupations.map((_,r)=>m.states.map(s=>s.amplitudes[r])),fixture.basis.re.map((row,i)=>row.map((x,j)=>c(x,fixture.basis.im[i][j])))),onsite:maxError(m.onsite.toMatrix(),decode(fixture.onsite).toMatrix()),volume:maxError(m.volume.toMatrix(),decode(fixture.volume).toMatrix())};
  for(const p of pairs)for(const name of ['bonds','dots'])errors[name+p.join('')]=maxError(m[name][p.join('')].toMatrix(),decode(fixture[name][p.join('')]).toMatrix());
  const caseResult={K:fixture.K,dimension:d,construction,phase_flips:phases.filter(x=>x<0).length,construction_errors:errors,graphs:{}};
  if(Math.max(...Object.values(errors))>tol)throw Error('Construction mismatch '+JSON.stringify(errors));
  for(const [graph,edges] of Object.entries(graphs)){
   const h=edges.reduce((op,p)=>op.add(m.bonds[p.join('')].scale(c(-1))),m.onsite.scale(c(5)));
   const {value:observables,timing:pipeline}=timed(()=>calculate(h,m.volume,m.active),repeats);
   const ref=fixture.graphs[graph],common=decode(ref.H),entries=[];
   common.toMatrix().forEach((row,i)=>row.forEach((x,j)=>{if(Math.hypot(x.re,x.im)>0)entries.push({row:i,col:j,value:x});}));
   const sparse=new SparseOperator({rows:d,cols:d,entries,nnz:entries.length},'general');const x=new StateVector(d,Array.from({length:d},(_,i)=>c(i+1))).normalize();
   const {value:y,timing:apply}=timed(()=>{let y=x;for(let i=0;i<100;i++)y=sparse.apply(y).normalize();return y;},repeats);
   const {timing:eigen}=timed(()=>common.eigensystem(),repeats);
   const obsError=maxError(observables.energies,ref.reference.energies);
   let error=Math.max(obsError,Math.abs(observables.commutator_frobenius-ref.reference.commutator_frobenius),maxError(observables.volume_eigenvalues,ref.reference.volume_eigenvalues));
   for(let i=0;i<observables.rows.length;i++)for(const field of ['energy','entropy','volume','volume2','active_probabilities','zero_volume_probability','logZ','heat_capacity'])if(observables.rows[i][field]!==null)error=Math.max(error,maxError(observables.rows[i][field],ref.reference.rows[i][field]));
   const stateError=maxError(y.amplitudes,ref.final_state.re.map((r,i)=>c(r,ref.final_state.im[i])));
   caseResult.graphs[graph]={reference_max_error:error,sparse_state_error:stateError,pipeline,eigendecomposition:eigen,sparse_apply_100:apply,observables};
   if(error>tol||stateError>tol)throw Error('Observable mismatch '+fixture.K+' '+graph+' '+error+' '+stateError);
  }
  const q=decode(fixture.root.Q);const {value:r,timing:rt}=timed(()=>positiveRoot(q),repeats);caseResult.root={timing:rt,max_error:maxError(r.toMatrix(),decode(fixture.root.matrix).toMatrix())};
  if(caseResult.root.max_error>tol)throw Error('Root mismatch');
  result.cases.push(caseResult);fs.writeFileSync(output,JSON.stringify(result,null,2));console.log(`TS K=${fixture.K}: dimension=${d}, construction=${construction.median_ms.toFixed(2)}ms, verified`);
 }
 result.environment.process_peak_rss_bytes=process.resourceUsage().maxRSS*1024;fs.writeFileSync(output,JSON.stringify(result,null,2));
}
main();
