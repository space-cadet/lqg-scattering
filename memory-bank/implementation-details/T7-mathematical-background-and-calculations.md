# T7: mathematical background and worked thermal-intertwiner calculation

*Created: 2026-10-06 12:28:49 IST*

This note derives the calculation implemented in `t7_geometry_thermal.py` and explains its physical scope. The numerical artifact is `t7_geometry_thermal_results.json`. The companion [findings note](T7-physical-thermal-intertwiners.md) gives the shorter interpretation. The starting manuscript is [Thermal Intertwiners](../../paper/thermal-intertwiners/thermal-intertwiners.tex).

The result is an audit of the manuscript's thermal state and a separate conditional candidate. It does not establish a unique thermal ensemble, a dynamical Hamiltonian of LQG, a classical-limit theorem, or a wormhole geometry.

## 1. Faces, oscillators, and physical state space

Assign two bosonic modes to each face $i=0,\ldots,N-1$:
$$
[a_i,a_j^\dagger]=[b_i,b_j^\dagger]=\delta_{ij},\qquad [a_i,b_j]=[a_i,b_j^\dagger]=0.
$$
Set $\hbar=1$ for spin algebra. The Schwinger generators are
$$
J_i^z=\frac12(a_i^\dagger a_i-b_i^\dagger b_i),\quad
J_i^+=a_i^\dagger b_i,\quad J_i^-=b_i^\dagger a_i.
$$
They obey $[J_i^z,J_i^\pm]=\pm J_i^\pm$ and $[J_i^+,J_i^-]=2J_i^z$. Define
$$
N_i=a_i^\dagger a_i+b_i^\dagger b_i,\qquad
j_i=N_i/2,\qquad \mathbf J_i^2=j_i(j_i+1).
$$
Thus a basis occupation $(n_{a_i},n_{b_i})$ has $j_i=(n_{a_i}+n_{b_i})/2$ and $m_i=(n_{a_i}-n_{b_i})/2$. A face is a leg of the intertwiner. The sum $J=\sum_i j_i$ is the FL spin-area label; total oscillator number is $K=2J$. These are distinct from an LQG area operator proportional to $\sum_i\sqrt{j_i(j_i+1)}$. The present output reports spin-area, without claiming either area normalization is the physical energy.

With $\mathbf G=\sum_i\mathbf J_i$, closure requires
$$
G^a|\psi\rangle=0\quad(a=x,y,z),\qquad
\langle\psi|\mathbf G^2|\psi\rangle=0.
$$
The equivalence follows because $\mathbf G^2=\sum_a(G^a)^\dagger G^a$ is positive. For fixed face spins the physical space is
$$
\mathcal H_{\{j_i\}}=\operatorname{Inv}_{SU(2)}\!\left(\bigotimes_i V_{j_i}\right).
$$
At fixed total $J$, sum over the allowed face-spin partitions. An odd total boson number cannot contain a singlet: the central $SU(2)$ element $-I$ acts as $(-1)^K$.

For $N=4$ the fixed-$J$ singlet-space dimension is
$$
d_4(J)=\frac{(J+1)(J+2)^2(J+3)}{12}.
$$
The fixed-area intertwiner representation has $U(4)$ highest weight $(J,J,0,0)$. Weyl's dimension product gives
$$
\prod_{1\le a<b\le4}\frac{\lambda_a-\lambda_b+b-a}{b-a}
=1\cdot\frac{J+2}{2}\cdot\frac{J+3}{3}\cdot(J+1)\cdot\frac{J+2}{2}\cdot1,
$$
which yields the displayed dimension. An independent finite-spin counting prescription couples faces 0,1 and 2,3. For each partition $\sum_i j_i=J$, count common intermediate spins in the two Clebsch–Gordan ranges; each common spin gives one singlet. The spectral code obtains dimensions $1,0,6,0,20,0,50$ at $K=0,\ldots,6$, consistent with the formula at integer $J=0,1,2,3$. These spaces include zero-area faces and degenerate configurations.

## 2. Closed input geometry and the FL seed

