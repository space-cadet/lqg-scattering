# Python versus ts-quantum: first T11 benchmarks

These are warm local CPU measurements, not general language rankings. The matched end-to-end run independently constructs the four-site fixed-area singlet model at $K=2$, including six hopping bonds and four RS terms. The Python reference artifacts also cover $K=3,4$; matched TS runs for those areas have not been saved. Matrix entries are checked after aligning coupled-basis phases.
$U/t=5$, $g=0$, $\gamma=0.2375$, $\hbar=1$. Python uses one BLAS thread. Each workload has one warm-up and three measured repetitions; the table reports medians. Compilation, loading JSON, result writing, and plotting are excluded.

| K | Work | Python ms | TS ms | TS / Python |
|---:|---|---:|---:|---:|
| 2 | construction | 56.447 | 84.339 | 1.49 |
| 2 | positive_root | 0.190 | 49.527 | 261.07 |
| 2 | complete_pipeline | 0.731 | 387.015 | 529.49 |
| 2 | complete_eigendecomposition | 0.212 | 186.722 | 881.63 |
| 2 | complete_sparse_apply_100 | 2.795 | 11.061 | 3.96 |
| 2 | ring_pipeline | 1.042 | 258.865 | 248.52 |
| 2 | ring_eigendecomposition | 0.230 | 199.766 | 867.76 |
| 2 | ring_sparse_apply_100 | 3.226 | 8.663 | 2.69 |

The T11 subset builds $H$, diagonalizes $H$ and $V$, and computes thermal energy, entropy, heat capacity, volume moments, active-site probabilities, zero-volume probability, and $\|[H,V]\|_F$. It excludes the original driver’s one-site reduced entropy, pair correlations, conditional distributions, operator norm, CSVs, and plots.

Sparse application performs 100 repeated sparse matrix-vector products, normalizing after each product in both implementations. Positive-root timing uses the full singlet-space $q_{012}$ matrix with the common zero-mode cutoff. Both root paths diagonalize once to set the cutoff and once to reconstruct the matrix function. Construction timings include implementation differences and Python CG cache reuse.

The JSON records process peak RSS. Python ran K=2,3,4 while TS ran K=2, so their process peaks are not directly comparable. Startup was excluded and not benchmarked.

The TS adapter uses StateVector, SparseOperator, MatrixOperator, Clebsch–Gordan coefficients, and eigensystem from the freshly built CJS package. Occupation enumeration, Schwinger assembly, coupled-basis projection, and T11 orchestration are benchmark adapters layered on the library. Fixtures verify the independently constructed TS matrices and provide common-matrix kernels.

K=3 passed a previous in-memory TS comparison, but it did not save an artifact before the K=4 run was interrupted. Its timings are omitted. The K=4 TS run was stopped because construction and evaluation were taking substantially longer than the K=2 case.

A separate library issue surfaced: MatrixOperator.compose carries Hermitian metadata to products of noncommuting Hermitian operators. The adapter labels intermediate products general. The library itself was not modified by this benchmark.

Reproduce the Python references and matched K=2 run:
```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 /Users/deepak/miniconda3/envs/qc-diff/bin/python code/benchmarks/python_reference.py
node code/benchmarks/run_ts_benchmark.cjs results/python-vs-ts/python-reference.json results/python-vs-ts/ts-results.json 2
python3 code/benchmarks/summarize.py
```

Set TS_QUANTUM_ROOT to use another checkout. Build its source before running. The saved hashes identify the harness, library source, and library Git revision.
