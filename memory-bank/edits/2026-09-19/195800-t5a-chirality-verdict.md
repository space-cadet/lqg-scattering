#### 19:58 IST - T5a: Triple-volume correlations -- per-triple chirality verdict landed

- **Action**: Updated
- **What**: Merged `main-orx` commit `0731eaf` ("T5a: triple-volume correlations at n=6,7 -- per-triple chirality verdict") into workspace `main` as merge commit `2583b6a`. Resolved add/add conflict in `memory-bank/implementation-details/experiments.md` by keeping both sides (workspace Notes block + orx's new T5a spec/results).
- **Result sign-off**: sign-agreement 0.50-0.70 across seeds at n=6,7; cross-seed Pearson |q| ~ 0 -> **no global handedness, chirality is per-triple**. New `rust/src/onthefly.rs` engine (combinatorial rank indexing + rayon atomic-scatter matvec) handles dim-40M Fock spaces at n=7 in ~3 min; n=8 resource-bound at spec reference (~10 GB/vector), documented.
- **Verification**: `cargo test --release` passes 19/19 (including `experiment::tests::n4_sign_matches_python` and 4 `onthefly` stored-vs-OTF engine cross-checks).
- **Memory-bank**: `tasks.md` marks T5a done; `progress.md` T5 block updated with result summary.
- **Origin**: orx session `chat_66108501-3931-4f5e-a250-1c797d93e50b` (project d2b5f4c2, "LQG-Grassmannian Phases 4-5 completion"). Monitor job orx-t5a-monitor retired after this run.
<!-- project: github.com/space-cadet/lqg-scattering -->
