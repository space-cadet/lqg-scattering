# System Patterns

*Last Updated: 2026-09-19 16:30 IST*

## Design Patterns and Conventions

### Numerical Computing
- **Sparse matrices are mandatory** for Fock spaces above n=4 — dense matrices exhaust memory
- **Checkpointable and resumable** — any computation >10 minutes must write incremental results and support `--resume`
- **Red-team protocol** — all numerical claims must pass 5-gate validation before being reported or committed
- **Cross-implementation verification** — Rust results must match Python at n=4 to f64 machine precision

### Code Organization
- **Published paper is frozen** — `paper/lqg-amplituhedron.tex` must not be modified
- **Rust is the production implementation** — Python is reference/benchmark only
- **Sparse-first design** — all operators use sprs::CsMat, dense only for small test matrices
- **Parallel by default** — rayon for basis state iteration and matrix construction

### Naming Conventions
- `[TEST]` prefix for runs with <500K sweeps to distinguish from production
- Task IDs: T{number} for major tasks, T{number}{letter} for subtasks (T3a, T3b, etc.)
- Rust modules: snake_case matching physics concept (fock.rs, coherent.rs, volume.rs)

### Testing Strategy
- Unit tests in each Rust module (`#[cfg(test)]`)
- n=4 is the critical benchmark — must match Python exactly
- Integration test: `cargo test --release` runs all tests including cross-validation

### Version Control
- All work committed to git before ORX session ends
- GitHub: https://github.com/space-cadet/lqg-scattering

#### Repository topology (dual-checkout, one remote)
There is **one** canonical remote — `github.com/space-cadet/lqg-scattering.git` — checked out in two local places with distinct roles. Do not treat either as a second source of truth; the remote is the single source of truth.

| Checkout | Path | Branch | Role |
|----------|------|--------|------|
| **Canonical repo** | `~/.openclaw/workspace/code/lqg-scattering` | `main` | Holds the **memory-bank** + dashboard + published manuscript. This is where durable records and the task registry live. |
| **ORX worktree** | `~/.local/share/openresearch/worktrees/…/chat_66108501…` | `main-orx` | ORX agent's isolated experiment/development branch. Scratch space; **not** the canonical record. |

**Sync discipline ("copy" workflow):**
- ORX works on its own branch `main-orx` and pushes to the same remote. Its worktree is private to its chat session.
- Periodically (after each experiment batch), the results are **merged `main-orx` → `main`** in the canonical repo, and `main` is pushed.
- The memory-bank lives **only** in the canonical repo (`code/lqg-scattering`), on `main`.
- **Do not** edit the ORX worktree directly from the canonical side, and do not let the two diverge without a merge — sync `main-orx` into `main` regularly so the memory-bank stays truthful.
- First sync done 2026-09-19 (merge `a24dac8`).

## Anti-Patterns to Avoid
- Dense matrices for large Fock spaces (memory explosion)
- Modifying the published paper
- Reporting numerical results without red-team validation
- Python for n≥5 computations (too slow)
