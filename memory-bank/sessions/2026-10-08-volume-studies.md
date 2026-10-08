---
source_branch: main
source_commit: 8a3919f9ad509e7cf164cb7953ef9cf922abf9c2
---

# Session summary: closed-state volume studies
*Recorded: 2026-10-08 23:21:44 IST*

## Context and thermal closure
The session began by reviewing T9 while the preceding chat completed its Memory Bank update. T9's four-face initial-area-one occupation/spin distribution was already calculated in the preceding session by two methods through $q=160$; this session did not rerun that thermal calculation. Full reduced-state blocks, entropy and thermal geometry remain open.

We distinguished ordinary closure of each copy from combined dual-copy closure. The selected two-copy squeezed FL construction preserves the latter but does not generally make each ordinary copy a singlet. Closed-polyhedron volume in each copy requires the corresponding closure constraint. Double-singlet conditional projection was discussed as a possible construction, not implemented or identified with a Gibbs state. Conjugating both state and observable by the same unitary preserves the corresponding expectation. A zero-temperature single-copy FL intertwiner provides a closed baseline.

## Existing studies and lowest-area physics
Reviewed pre-existing positive RS/AL FL calculations: the regular-tetrahedron area sweep through historical $J=5$, the 440-point equal-face-area shape scan at historical $J=2$, regular and unequal-skew weighted inputs through historical $J=7$, and existing flat-boundary probes. Finite-grid minima are not global proofs. Four-valent closure explains agreement after the fixed geometric factors; this does not independently validate physical normalization or establish either classical limit.

Schwinger occupations obey $j_i=(n_{a_i}+n_{b_i})/2$ and $m_i=(n_{a_i}-n_{b_i})/2$. Four faces each with occupations $(1,1)$ have total area 4, not 2. Four active faces at area 2 have spins $(1/2,1/2,1/2,1/2)$ and two singlet recoupling channels. If zero-spin faces are admitted, the full four-slot area-two space has 19 spin assignments and 20 basis vectors. Different FL shapes change their weights across assignments; positive volume must be evaluated spectrally, not as the square root of the absolute signed mean. In the two-dimensional four-half block, positive volume is scalar, while blocks with fewer than four active faces have zero volume.

