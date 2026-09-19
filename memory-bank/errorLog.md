# Error Log

## 2026-09-19 12:00 IST: T1 - Python Performance Limitation

**File:** `positivity.py`

**Error Message:**
```
MemoryError / excessive computation time for n>=5
```

**Cause:**
Fock space dimension grows combinatorially: dim = C(n+k-1, k). For n=4, dim ≈ 100. For n=5, dim ≈ 1000. For n=6, dim ≈ 10000. Python's dense matrix operations and interpreted loops cannot handle the sparse structure efficiently.

**Fix:**
Port to Rust with sparse matrices (sprs crate) and parallel iteration (rayon crate). See T3.

**Affected Files:**
- `rust/src/fock.rs`
- `rust/src/ops.rs`
- `rust/src/volume.rs`

**Related Task:** T3

---

## 2026-09-19 15:17 IST: T3c - ORX Agent Timeout Loop

**File:** `rust/src/volume.rs`

**Error Message:**
```
Agent stuck in computation loop, unresponsive to messages
```

**Cause:**
ORX agent hit a long-running Rust compilation or benchmark and could not process incoming messages. The agent's event loop blocks during tool execution.

**Fix:**
Sent explicit stop message. Agent acknowledged, committed WIP state (commit 42ce24e), and resumed with explicit task boundaries.

**Affected Files:**
- `rust/src/volume.rs`
- `rust/src/lib.rs`
- `rust/src/ops.rs`

**Related Task:** T3c

---

## 2026-09-19 15:55 IST: T3 - ORX/OpenCode No Context Compaction

**File:** ORX dashboard session

**Error Message:**
```
Context window at 185K/1M tokens — no compaction mechanism available
```

**Cause:**
Neither ORX nor OpenCode backend implements context compaction. The session will run until API error if context fills. This is a known limitation of the tooling.

**Fix:**
Monitoring context usage. Will manually start new session with resume prompt if needed. Long-term fix requires upstream patch to OpenResearch.

**Affected Files:**
- None (tooling limitation)

**Related Task:** T3 (all subtasks)
