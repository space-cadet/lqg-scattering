# Memory Bank Project

*Initialized: 2026-19-09 16:09:50 GMT+5:30*

## Overview

This directory contains your Memory Bank - a system for maintaining project knowledge, tracking tasks, and preserving context across work sessions.

## Getting Started

### 1. Update Core Files

**projectbrief.md** - Project overview
- Project name and description
- Core objectives
- Key constraints or requirements
- Success metrics

**tasks.md** - Task registry
- Create entries for planned tasks
- Use format: Task ID, title, status, priority
- Update as work progresses

**.cursorrules** - Development guidelines
- Project coding standards
- Architecture patterns
- Technology stack details
- Important conventions

### 2. Database Setup (if using database features)

After initializing the memory bank, set up the database:

```bash
cd memory-bank/database
pnpm install
./run-all.sh
node query.js stats
```

### 3. File Structure Reference

```
memory-bank/
├── README.md              # This file
├── activeContext.md       # Current task context
├── changelog.md           # Project changes
├── edit_history.md        # File modification log
├── errorLog.md            # Error tracking
├── progress.md            # Implementation status
├── projectbrief.md        # Project overview
├── session_cache.md       # Session tracking
├── tasks.md               # Task registry
├── techContext.md         # Technical details
├── .cursorrules           # Development guidelines
├── tasks/                 # Individual task files
├── sessions/              # Session records
├── templates/             # File templates
├── database/              # Database and parser scripts
├── implementation-details/ # Technical notes
└── archive/               # Completed/archived items
```

### Implementation details and shared mathematics

Numerical specifications and shared definitions live in
implementation-details/. Start with
[volume numerical preliminaries](implementation-details/volume-numerical-preliminaries.md)
for common symbols and volume conventions, then follow its links to the
task-specific calculation, implementation, verification, and evidence notes.
The T5 program overview is
[volume-positivity-studies.md](implementation-details/volume-positivity-studies.md);
the detailed T5c specification is
[T5c-flux-covariance-volume-comparison.md](implementation-details/T5c-flux-covariance-volume-comparison.md).
Run logs preserve calculation evidence and provenance rather than serving as
the theory reference.

### 4. Working with the Memory Bank

When using with an AI assistant:

1. Reference memory bank files in prompts
2. Request specific sections when needed
3. Update files after completing work
4. Maintain activeContext.md and session_cache.md

### 5. Next Steps

1. Fill in **projectbrief.md** with your project details
2. Add your first tasks to **tasks.md**
3. Define development standards in **.cursorrules**
4. If using database: `cd memory-bank/database && pnpm install && ./run-all.sh`
5. Start working and update context files as you progress
