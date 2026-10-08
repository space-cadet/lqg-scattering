#!/bin/bash
# T5e run recipe (run from the project root: `bash code/tools/run_t5e.sh`).
# Builds the vendored Rust engine, sweeps K in two reference families plus a
# second-seed robustness check, then fits V ~ K^alpha. All evidence (per-K
# lines, fit block) goes to stdout; raw + merged JSONs are written in the
# results/. Exits nonzero if any sanity gate fails.
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT"
mkdir -p results

echo "=== T5e build (rust t5e binary) ==="
if ! (cd code/rust && CARGO_NET_OFFLINE=true cargo build --release --offline --bin t5e 2>&1 | tail -2); then
  echo "offline build failed, retrying online"
  (cd code/rust && cargo build --release --bin t5e 2>&1 | tail -2)
fi
BIN=code/rust/target/release/t5e
test -x "$BIN" || { echo "BUILD FAILED: $BIN missing"; exit 1; }

echo "=== T5e sweep: uniform M=0 family, seed 11 (primary) ==="
"$BIN" --family uniform --ks 8,12,16,20,24 \
  --out results/t5e_raw_uniform.json --xcheck --controls

echo "=== T5e sweep: vertex-scaled family, seed 11 (robustness) ==="
"$BIN" --family vertex --ks 10,13,16,19,22 \
  --out results/t5e_raw_vertex.json --controls

echo "=== T5e sweep: uniform M=0, seed 42 (second seed) ==="
"$BIN" --family uniform --seed 42 --ks 8,16,24 \
  --out results/t5e_raw_seed42.json

echo "=== T5e fit ==="
python3 code/python/t5e_fit.py
