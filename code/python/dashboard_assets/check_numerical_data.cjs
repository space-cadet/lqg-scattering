const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'), dir=path.join(root,'code/dashboard');
const model=require(dir+'/data-model.js'), schema=require(dir+'/data.schema.json'), manifest=require(dir+'/datasets.json');
let links=0, hashChecks=0, rows=0;
for(const relative of ['data.json',...manifest.datasets.map(d=>d.path)]) {
 const filename=path.join(dir,relative),data=JSON.parse(fs.readFileSync(filename));
 const errors=model.validate(data,schema);if(errors.length)throw Error(relative+':'+errors.join('\n'));
 rows+=data.runs.length;
 for(const a of [...(data.docs||[]),...(data.figures||[]),...data.runs.flatMap(r=>[...(r.artifacts||[]),...(r.figures||[])])]){
  const u=new URL(a.path,'http://local'+filename);const local=decodeURIComponent(u.pathname);if(!fs.existsSync(local))throw Error('Missing '+local);links++;
  if(a.sha256){const actual=crypto.createHash('sha256').update(fs.readFileSync(local)).digest('hex');if(actual!==a.sha256)throw Error('Hash mismatch '+local);hashChecks++;}
 }
}
console.log(JSON.stringify({datasets:manifest.datasets.length,rows,links,hashChecks,validation:'PASS'},null,2));
