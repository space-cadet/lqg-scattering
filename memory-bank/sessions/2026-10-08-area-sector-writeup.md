# T9 area sectors, thermal coefficients, and source organization

*Recorded: 2026-10-08 10:31:19 IST*

## Research note and preserved discussion

The T9 discussion was written up in [`notes/thermal-area-sectors.md`](../../notes/thermal-area-sectors.md). A separate reconstructed transcript, [`2026-10-08-thermal-area-coefficients-transcript.md`](2026-10-08-thermal-area-coefficients-transcript.md), ends immediately before the user's “Good. So let's write all this up” request, as requested. It covers the coefficient expansion, density matrices, occupation sectors, cutoff question, and why multiplicity can make the sector curve peak.

For the selected two-copy squeeze, the note distinguishes individual occupation-basis amplitudes from the probability of a whole final-area sector. Coherent contributions to a fixed sector must be combined before forming $C_qC_q^\dagger$; tracing the right copy removes cross-sector terms because different right total occupations are orthogonal. The $J=0$, four-face oscillator vacuum is an exact illustration, not an approximation to the nonzero-$J$ FL coefficients.

The plot uses $p_q=(1-e^{-b})^8\binom{q+7}{7}e^{-bq}$ and shows the coefficient, multiplicity-weighted sector probability, and cutoff tail. Source is [`code/thermal/plot_vacuum_coefficients.py`](../../code/thermal/plot_vacuum_coefficients.py); pinned dependencies are in `code/thermal/requirements.txt`. The outputs are in `figures/thermal-area-sectors/`. For the tested $b=2,1,0.5,0.25$, the smallest cutoffs with omitted probability at most $10^{-6}$ are $11,26,55,113$. The script checks normalization, the mean, monotone tails, and cutoff minimality.

One conclusion follows without computing the excited-state coefficients. For fixed positive $H_A=\lambda N_L/2$ on unrestricted Fock space, the Gibbs family tends to the $q=0$ vacuum as $\beta\to\infty$; the selected squeeze tends to its initial nonzero-$J$ FL pair. That area Gibbs family therefore cannot equal the selected family at all temperatures. Other supports or Hamiltonians require separate specification.

## Code organization

Project source code is now grouped under `code/`: Python calculations, the Rust crate, the dashboard, Memory Bank parsers/viewer, shell workflows, thermal plot code, and LaTeX sources/build assets. Compiled PDFs remain under `paper/`; research notes, task specifications, and the paper overview are organized under `notes/`; calculation records are in `results/`, figures remain under `figures/`, and Memory Bank records remain under `memory-bank/`. The dashboard files were flattened to `code/dashboard/` so scripts and documentation resolve the same paths. Root and component READMEs, active Memory Bank references, and moved path helpers were updated for the new layout. Historical session/edit records were preserved.

## Remaining T9 work

Calculate the nonzero-$J$ squeeze coefficients in each final occupation sector, including coherent interference, then construct the sector reduced density matrices and compute their spectra and entropies. Evaluate geometric and two-sided observables with declared cutoffs. Compare with explicitly specified ensembles, respecting the low-temperature exclusion above.

## Session close: nonzero angular momentum

*Recorded: 2026-10-08 13:20:48 IST*

The later discussion distinguished the area label $J$ from resultant spin $S$ and magnetic number $M$, reviewed which squeeze and face-ladder operators change them, and derived a candidate fixed-$J,S,M$ $U(N)$ reference-state family. It also clarified that $\widehat U(u)$ represents one chosen $U(N)$ transformation, while Haar group averaging projects onto the $SU(2)$ singlet sector. The proposed nonzero-spin extension remains unverified. See the [session handoff](2026-10-08-physics-handoff.md) and [physics transcript](2026-10-08-physics-transcript.md).
