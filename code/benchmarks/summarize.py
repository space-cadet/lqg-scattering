"""Verify paired artifacts and write a compact benchmark report."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/python-vs-ts'
p = json.loads((OUT / 'python-reference.json').read_text())
t = json.loads((OUT / 'ts-results.json').read_text())
rows = []
for tc in t['cases']:
    pc = next(case for case in p['cases'] if case['K'] == tc['K'])
    assert pc['dimension'] == tc['dimension']
    def add(work, py, ts, error):
        assert error <= p['settings']['absolute_tolerance']
        rows.append({'K': pc['K'], 'dimension': pc['dimension'], 'work': work,
                     'python_ms': py['median_ms'], 'ts_ms': ts['median_ms'],
                     'ts_over_python': ts['median_ms'] / py['median_ms'],
                     'max_abs_error': error})
    add('construction', pc['construction'], tc['construction'], max(tc['construction_errors'].values()))
    add('positive_root', pc['root']['timing'], tc['root']['timing'], tc['root']['max_error'])
    for graph, case in pc['graphs'].items():
        other = tc['graphs'][graph]
        for field in ['pipeline', 'eigendecomposition', 'sparse_apply_100']:
            error = other['sparse_state_error'] if field == 'sparse_apply_100' else other['reference_max_error']
            add(graph + '_' + field, case[field], other[field], error)
summary = {
    'settings': p['settings'], 'python_environment': p['environment'],
    'ts_environment': t['environment'], 'rows': rows,
    'source_sha256': {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest()
                      for f in (ROOT / 'code/benchmarks').glob('*') if f.is_file()},
}
tsroot = Path(t['environment']['built_package']).parents[1]
summary['ts_source_sha256'] = {
    str(f.relative_to(tsroot)): hashlib.sha256(f.read_bytes()).hexdigest()
    for f in tsroot.glob('src/**/*.ts')
}
summary['ts_git_head'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=tsroot, text=True).strip()
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2))
lines = [
    '# Python versus ts-quantum: first T11 benchmarks', '',
    'These are warm local CPU measurements, not general language rankings. The matched end-to-end run independently constructs the four-site fixed-area singlet model at $K=2$, including six hopping bonds and four RS terms. The Python reference artifacts also cover $K=3,4$; matched TS runs for those areas have not been saved. Matrix entries are checked after aligning coupled-basis phases.',
    '$U/t=5$, $g=0$, $\\gamma=0.2375$, $\\hbar=1$. Python uses one BLAS thread. Each workload has one warm-up and three measured repetitions; the table reports medians. Compilation, loading JSON, result writing, and plotting are excluded.', '',
    '| K | Work | Python ms | TS ms | TS / Python |', '|---:|---|---:|---:|---:|',
]
for r in rows:
    lines.append(f'| {r["K"]} | {r["work"]} | {r["python_ms"]:.3f} | {r["ts_ms"]:.3f} | {r["ts_over_python"]:.2f} |')
lines += [
    '', 'The T11 subset builds $H$, diagonalizes $H$ and $V$, and computes thermal energy, entropy, heat capacity, volume moments, active-site probabilities, zero-volume probability, and $\\|[H,V]\\|_F$. It excludes the original driver’s one-site reduced entropy, pair correlations, conditional distributions, operator norm, CSVs, and plots.',
    '', 'Sparse application performs 100 repeated sparse matrix-vector products, normalizing after each product in both implementations. Positive-root timing uses the full singlet-space $q_{012}$ matrix with the common zero-mode cutoff. Both root paths diagonalize once to set the cutoff and once to reconstruct the matrix function. Construction timings include implementation differences and Python CG cache reuse.',
    '', 'The JSON records process peak RSS. Python ran K=2,3,4 while TS ran K=2, so their process peaks are not directly comparable. Startup was excluded and not benchmarked.',
    '', 'The TS adapter uses StateVector, SparseOperator, MatrixOperator, Clebsch–Gordan coefficients, and eigensystem from the freshly built CJS package. Occupation enumeration, Schwinger assembly, coupled-basis projection, and T11 orchestration are benchmark adapters layered on the library. Fixtures verify the independently constructed TS matrices and provide common-matrix kernels.',
    '', 'K=3 passed a previous in-memory TS comparison, but it did not save an artifact before the K=4 run was interrupted. Its timings are omitted. The K=4 TS run was stopped because construction and evaluation were taking substantially longer than the K=2 case.',
    '', 'A separate library issue surfaced: MatrixOperator.compose carries Hermitian metadata to products of noncommuting Hermitian operators. The adapter labels intermediate products general. The library itself was not modified by this benchmark.',
    '', 'Reproduce the Python references and matched K=2 run:', '```bash',
    'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 /Users/deepak/miniconda3/envs/qc-diff/bin/python code/benchmarks/python_reference.py',
    'node code/benchmarks/run_ts_benchmark.cjs results/python-vs-ts/python-reference.json results/python-vs-ts/ts-results.json 2',
    'python3 code/benchmarks/summarize.py', '```',
    '', 'Set TS_QUANTUM_ROOT to use another checkout. Build its source before running. The saved hashes identify the harness, library source, and library Git revision.',
]
(OUT / 'README.md').write_text('\n'.join(lines) + '\n')
for r in rows:
    print(f'K={r["K"]} {r["work"]}: Python {r["python_ms"]:.3f}ms TS {r["ts_ms"]:.3f}ms ratio {r["ts_over_python"]:.2f}')
