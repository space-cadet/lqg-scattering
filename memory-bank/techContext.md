# Tech Context

*Last Updated: 2026-09-19 16:30 IST*

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Rust implementation | Rust (sprs, rayon, nalgebra) | Production numerical code for n≥5 |
| Python reference | Python 3 (NumPy, SciPy) | n=4 benchmark and validation |
| Agent orchestration | OpenResearch (ORX) + Kimi K3 | Autonomous implementation and testing |
| Version control | Git + GitHub | Source management |
| Memory bank | mb-core v6.12 | Project knowledge base |

## Rust Crate Structure

```
rust/
├── Cargo.toml
└── src/
    ├── main.rs          # Binary entry, benchmark scan loop
    ├── lib.rs           # Module re-exports
    ├── fock.rs          # Fock space basis (Schwinger bosons)
    ├── ops.rs           # Sparse u(N) operators (J_+, J_-, J_z)
    ├── coherent.rs      # U(N) Perelomov coherent states
    ├── volume.rs        # Volume operator (BHT triple-grasp)
    └── grassmannian.rs  # Plücker embedding, positivity tests
```

## Key Dependencies

| Crate | Version | Purpose |
|-------|---------|---------|
| sprs | latest | Sparse matrix operations (essential for large Fock spaces) |
| rayon | latest | Data-parallel iteration over basis states |
| nalgebra | latest | Dense linear algebra for small matrices |

## Python Reference Implementation

| File | Purpose |
|------|---------|
| `coherent_states.py` | U(N) coherent state construction |
| `positivity.py` | Positive Grassmannian cell tests |
| `manifold.py` | Geometric utilities |
| `rotation.py` | Rotation operators |

## Build and Run

```bash
cd rust
cargo build --release
cargo test --release          # Unit tests
cargo run --release -- scan   # Benchmark n=4..8
```

## Development Environment

- ORX agent session: chat_66108501 (running on port 4791)
- Model: kimi/k3-agent
- Workspace: ORX-managed git worktree

## Constraints

- Fock space dimension grows combinatorially: dim = C(n+k-1, k) for k bosons
- n=4: manageable in Python; n≥5 requires sparse matrices and parallelism
- All numerical claims must pass red-team protocol before reporting
