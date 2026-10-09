const fs=require('fs');const path=require('path');
const root=process.env.TS_QUANTUM_ROOT||'/Users/deepak/code/ts-quantum';
const ts=require(path.join(root,'node_modules/typescript'));
const source=path.join(__dirname,'ts_quantum_benchmark.ts');
const output=ts.transpileModule(fs.readFileSync(source,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
const Module=require('module');const m=new Module(source,module);m.filename=source;m.paths=module.paths;m._compile(output,source);