For outward classical face-area vectors $\mathbf A_i=A_i\mathbf n_i$, define fractions $f_i=A_i/\sum_jA_j$. A closed tetrahedron satisfies $\sum_i f_i\mathbf n_i=0$. Write a normalized spinor for its normal as
$$
\chi_i=\begin{pmatrix}\cos(\vartheta_i/2)\\e^{i\varphi_i}\sin(\vartheta_i/2)\end{pmatrix},\qquad
\chi_i^\dagger\boldsymbol\sigma\chi_i=\mathbf n_i.
$$
Use $z_i=\sqrt{2f_i}\chi_i$. Then
$$
\sum_i |z_i\rangle\langle z_i|=I_2,
$$
because each summand is $f_i(I+\mathbf n_i\cdot\boldsymbol\sigma)$.

The regular seed in the existing builder uses unit spinors with normals
$$
\frac1{\sqrt3}(1,1,1),\quad\frac1{\sqrt3}(1,-1,-1),\quad
\frac1{\sqrt3}(-1,1,-1),\quad\frac1{\sqrt3}(-1,-1,1).
$$
A common rescaling of all spinors rescales the unnormalized fixed-$J$ state only; normalization removes it. Thus this regular convention is equivalent to fractions $f_i=1/4$.

The unequal seed uses vertices $(0,0,0)$, $(1.3,0,0)$, $(0.2,0.9,0)$, $(0.25,0.15,0.8)$. For the face opposite vertex $i$, compute $\mathbf A_i=\tfrac12(\mathbf v_k-\mathbf v_j)\times(\mathbf v_l-\mathbf v_j)$ and flip its sign if necessary to point outward. The code checks weighted closure to $10^{-12}$.

Define the singlet pair creator and spinor determinant
$$
F_{ij}^\dagger=a_i^\dagger b_j^\dagger-a_j^\dagger b_i^\dagger,\qquad
[z_j,z_i]=z_j^0z_i^1-z_j^1z_i^0,
$$
$$
F_z^\dagger=\sum_{i<j}[z_j,z_i]F_{ij}^\dagger,\qquad
|J,z\rangle=\frac{(F_z^\dagger)^J|0\rangle}{\|(F_z^\dagger)^J|0\rangle\|}.
$$
The antisymmetric contraction commutes with global spin, $[G^a,F_{ij}^\dagger]=0$. The vacuum is a singlet; therefore this seed is a singlet for any spinor labels. Closed labels supply its intended geometric interpretation. The implementation applies the creation operators with their exact square-root occupation factors, accumulates amplitudes in a dictionary, then normalizes numerically. It does not rely on an analytic normalization convention.

Write the normalized result as $|J,z\rangle=\sum_{|n|=K_0}c_n|n\rangle$, $K_0=2J$. Finite-$J$ FL states superpose face-spin partitions and have fluctuations. A spinor-labelled quantum state is not a classical tetrahedron with perfectly sharp face areas and angles.

## 3. What the earlier Gibbs/TFD calculations compute

For an explicitly chosen Hamiltonian $H$,
$$
\rho_\beta=Z^{-1}e^{-\beta H},\qquad
|\mathrm{TFD}\rangle=Z^{-1/2}\sum_\alpha e^{-\beta E_\alpha/2}|\alpha\rangle_L|\bar\alpha\rangle_R.
$$
Tracing R gives $\rho_\beta$. In the old T7 oscillator controls, $H=\sum_iN_i$ on a capped full Fock space. Rotational invariance, $[H,G^a]=0$, does not impose singlet support: it leaves nonzero-total-spin sectors populated.

A physical Gibbs prescription would instead trace over a chosen singlet space, or use $P_0e^{-\beta H}P_0$ when the Hamiltonian preserves that space. At fixed $J$, $H=2J I$ gives $\rho_\beta=I/d_4(J)$, independent of temperature. To obtain nontrivial temperature dependence one must vary area or specify energy differences within the physical sector. Neither choice follows automatically from calling a state thermal.

The new pilot evaluates a squeezed geometric seed rather than this Gibbs state. Its reduced state is not assumed to equal $e^{-\beta H}/Z$.

## 4. Exact squeezing amplitudes

Flatten the $a,b$ face modes into $\mu=1,\ldots,M$, $M=2N=8$. The implemented draft operator is
$$
U(\theta)=\exp\!\left[\theta\sum_\mu(c_{\mu L}^\dagger c_{\mu R}^\dagger-c_{\mu L}c_{\mu R})\right],
\qquad \tanh^2\theta=x=e^{-\beta\omega}.
$$
Here $\omega=1$ and $k_B=1$. Start with $|\Psi_0\rangle=|J,z\rangle_L|0\rangle_R$ and form $|\Psi_\beta\rangle=U|\Psi_0\rangle$.