## Notation and state spaces
The user adopted $K=\sum_i j_i=N_{\mathrm{bosons}/2$ for total linear area and $J$ for resultant angular momentum. All new enumeration/volume files use this convention; earlier thermal sections retain historical $J$-area/$S$-spin notation with an explicit mapping in the new section. No global notation migration was performed.

$\Omega_N(K)$ comprises normalized closed pure states at area $K$. An orthonormal basis has a finite dimension; arbitrary normalized superpositions form a continuous set. Face-spin assignments, individual basis states, volume eigenstates and whole fixed-area spaces are distinct objects. A fixed-area maximally mixed state uses $P_K/d_N(K)$ and yields $\operatorname{Tr}V/d_N(K)$, whereas a Hamiltonian proportional to area allows area fluctuations in a canonical ensemble. No new thermal Hamiltonian was adopted.

## Enumeration and complete four-face volume evaluation
Created `code/python/enumerate_closed_basis.py` to enumerate labelled four-face singlets at $K=2,3,4$ with zero-spin faces allowed. Saved 175 rows under `results/closed-state-enumeration/`. Dimensions are 20, 50 and 105; the all-active dimensions are 2, 16 and 51. Basis labels are $(j_1,j_2,j_3,j_4;k)$, obtained by coupling pairs to the same intermediate $k$ and then to $J=0$ using Condon–Shortley phases.

With user authorization, created `code/python/closed_basis_volume.py`, reusing existing oscillator operators and independent local-spin checks. Completed $K=2$ through 12, totaling 10,549 basis states. The user stopped the extension during $K=13$ archive verification; its partial archive was removed and no $K=13$ result is accepted. The largest physical singlet matrix is $7\times7$ at $K=12$. The $K=12$ compressed archive is approximately 2.5 MB.

| $K$ | Basis dimension | Basis states with positive volume expectation |
|---:|---:|---:|
| 2 | 20 | 2 |
| 3 | 50 | 12 |
| 4 | 105 | 39 |
| 5 | 196 | 94 |
| 6 | 336 | 190 |
| 7 | 540 | 342 |
| 8 | 825 | 567 |
| 9 | 1210 | 884 |
| 10 | 1716 | 1314 |
| 11 | 2366 | 1880 |
| 12 | 3185 | 2607 |

Positive-expectation counts depend on the declared tolerance and do not count nonzero eigenvalues. At $K=2$, the two four-half basis states have raw RS expectation 0.304653190236 and AL expectation 0.152326595118, with zero volume fluctuation; the other 18 states have zero volume.

Saved each area's CSV rows, metadata and compressed NPZ operators under `results/closed-basis-volume/`. Archives retain six singlet dot products, four signed triple operators, positive RS/AL operators and squares, eigensystems, CSR recoupling transforms, occupation labels and intermediate-spin labels. Storage is lossless and does not require pickle. Individual vector flux operators leave the singlet subspace, so a zero singlet-projected vector is not advertised as the full spin operator. Cache the loaded archive arrays for repeated access to avoid repeated decompression.

## Numerical evidence and limits
Checks cover exact dimensions, orthonormality, closure/Casimir, recoupling, Hermiticity, singlet invariance, four-valent triple identities, positive variances and archive reloads. Every unordered spin pattern uses an independent sparse local-spin triple contraction. Through $K=4$, full tensor-product triples and the original project triple routine were also compared. Recorded residuals remain below $8\times10^{-14}$ against an absolute tolerance $2\times10^{-10}$. Spectral zeros use $64\epsilon_{\mathrm{mach}}\max(1,\rho(|Q|))$.

Enumeration is exact and complete in finite area support; spectral evaluation is floating point. Raw units use $\gamma=0.2375$, $\hbar=1$, and AL signs $(+,-,+,-)$ in the four-face triple order. Geometric comparison factors are $\sqrt2/12$ for RS and $\sqrt2/6$ for AL; absolute physical regularization remains open. This is one copy at zero temperature, not a new finite-temperature volume result or a semiclassical-limit proof.

## Note and figures
Expanded `notes/thermal-area-sectors.md` with pedagogical preliminaries, smoother transitions and a linked table of contents. Added the occupation/closure discussion, positive-volume definitions, the area-two example, existing numerical comparisons, the possible thermal projection bridge, and a complete closed-state calculation section (anchor `section-03-05`).

Created `code/python/plot_single_copy_volume.py` to plot existing saved FL data without rerunning its physics. Embedded regular-area and weighted-area volume figures from `figures/single-copy-volume/`. Created `code/python/plot_closed_basis_volume.py` and embedded basis means/fluctuations at $K=2,3,4$ plus fixed-area ensemble volume curves through $K=12$ from `figures/closed-basis-volume/`. Exports include 300-dpi PNG, vector PDF and source-hash summaries. Arrays were checked and figures visually inspected. Ensemble curves do not represent one chosen classical shape.

## Large-area counting and variable face number
Explained the exact fixed-$N$ dimension

$$
d_N(K)=\frac{1}{K+1}\binom{K+N-1}{K}\binom{K+N-2}{K},\qquad
d_4(K)=\frac{(K+1)(K+2)^2(K+3)}{12}.
$$

At fixed $N$, $d_N(K)\sim K^{2N-4}/[(N-1)!(N-2)!]$. Stirling's approximation $n!\sim\sqrt{2\pi n}(n/e)^n$ and its logarithmic form were explained. These asymptotics keep $N$ fixed and do not justify replacing the variable-$N$ count by the same polynomial.

The user then clarified the target: catalogue closed volume states at fixed $K$ across any active $N$. Omitting $j_i=0$ ensures $N\leq2K$. A volume-capable catalogue sums $N=4,\ldots,2K$, retaining zero-volume states until an explicit operator separates its kernel. For labelled active faces, inclusion–exclusion gives exact dimensions 2, 36 and 347 at $K=2,3,4$. These are not volume-spectrum counts. Unlabelled counting requires a specified permutation prescription; division by $N!$ is insufficient. Above four faces, AL requires explicit graph orientation data.

## Deferred work and handoff
Created [T10](../tasks/T10.md) at the user's request for a later-session complete variable-$N$ enumeration and volume-spectrum study. Start with all $N$ at $K=2,3,4$, retain analytic integer checks, generalize the four-face driver, and distinguish RS evaluation from AL embedding requirements. No variable-$N$ volume spectra were computed here. T1a remains in progress for its broader volume-validation scope; T9 retains the uncomputed thermal reduced-state and geometry work.

The [physics-only transcript](2026-10-08-volume-physics-transcript.md) preserves the actual dialogue. This summary records the entire session's physics, implementation, evidence and deferred work. Closeout used chat-summary, mem-scan, mem-update and commit-message as requested. Source baseline was `main` at `8a3919f9ad509e7cf164cb7953ef9cf922abf9c2`; commit and push results are reported in chat after execution.
