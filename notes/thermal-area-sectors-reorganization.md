# Reorganizing the thermal area-sector note

*Reviewed: October 14, 2026. This assessment guided the subsequently completed main-text/appendix rewrite; its proposals and extraction-stage findings are preserved below.*

## What the note should explain

The remaining note has one central physical question: what state does the two-copy squeeze produce from closed FL inputs, and what can its occupation and spin distributions tell us about geometry and temperature?

A coherent account should first define the state, then explain the observables and constraints, solve the vacuum control, and finally present the excited-input result. Single-copy volume catalogues, derivation machinery, numerical protocols and discussion chronology interrupt that progression. Their evidence should remain accessible, but they need not all be part of the main argument.

The later physical development now has its own home: [Heating closed quantum geometry: equilibrium and singlet exchange](thermal-geometry-and-singlet-exchange.md). It contains the ordinary-closure sweep, separate projection and area/volume growth, the fixed-Gibbs obstruction, many-body connections, and the implemented exchange model with all four related figures. The remaining area-sector note should lead into that document rather than reproduce it.

## Basic physical insights and results to retain

### 1. Fixed area does not fix shape or face occupations

An FL state has fixed total linear area but coherently mixes face-spin assignments. Spinor labels prescribe mean face-area proportions and correlations; they do not prescribe one definite occupation vector. Gauge invariance makes single-face vector means vanish, so geometric shape information is carried by flux correlations rather than those means.

Keep one short example and the FL state formula. Move exhaustive spin assignments and volume-block enumeration out of the main text. State once that linear FL area $A=\sum_i j_i$ differs from standard LQG area proportional to $\sum_i\sqrt{j_i(j_i+1)}$.

### 2. The selected squeeze is a preparation map, whose Gibbs character must be tested

The selected input is a conjugate pair of closed FL states, not the earlier one-sided FL/vacuum input. At zero squeeze it returns to that product. The doubled state is pure and each marginal generally becomes mixed.

An orthonormal energy-basis canonical TFD and a squeezed coherent-state preparation are different constructions. Keep that distinction near the definition of the state, including its support and right-copy convention. The low-temperature return to a nonvacuum FL input excludes the unrestricted positive oscillator-number/linear-area Hamiltonian as its Gibbs generator; it does not exclude every possible Hamiltonian for the unprojected excited family. The stronger projected-reference obstruction belongs in the extracted note.

### 3. Equal copy occupations do not mean fixed copy occupation

The same-mode squeeze preserves the occupation difference $N_L-N_R$. It can create or annihilate matched excitations, changing their sum. A finite initial FL state therefore develops unbounded final occupation support at finite temperature. Annihilation on the input terminates; creation does not.

Keep the conservation statement and one oscillator example. Move the full ordered expansion and factorial coefficient sums to Appendix A. Temperature changes weights, not a hard maximum accessible occupation.

### 4. Combined, transformed and separate ordinary closure are distinct

The squeezed state obeys combined dual-copy closure and consistently transformed per-copy closure. It generally fails separate ordinary closure. Rotational invariance or zero mean total flux does not establish singlet support; the positive Casimir detects nonzero resultant-spin sectors.

Keep the three constraint definitions together, followed by one two-spin illustration. Introduce the right-copy magnetic sign there, rather than returning to it in a separate long discussion. Simultaneously conjugating state and observable leaves the expectation unchanged; transformed geometry is therefore not the same measurement as the temperature-dependent ordinary geometry.

### 5. The vacuum is an exact Gibbs control, and its sector peak comes from multiplicity

For four faces, the vacuum reduced state is exactly Gibbsian for $H=\hbar\omega N_L$ on the full eight-mode Fock space. Its occupation law is

$$
p_q=(1-e^{-b})^8\binom{q+7}{7}e^{-bq},\qquad
\langle q\rangle=\frac8{e^b-1}.
$$

The peak of a sector distribution is caused by competition between increasing multiplicity and decreasing individual-state weight. The multiplicity counts oscillator states, not closed intertwiners. This is a genuine physical explanation and should remain in the main text, with the vacuum figure. Detailed cutoff tables belong in the numerical appendix.

### 6. Ordinary spin is distributed even when the doubled state closes

For the vacuum, the normalized reduced state within an occupation sector is uniform. Its conditional spin probabilities depend on occupation but not temperature; temperature reweights occupation sectors. Nonzero occupation has positive mean closure Casimir, even though singlet components exist at even occupations.

Keep the spin figure and the simple $q=2$ example: singlet probability $1/6$ and spin-one probability $5/6$. Move the magnetic-counting derivation, Weyl dimensions and direct eigenspectrum checks to Appendix B. This explains why a thermal oscillator state is not automatically an ensemble of separately closed polyhedra.

### 7. Excited FL inputs change the weights through coherent interference

For the four-face initial-area-one reference, the coefficient matrix includes creation and annihilation contributions which must be combined before squaring. Vacuum multiplicity counting alone cannot reproduce its distribution. The conditional spin weights now depend on temperature, and

$$
\langle q\rangle=2+\frac{12}{e^b-1}.
$$

The two independently organized spin-resolution methods agree, with additional direct oscillator checks of their shared coefficients. The main text should present the physical contrast with the vacuum, one compact result table and the two excited-input figures. Put both complete algorithms and their occupation-moment formulas in Appendix C.

### 8. Finite-temperature support and geometric information have precise limits

Every kinematically allowed $(q,S)$ has positive weight for this excited reference at finite positive temperature. The bounds $S\le q/2$ and spin parity are exact; a plot floor or occupation cutoff is a display/numerical choice. Keep this result beside the joint-distribution figure. Its short positivity proof can remain there; longer convergence estimates belong in Appendix D.