For one mode pair, let $K_+=c_L^\dagger c_R^\dagger$, $K_-=c_Lc_R$, $K_0=(N_L+N_R+1)/2$. The squeeze disentangles as
$$
U=e^{tK_+}e^{-2\log(\cosh\theta)K_0}e^{-tK_-},\qquad t=\tanh\theta.
$$
On $|n,0\rangle$ the last factor is identity. Expanding the first factor gives
$$
\frac{K_+^r}{r!}|n,0\rangle
=\sqrt{\frac{(n+r)!}{n!r!}}|n+r,r\rangle,
$$
so
$$
U|n,0\rangle=\sum_{r\ge0}\sqrt{\binom{n+r}{r}}\frac{t^r}{\cosh^{n+1}\theta}|n+r,r\rangle.
$$
Multiplying the commuting mode-pair factors gives the full exact amplitude
$$
C_{n+r,r}=c_n(1-x)^{(K_0+M)/2}x^{|r|/2}
\sqrt{\prod_\mu\binom{n_\mu+r_\mu}{r_\mu}}.
$$
For a fixed right occupation $r$, the left occupation determines $n$ uniquely. No interference terms between distinct seed occupations contribute to the norm at that fixed right occupation.

Let $\ell=|r|$. Each block has left/right boson totals $K_0+\ell$ and $\ell$. Strip off the common thermal factor and denote the remaining matrix by $B_\ell$. Using
$$
\prod_\mu\sum_{r_\mu\ge0}\binom{n_\mu+r_\mu}{r_\mu}y^{r_\mu}
=(1-y)^{-(K_0+M)},
$$
we obtain
$$
\|B_\ell\|_F^2=\binom{K_0+M+\ell-1}{\ell},\qquad
p_\ell=(1-x)^{K_0+M}x^\ell\binom{K_0+M+\ell-1}{\ell}.
$$
This is an exact negative-binomial pair-number distribution. Its mean is $(K_0+M)\bar n$, $\bar n=x/(1-x)$. Consequently the exact mean spin-areas are $J_L=J+(K_0+M)\bar n/2$ and $J_R=(K_0+M)\bar n/2$. The construction changes area.

## 5. Three different closure questions

### 5.1 Combined conjugate-copy closure

The right copy carries the conjugate representation: in a real occupation basis its Cartesian generators are $-G^{aT}$. The combined generator is
$$
\mathcal G^a=G_L^a\otimes I-I\otimes G_R^{aT}.
$$
The pair creator $\sum_\mu c_{\mu L}^\dagger c_{\mu R}^\dagger$ contracts a representation with its conjugate. It commutes with $\mathcal G^a$. The seed is annihilated by this combined generator, and therefore $\mathcal G^a|\Psi_\beta\rangle=0$.

For coefficient matrix $C$, this action is $G^a_LC-CG^a_R$. In ladder notation the computed squared residual is
$$
\|G_L^zC-CG_R^z\|_F^2+
\frac12\|G_L^+C-CG_R^+\|_F^2+
\frac12\|G_L^-C-CG_R^-\|_F^2.
$$
The minus-transpose right convention is essential. This constraint expresses joint invariance; it does not require independent singlets on L and R.

### 5.2 Ordinary closure on each copy: full derivation

Trace over the initially vacuum R modes. The left modes undergo an independent quantum-limited amplifier. Set $s=\bar n$, $g=1+s=\cosh^2\theta$. The Heisenberg relation is
$$
U^\dagger c_LU=\sqrt g\,c_L+\sqrt s\,c_R^\dagger.
$$
For one mode, conditional on input occupation $n$, the mean output number is $gn+s$ and its variance is $gs(n+1)$, obtained from the negative-binomial coefficients above. For a face's two modes, writing $N=N_i$, we therefore have
$$
\langle N'\rangle=g\langle N\rangle+2s,
$$
$$
\langle N'^2\rangle=g^2\langle N^2\rangle+5gs\langle N\rangle+4s^2+2gs.
$$
The second identity follows by adding conditional variance $gs(N+2)$ to conditional mean squared $(gN+2s)^2$ and then averaging over the input state.

