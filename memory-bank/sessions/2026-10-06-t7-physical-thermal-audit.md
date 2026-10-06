# T7 physical thermal audit — 2026-10-06

User authorized the steps needed to move from oscillator controls to geometry-aware T7 numerics. Implemented the exact small-sector draft squeeze and independently closed conditional candidate. Four-face regular/unequal FL seeds at J=1,2 and beta=3,4,5,8 were tested with created-pair cutoff4 and comparison cutoff2. Ordinary per-copy closure fails for the draft; combined conjugate-copy closure passes. Double-singlet postselection restores ordinary closure but changes the state and is not established as Gibbs. Positive volumes, face correlations, entropy and truncation evidence are saved.

See [durable findings](../implementation-details/T7-physical-thermal-intertwiners.md), `t7_geometry_thermal.py`, and `t7_geometry_thermal_results.json`. Physical observable/ensemble selection remains open. Python handles this pilot; the manuscript, archived results and unrelated local changes were preserved. No commit or deployment performed.

Documentation follow-up, 12:28:49 IST: user requested the complete mathematical background and all calculation steps. Added `implementation-details/T7-mathematical-background-and-calculations.md`, linked from the findings and task record. Checked worked values against the saved artifact and equations against the implementation. No numerical code changed in this follow-up.


Task ownership follow-up, 2026-10-06 12:46:36 IST: an initial forward division made T7 the constructor and T9 the study owner; this interim split was superseded at 12:55 when the user consolidated the whole TFD program under T9. T7 was archived as transferred with work still open. T7a–T7e retain their completed records and IDs as T9’s exactly five child studies; new work stays at T9 parent level to respect the five-subtask cap. The inherited `tasks.md` T7a summary was corrected to say the old n=4,5 Gibbs calculation used unrestricted capped Fock spaces, not singlet intertwiner spaces.

Consolidation, 2026-10-06 12:55:19 IST: moved `tasks/T7.md` to `archive/T7.md` and marked it transferred rather than complete. T9 now owns construction and physical/geometric study; its five completed children retain identifiers T7a–T7e. Updated dependencies, task graph, registry, progress, changelog, cache, and technical-note ownership links. The older T7 IDs and filenames in numerical artifacts remain for provenance.
