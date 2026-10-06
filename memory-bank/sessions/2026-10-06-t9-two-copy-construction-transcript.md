# T9 two-copy intertwiner construction and mathematics

Recorded 2026-10-06 20:52 IST. This transcript preserves the discussion that selected the two-copy FL construction and derived its pair-operator factorization. No numerical implementation or new calculations were run in this discussion. The selected state and full derivation are also recorded in [the mathematical-background note](../implementation-details/T7-mathematical-background-and-calculations.md#11-t9-follow-up-squeeze-two-conjugate-fl-intertwiners).

## Physical operators and the draft

**User:** What fluxes are you referring to?

**Assistant:** By fluxes I mean the face angular-momentum operators $\mathbf J_i$ in the Schwinger-boson construction, the quantum counterparts of outward face-area vectors. Closure is $\sum_i\mathbf J_i=0$. The distinction was between the ordinary operators and their conjugates by the squeeze, $\widetilde O=UOU^\dagger$.

**User:** Using transformed operators seems sensible. After tracing out one copy in the TFD, do we retain the same expectation values as for the single-copy state?

**Assistant:** For any operator acting only on the left, tracing out the right exactly preserves its expectation: $\operatorname{Tr}(\rho_L O_L)=\langle\Psi|O_L\otimes I_R|\Psi\rangle$. But $U(O_L\otimes I_R)U^\dagger$ generally acts on both copies, so it cannot generally be evaluated from $\rho_L$ alone. The earlier answer also distinguished the original FL expectation from a thermal reduced-state expectation.

**User:** Who calls the original FL state a “seed”? And should the TFD prescription differ from a state that is nontrivial in only one copy?

**Assistant:** The word “seed” was shorthand and was dropped. The draft starts from one FL intertwiner on the left and vacuum on the right, then applies the two-copy squeeze. This populates both original oscillator copies, but the draft's state is not automatically the canonical Gibbs purification for an excited FL state. A state built from two FL factors is a distinct construction.

**User:** Show what the draft does.

**Assistant:** The draft first defines the oscillator thermal vacuum $|0(\beta)\rangle=U_\beta|0,0\rangle$. It dresses the left FL pair creator by conjugation and acts with its $J$th power on that thermal vacuum. Algebraically,
$$
|J,\mathbf z\rangle_{\beta,L}
=U_\beta\bigl(|J,\mathbf z\rangle_L\otimes|0\rangle_R\bigr).
$$
The right copy is vacuum for the transformed right annihilation operators, not for the original right oscillators. The source is `paper/thermal-intertwiners/thermal-intertwiners.tex`, especially its TFD and “Coherent Thermal Intertwiners” sections.

## Prior literature and the project's target

The Kotecha discussion established relevant context, not a prescription for T9. Kotecha and Oriti's GFT Gibbs example weights geometric volume and particle number, $\rho\propto e^{-\beta(V-\mu N)}$; the later Assanioussi–Kotecha paper constructs thermal vacua in a doubled GFT representation and adds coherent configurations over that thermal vacuum. Sources consulted in the discussion: [arXiv:1801.09964](https://arxiv.org/abs/1801.09964) and [arXiv:1910.06889](https://arxiv.org/abs/1910.06889).

**User:** I am not trying to reproduce Kotecha or another prescription. My goal is to construct TFD states using intertwiners.

**Assistant:** A general TFD can be written from a complete orthonormal basis of physical intertwiner eigenstates of a chosen generator, paired with their conjugates and weighted by the generator's Boltzmann factors. This identifies the mathematical properties needed for a Gibbs TFD, but does not force that construction as the user's target.

**User:** What basis should be used?

**Assistant:** The recoupling basis is a useful four-face working basis: specify the face spins, couple faces 1 and 2 to intermediate spin $k$, couple faces 3 and 4 to the same $k$, and form a singlet. It is orthonormal and closed, while FL coherent states are useful geometric superpositions rather than an orthonormal basis. A thermal sum's defining basis would have to diagonalize the operator whose eigenvalues supply its weights.

**User:** For a holographic TFD parallel, what properties should basis states have?

**Assistant:** In the canonical form, states should form complete orthonormal energy eigenbases of two copies, each physical, with matched energies and conjugate pairing. Intertwiners satisfy separate closure. However, individual terms need not be classical geometries. Whether an FL-based squeezed state has Gibbs marginals or the canonical energy-basis form must be checked rather than assumed.

**User:** Check the physical motivation for doubling the face oscillators in the draft.

**Assistant:** The draft's motivation is to express thermal ensemble averages as pure-state expectations on an enlarged, doubled Hilbert space, while applying the familiar oscillator thermal construction to the existing Schwinger-boson description of each face. Its geometric motivation is to combine semiclassical coherent geometry with finite-temperature fluctuations. The equal face temperature assumption is tied to its gluing/equipartition argument. The later suggestion that inter-copy entanglement connects two geometries and describes a wormhole is an interpretation; the draft does not derive a metric connection or holographic correspondence.

## Selected two-copy FL state

**User:** What happens if we start with a vacuum product and act with thermal $F$ operators on both copies?

**Assistant:** Starting from the ordinary doubled vacuum and acting with conjugated pair creators is different from acting on the thermal vacuum: a residual $U_\beta^\dagger$ remains and does not cancel. Acting with the thermal pair creators on the thermal vacuum does cancel the adjacent unitaries and gives $U_\beta$ applied to an FL intertwiner on each copy.

**User:** Yes. That $\Psi_\beta$ is exactly what I want.

The selected state is
$$
|\Psi_0\rangle=|J,\mathbf z\rangle_L\otimes|\overline{J,\mathbf z}\rangle_R,
\qquad
|\Psi_\beta\rangle=U_\beta|\Psi_0\rangle.
$$
The right factor is the conjugate intertwiner in the dual copy. Use consistently transformed geometric observables. This is the T9 target construction; no claim has yet been established that its left reduction is a Gibbs state or that it is equivalent to a canonical energy-eigenbasis TFD.

**User:** I thought we were going to work through the math first.

**Assistant:** No files had been changed, and implementation stopped. The mathematical derivation was then worked through in discussion before this documentation update.

## Pair algebra and exact disentangling

For $N$ faces, introduce $2N$ paired oscillator modes only as compact notation: $c_{2i-1,X}=a_{iX}$ and $c_{2i,X}=b_{iX}$ for $X=L,R$. The symbol $c$ names no new oscillator. In original notation,
$$
K_+=\sum_{i=1}^N(a_{iL}^\dagger a_{iR}^\dagger+b_{iL}^\dagger b_{iR}^\dagger),\quad
K_-=K_+^\dagger=\sum_{i=1}^N(a_{iL}a_{iR}+b_{iL}b_{iR}),
$$
$$
K_0=\frac12\left[\sum_{i=1}^N(a_{iL}^\dagger a_{iL}+b_{iL}^\dagger b_{iL}+a_{iR}^\dagger a_{iR}+b_{iR}^\dagger b_{iR})+2N\right].
$$
The oscillator commutators imply $[K_0,K_\pm]=\pm K_\pm$ and $[K_+,K_-]=-2K_0$. Thus these are $\mathfrak{su}(1,1)$ generators, and
$$
U_\beta=e^{\theta(K_+-K_-)},\qquad \tanh\theta=e^{-\beta\hbar\omega/2}.
$$

To derive the ordered factorization, set
$$
U=e^{fK_+}e^{gK_0}e^{hK_-},\quad f(0)=g(0)=h(0)=0.
$$
The commutators give
$$
e^{fK_+}K_0e^{-fK_+}=K_0-fK_+,\quad
e^{fK_+}K_-e^{-fK_+}=K_--2fK_0+f^2K_+,\quad
e^{gK_0}K_-e^{-gK_0}=e^{-g}K_-.
$$
Differentiate the ansatz, form $U'U^{-1}$, and match coefficients with $K_+-K_-$:
$$
h'e^{-g}=-1,\quad g'-2fh'e^{-g}=0,\quad f'-fg'+f^2h'e^{-g}=1.
$$
The solution is $f=\tanh\theta$, $g=-2\log\cosh\theta$, $h=-\tanh\theta$, hence
$$
U_\beta=e^{tK_+}(\operatorname{sech}\theta)^{2K_0}e^{-tK_-},\qquad t=\tanh\theta.
$$

Each initial copy has $2J$ bosons. Therefore $K_-^s|\Psi_0\rangle=0$ for $s>2J$. The initial $K_0$ eigenvalue is $2J+N$, and after $s$ annihilations it is $2J+N-s$. The expansion is
$$
|\Psi_\beta\rangle=\sum_{s=0}^{2J}\sum_{r=0}^{\infty}
\frac{(-1)^st^{s+r}}{s!r!}(\operatorname{sech}\theta)^{4J+2N-2s}
K_+^rK_-^s|\Psi_0\rangle.
$$
For fixed net pair change $r-s$, amplitudes from different $r,s$ can contribute to the same final sector and must be combined coherently. $N_L-N_R$ commutes with $K_\pm$, so the two copies have equal total boson number throughout; their shared total area label fluctuates. As $\beta\to\infty$, $\theta\to0$ and the state returns to the conjugate FL product. Each transformed copy closure generator annihilates the state because the corresponding initial FL factor is closed. This does not imply closure under the original per-copy generators.

The derivation is mathematical work only. The reduced density matrix, its eigenvalues and entropy, two-sided geometry correlations, transformed volume observables, and any Gibbs characterization remain to be computed. Continue with the mathematics before implementation.