Since $\mathbf J_i^2=N_i(N_i+2)/4$, substitution yields
$$
\langle\mathbf J_i'^2\rangle
=g^2\langle\mathbf J_i^2\rangle+
\frac34gs\langle N_i\rangle+\frac32gs.
$$
The amplifier maps each spin component's mean to $gJ_i^a$. Different faces have independent right-vacuum noise, so for $i\ne j$,
$$
\langle\mathbf J_i'\cdot\mathbf J_j'\rangle
=g^2\langle\mathbf J_i\cdot\mathbf J_j\rangle.
$$
Sum diagonal and off-diagonal terms:
$$
\langle\mathbf G_L^2\rangle
=g^2\langle\mathbf G_0^2\rangle+
\frac34gs\sum_i\langle N_i\rangle+\frac32Ngs.
$$
For the fixed-number singlet seed, $\mathbf G_0|\Psi_0\rangle=0$ and $\sum_iN_i=K_0$, hence
$$
\boxed{\langle\mathbf G_L^2\rangle=\frac34(K_0+2N)\bar n(1+\bar n).}
$$
Combined dual closure implies $\langle\mathbf G_R^2\rangle=\langle\mathbf G_L^2\rangle$, because the norms of corresponding left and transposed-right generator actions agree. The defect is positive at every finite temperature for this seed and uniform squeeze. It vanishes as $\beta\to\infty$.

The same calculation gives exact unprojected flux Gram entries: off-diagonal entries scale by $g^2$ and diagonal entries receive the displayed amplifier-noise correction. These identities concern the untruncated draft state, not the projected candidate.

### 5.3 Transformed closure

For $\widetilde G_L^a=UG_L^aU^\dagger$, $\widetilde G_L^a|\Psi_\beta\rangle=UG_L^a|\Psi_0\rangle=0$; similarly on R. This is the closure obtained by conjugating the constraint together with the state. It is compatible with failure of ordinary closure.

If volume is also defined by $\widetilde V=UVU^\dagger$, then
$$
\langle\Psi_\beta|\widetilde V|\Psi_\beta\rangle
=\langle\Psi_0|V|\Psi_0\rangle.
$$
Thus temperature dependence of ordinary volume and closure of transformed fluxes cannot be combined without explaining which geometric observables are intended. The right copy is a vacuum of transformed annihilation operators; its ordinary number expectation is nonzero.

## 6. Conditional projection onto independently closed copies

Construct the ordinary singlet projector $P_0$ spectrally from $\mathbf G^2$. Define
$$
|\Phi_\beta\rangle=
\frac{(P_{0,L}\otimes P_{0,R})|\Psi_\beta\rangle}{\sqrt{p_{00}}},\qquad
p_{00}=\|(P_{0,L}\otimes P_{0,R})|\Psi_\beta\rangle\|^2.
$$
The coefficient matrix becomes $C_{00}=P_{0,L}CP_{0,R}^T$. The transpose comes from the coefficient-matrix rule for an operator acting on the second ket, not from an additional convention about complex conjugation.

By construction, both ordinary Gauss constraints annihilate $|\Phi_\beta\rangle$. Since $K_0$ is even, odd $\ell$ gives odd boson number on both copies and is eliminated. Even-$\ell$ sectors survive selectively; this is more than removal of odd sectors.

This is postselection. It is not shown to be a unitary thermal operation, a Gibbs state, or the manuscript's original ket. No physical Hamiltonian or experimental realization of this conditioning has been assigned.

## 7. Finite-sector matrices and observables

The exact-total-number basis has dimension $\binom{K+7}{7}$. The largest left sector here is $K=8$, dimension 6435; the largest right sector is $\ell=4$, dimension 330. A coefficient matrix avoids storing operators on their full tensor-product space.

Group the basis by face counts $k_i=N_i$ and total $a$ occupation. These fix local spins and total magnetic number. In each block form
$$
D_{ij}=\mathbf J_i\cdot\mathbf J_j
=J_i^zJ_j^z+\tfrac12(J_i^+J_j^-+J_i^-J_j^+),
$$
$$
G^2=\sum_i\frac{k_i(k_i+2)}4 I+2\sum_{i<j}D_{ij}.
$$
Its zero eigenspace in the $M_z=0$ block gives $P_0$. Singlet eigenvalues are identified by absolute tolerance $10^{-10}$; other magnetic blocks have no singlet projector.