Occupation and spin probabilities do not determine the entire reduced state or its shape. They fix occupation/spin moments and singlet fractions, but do not by themselves give the full entanglement spectrum or arbitrary volume and face correlations. The paired $U(N)$ symmetry makes these global occupation/spin results common to the coherent orbit at fixed input area under uniform squeezing; face-specific geometry and volume need separate treatment. Keep this useful scope statement rather than burying it in a future-work list.

## Proposed main-text sequence

1. **The physical question and the chosen state.** Brief motivation; closed FL input, conjugate second copy, squeeze parameter, and canonical TFD comparison.
2. **Area, spin and observables.** One notation table, fixed area versus shape, the reduced state, and what occupation-sector probabilities determine.
3. **What squeezing preserves and what it changes.** Occupation difference, combined closure, ordinary versus transformed measurements, and infinite occupation support.
4. **The vacuum control.** Exact Gibbs state, multiplicity peak and conditional spin distribution; two existing figures.
5. **The excited FL reference.** Coherent interference, occupation/spin results, temperature dependence and exact support; two existing figures.
6. **Physical interpretation and remaining questions.** Global symmetry, limits of marginal data, and a short transition to the extracted heating/equilibrium/exchange note.

This order puts each result after the definitions needed to understand it. It avoids beginning with a long single-copy catalogue or using numerical algorithms as the principal section headings.

## Material for appendices or other documents

| Current material | Proposed destination | Keep in the main argument |
|---|---|---|
| Occupation normalization, $SU(1,1)$ disentangling, factorial sector sums | Appendix A: state coefficients | State definition, coherent interference and conservation laws |
| Magnetic counts, spin multiplicities, Weyl-dimension checks and dual-right details | Appendix B: spin resolution and representations | Three closure definitions, conditional spin result and one sign convention |
| Excited-reference coefficient polynomial, group-spin sums and occupation moments | Appendix C: the initial-area-one calculation | Excited-input physical contrast, mean occupation and plotted distributions |
| Cutoffs, omitted probability/moment bounds, numerical tolerances, version/source hashes and reproduction commands | Appendix D: verification and convergence; link result reports | One evidence paragraph, exact support and claim limits |
| Full single-copy volume scans, normalization factors, closed-basis catalogue and its four figures | Existing volume-studies note or a dedicated linked volume appendix | Positive volume is not a signed-mean proxy; area alone does not determine it |
| The $K=2$ scalar-volume-block explanation | Linked volume appendix | A short warning that volume does not resolve all shape information |
| Proposed nonzero-resultant-spin coherent family and compensating extra leg | Appendix E: exploratory extension, clearly marked unimplemented | A link if needed to explain open components |
| Historical proposed-calculation program | Session records; replace in research note with a current status table | Only the presently open questions |
| Discussion chronology, per-section dates and agent attributions | Appendix F or existing session records | One provenance statement with links |

Analytic derivations are not disposable numerical details. They should remain fully available in mathematical appendices; the main text should retain the equations which carry the physical argument. Test counts and source hashes belong with reproducibility evidence rather than serving as substitutes for the argument.

## Concrete inconsistencies and editorial repairs

- **Mixed notation:** initial area called $J$, later $K$, while $J$ is also reassigned to resultant spin. Adopt $K_{\rm in}$ for input linear area, $q$ for occupation, $A=q/2$ for final linear area, $S,M$ for resultant spin and magnetic component, and reserve $K_0,K_\pm$ for squeeze generators. Include an explicit mapping to historical formulas and saved files.
- **Potential symbol collisions:** $A$ is also a creation operator in the opening discussion and pair occupation in the coefficient polynomial. Use a named preparation operator and $n_{12}$ for the latter when rewriting. The parameter $t=e^{-b/2}$ also conflicts with dynamical time in the extracted exchange work; use a squeeze symbol such as $\tau$ consistently in a future rewrite, with a notation map.
- **Outdated status:** the October 8 proposal list still asks for already completed occupation/spin and projection calculations. Replace it with a dated status table separating completed reference studies from open full reduced spectra, other inputs and reservoir work. Historical wording belongs in the session record.
- **Misleading generality:** vacuum formulas, initial-area-one reference results, the selected FL orbit and arbitrary geometric observables need separate scope statements. Do not turn a checked reference or finite-range plot into a general geometric theorem.
- **Interruptions:** the long volume catalogue precedes the squeeze definition, and the exploratory nonzero-spin family interrupts the vacuum-to-excited comparison. Move both to the destinations above.
- **Repeated explanations:** consolidate fixed versus individual area, ordinary versus transformed closure, unbounded occupation, and the Gibbs caveat at their first logical use.
- **Navigation:** section numbering jumps from 12 to 16 and 17 and back to 13. The extraction removes that jump from the substantive text; a later rewrite should generate a thematic contents list while preserving legacy anchors.
- **Verified transcription error:** the general coefficient formula had a missing denominator brace in its fraction. This extraction repaired it to match the immediately preceding ordered expansion; no numerical formula or code was changed.

## What was changed now

The requested sections have been physically moved to the new illustrated note. The previous manuscript work and this session's exchange Hamiltonian, FL choices, comparisons, results and verification have been included. The old note retains short legacy-anchor redirects, so historical links continue to resolve, and current navigation links point to the new document. Three directly verified stale statements and the malformed fraction were corrected.

At the extraction stage the remaining note had been assessed but not yet rewritten. Following the user's subsequent authorization, the main-text/appendix rewrite is now complete: six narrative sections, seven appendices, all eight retained figures and all legacy anchors. The main text uses consistent notation with a mapping to the unchanged historical formulas and data. Scientific code, saved numerical arrays and figure assets were not changed.