The repository's Hermitian signed triple operator is
$$
q_{ijk}=i[D_{ij},D_{jk}].
$$
For $q=W\operatorname{diag}(\lambda)W^\dagger$, compute
$$
\sqrt{|q|}=W\operatorname{diag}(\sqrt{|\lambda|})W^\dagger.
$$
Eigenvalues with $|\lambda|\le64\epsilon_{\rm mach}\max(1,\max|\lambda|)$ are set to zero before taking roots. This avoids spurious positive contributions from exact kernel modes.

The positive volumes used are
$$
V_{RS}=\gamma^{3/2}\sum_{i<j<k}\sqrt{|q_{ijk}|},\qquad
V_{AL}=\gamma^{3/2}\sqrt{\left|\sum_{i<j<k}\epsilon_{ijk}q_{ijk}\right|},
$$
with $\gamma=0.2375$, $\hbar=1$ and signs $(+1,-1,+1,-1)$ for triples $(012,013,023,123)$. These are project conventions; no classical-volume matching factors are applied in this pilot. In an independently closed four-face sector the triples are related by closure. RS/AL proportionality there is not independent physical confirmation.

For any left operator $O$, the unnormalized expectation is $\operatorname{Tr}(C^\dagger OC)$. Its second moment is $\|OC\|_F^2$ for Hermitian $O$. Divide by state norm to obtain normalized moments. Volume variance is $\langle V^2\rangle-\langle V\rangle^2$. A vanishing signed mean $\langle q\rangle$ does not imply a vanishing positive volume.

The face diagnostics are
$$
\langle j_i\rangle=\langle N_i/2\rangle,\qquad
\Gamma_{ij}=\langle\mathbf J_i\cdot\mathbf J_j\rangle,\qquad
R_{ij}=\frac{\Gamma_{ij}}{\sqrt{\Gamma_{ii}\Gamma_{jj}}}.
$$
$R_{ij}$ is a normalized quantum correlation, not an exact classical angle formula at finite $J$. Individual vector means vanish for singlets. The pilot records left face diagnostics, not a full set of two-sided geometric correlations or a reconstructed metric.

For normalized $C$, $\rho_L=CC^\dagger$. Its nonzero eigenvalues equal those of $C^\dagger C$. Different $\ell$ blocks are orthogonal in both copies, so their eigenvalue lists combine directly. Entropy is $S_L=-\sum_\alpha\lambda_\alpha\log\lambda_\alpha$, with natural logarithms. The implementation drops eigenvalues $\le10^{-14}$ from the entropy sum; it records no rigorous entropy error bound for this numerical threshold.

## 8. Cutoff, normalization, and error accounting

Retain $\ell\le L=4$. The raw retained norm is
$$
W_L=\sum_{\ell=0}^Lp_\ell,
$$
and the exact omitted raw probability is $\delta_L=1-W_L$. All reported raw expectations are normalized by $W_L$ and therefore belong to the retained state.

For projected blocks let $W_{00,L}$ be their retained, unnormalized weight relative to the original infinite squeezed state. This is the reported candidate `norm`; it is not the projection probability conditioned on raw retention. That latter probability would be $W_{00,L}/W_L$.

Projection is contractive, so its omitted weight $e$ obeys $0\le e\le\delta_L$. The omitted probability in the normalized infinite projected state is bounded by
$$
\frac{e}{W_{00,L}+e}\le\frac{\delta_L}{W_{00,L}+\delta_L}.
$$
The full projection probability lies between $W_{00,L}$ and $W_{00,L}+\delta_L$. Probability bounds alone do not bound unbounded volume moments or infinite-dimensional entropy. The artifact separately records differences between cutoffs 2 and 4 for raw closure/RS volume and candidate RS volume/entropy. No high-temperature extrapolation is made.

## 9. Worked results and verification

The calculation ran all combinations of two shapes, $J=1,2$, and $\beta=3,4,5,8$: 16 temperature rows. Zero-temperature seed controls were evaluated separately.

For regular $J=2$, $\beta=5$:

| Quantity | Value |
|---|---:|
| Exact ordinary Gauss defect on each copy | 0.0614670559217 |
| Retained raw left defect | 0.0614667783298 |
| Projected left defect | approximately $-2.76\times10^{-16}$ |
| Retained projected weight $W_{00,4}$ | 0.922702873707 |
| Seed RS volume | 0.0507755317061 |
| Candidate RS volume | 0.0508234370560 |
| Candidate entropy | 0.00675091984015 |
| Conditional omitted-probability bound | $6.18\times10^{-8}$ |
| Candidate RS change, cutoff 2 to 4 | $3.39\times10^{-8}$ |
| Candidate entropy change, cutoff 2 to 4 | $4.12\times10^{-6}$ |

A small negative closure expectation is numerical roundoff in a theoretically positive operator. For unequal-skew $J=2$ at the same temperature, seed RS volume is 0.0449586858972 and candidate RS volume is 0.0450057132833. These two examples retain different volume responses. Both $J=1$ seeds have zero positive seed volume; they are not useful examples of a sharply resolved nonzero classical tetrahedral volume.

For $J=2$, $\beta=3$, the projected omitted-probability bound is about 0.0014932 and the regular candidate RS cutoff difference is $9.59\times10^{-5}$. The warmer pilot is less converged.

Checks actually performed:

1. Compared the one-pair amplitudes with a separately exponentiated $40\times40$ squeeze generator at $\theta=0.2$, inputs $n=0,1,2,4$. Maximum difference: $1.67\times10^{-16}$. This is a finite-matrix check at small squeezing, not an arbitrary-temperature theorem.
2. Compared numerical singlet dimensions through total bosons 6 with $1,0,6,0,20,0,50$.
3. Checked each stripped pair-sector norm against $\binom{K_0+8+\ell-1}{\ell}$, absolute tolerance $10^{-8}$.
4. Checked each sector's combined dual residual below $10^{-20}\max(1,\|B_\ell\|_F^2)$. Maximum normalized combined residual across the temperature rows: $6.23\times10^{-32}$.
5. Checked normalized seed norm and closure to $10^{-12}$ and candidate per-copy closure to $10^{-10}$.
6. At $\beta\ge5$, compared retained raw closure with the exact infinite-state formula to absolute tolerance $10^{-5}\max(1,D_{\rm exact})$.
7. Compared all four seed RS/AL volumes with the existing implementation. Maximum difference: $1.04\times10^{-17}$. Both paths share the triple-action helper, so this checks sector assembly and normalization rather than independently verifying the triple convention.
8. Compared cutoffs 2 and 4 as described above; these are convergence diagnostics, not rigorous observable error bars.

## 10. Reproduction and remaining mathematical work

Run from the repository root with NumPy and SciPy available:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  /opt/homebrew/bin/python3 t7_geometry_thermal.py \
  --pair-cutoff 4 --betas 3 4 5 8 \
  --output t7_geometry_thermal_results.json > /tmp/t7-geometry-thermal.log 2>&1
```

The JSON records parameters, conventions, source HEAD, timestamps, diagnostics and results. Source HEAD identifies the Git baseline; the new uncommitted script itself is not identified by that commit. Preserve the script alongside the artifact for reproduction. The bundled runtime tried first lacked SciPy; the successful calculation used the Homebrew Python environment. Rust was not needed for this pilot.

The next mathematical decision is the intended physical state and observable pair. Ordinary fluxes require independently closed states; the manuscript's squeeze provides combined closure, while its conjugated observables provide transformed closure. Postselection supplies an explicit independently closed candidate, but its Gibbs interpretation remains unproved. A singlet-preserving operation or a Gibbs/TFD construction on the physical Hilbert space must specify its Hamiltonian, area ensemble and right-copy convention.

Subsequent work would derive the selected ensemble, test additional geometric states and cutoff values, investigate two-sided geometric correlations, and establish any claimed large-area or temperature limit. Neither the pilot nor this derivation proves those results. T9 now owns state definitions, construction, and geometric/physical study; this note records the work transferred from the former T7 umbrella. Completed T7a–T7e results remain valid for their documented Gibbs/oscillator scopes.

## Source map

- `coherent_states.py`: Schwinger ladder actions and occupation representation.
- `fl_volume_validation.py`: normalized FL seed, regular normals, spinor conversion and project conventions.
- `t5c_input_geometry_scan.py`: outward face-area vectors from vertices.
- `positivity.py`: flux dot products, signed triple action and positive RS/AL reference routines.
- `t7_geometry_thermal.py`: sector/projector assembly, exact squeezed coefficients, candidate projection, moments, entropy and validations.
- `t7_geometry_thermal_results.json`: numerical evidence for this note.
- `paper/thermal-intertwiners/thermal-intertwiners.tex`: manuscript background, thermal coherent-state proposal and appendices. Its interpretation is subject to the explicit constraint distinctions derived here.
