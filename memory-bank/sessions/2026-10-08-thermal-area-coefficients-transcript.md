# Session transcript: thermal area sectors and coefficients

Recorded 2026-10-08. This reconstructed transcript preserves the discussion from the request to revisit the two-copy construction through the assistant's response explaining why sector multiplicity causes peaks in the vacuum occupation distribution. It ends immediately before the user's subsequent request to write up the discussion.

## Revisiting the two-copy squeeze

**User:** What is $K_0$?

**Assistant:** It is the shifted total-boson-number operator $K_0=(N_L+N_R+2N)/2$, where $N$ is the number of faces. Each initial FL factor has $2J$ bosons, so $K_0|\Psi_0\rangle=(2J+N)|\Psi_0\rangle$. The additive shift makes $[K_+,K_-]=-2K_0$.

**User:** Right. Let's go through the discussion again, looking at the steps taken in between.

**Assistant:** The discussion began by identifying the geometric operators. The face fluxes are Schwinger-boson angular momenta $\mathbf J_i$, and closure is $\sum_i\mathbf J_i=0$. Under the squeeze, consistently transformed observables are $\widetilde O=U_\beta O U_\beta^\dagger$. The transformed closure generator annihilates the squeezed state; ordinary per-copy closure does not follow.

For a left-only operator, tracing out the right copy preserves its expectation: $\operatorname{Tr}(\rho_LO_L)=\langle\Psi_\beta|O_L\otimes I_R|\Psi_\beta\rangle$. A transformed observable generally acts on both copies and cannot be obtained from $\rho_L$ alone.

The draft constructs $|J,\mathbf z\rangle_{\beta,L}=U_\beta(|J,\mathbf z\rangle_L\otimes|0\rangle_R)$: an FL intertwiner on the left and vacuum on the right before the squeeze. We distinguished this from the user's two-intertwiner construction. A canonical TFD would require a complete orthonormal basis diagonalizing a specified Hamiltonian and weights of the form $Z^{-1/2}e^{-\beta E_\alpha/2}$. This comparison framed the properties to investigate; it did not select a different construction.

**User:** What happens if we start with a vacuum product and act with thermal $F$ operators on both copies?

**Assistant:** Acting with transformed pair creators on the thermal vacuum cancels the adjacent unitaries and gives $U_\beta$ applied to an FL intertwiner on each copy. Acting on the ordinary doubled vacuum leaves a residual $U_\beta^\dagger|0,0\rangle$.

**User:** Yes. That $\Psi_\beta$ is exactly what I want.

The selected state is

$$

**User:** The way I understand the expressions for $\Psi_\beta$ is the following. For the ordinary FL state, there is no expression involving an infinite sum. All quantities, Hilbert spaces, bases, are finite. Here, the infinite sum appears because at finite temperature there is a nonzero probability that a state, no matter how far from the ground state, will be excited. Thoughts?

**Assistant:** At fixed $J$ and fixed number of faces, the ordinary FL vector lies in a finite-dimensional fixed-number sector. The full oscillator Fock space containing all $J$ values is infinite. The squeeze opens unbounded final occupation sectors $q$; at finite positive $\beta$ each allowed arbitrarily high sector can contribute. Symmetries and conservation still restrict support, including equal total occupation in the two copies. Calling those coefficients thermal probabilities for a physical Hamiltonian requires establishing the corresponding Gibbs form.
|\Psi_\beta\rangle=U_\beta\bigl(|J,\mathbf z\rangle_L\otimes|\overline{J,\mathbf z}\rangle_R\bigr).
$$

## Occupation expansion

**User:** How did you get that last expression for $\Psi_\beta$ from the product form?

**Assistant:** Start with the ordered factorization

$$
U_\beta=e^{tK_+}(\operatorname{sech}\theta)^{2K_0}e^{-tK_-},\qquad t=\tanh\theta.
$$

Apply factors right to left. First expand pair annihilation:

$$
e^{-tK_-}|\Psi_0\rangle=\sum_{s=0}^{2J}\frac{(-t)^s}{s!}K_-^s|\Psi_0\rangle.
$$

The sum ends at $2J$ because each copy begins with $2J$ bosons. Initially $K_0|\Psi_0\rangle=(2J+N)|\Psi_0\rangle$. Since $[K_0,K_-]=-K_-$,

$$
K_0K_-^s|\Psi_0\rangle=(2J+N-s)K_-^s|\Psi_0\rangle,
$$

so the middle factor contributes $(\operatorname{sech}\theta)^{4J+2N-2s}$. Finally,

$$
e^{tK_+}=\sum_{r=0}^\infty\frac{t^r}{r!}K_+^r.
$$

Combining them in that order gives

$$
|\Psi_\beta\rangle=\sum_{s=0}^{2J}\sum_{r=0}^{\infty}
\frac{(-1)^st^{s+r}}{s!r!}(\operatorname{sech}\theta)^{4J+2N-2s}
K_+^rK_-^s|\Psi_0\rangle.
$$

No operators have been commuted past one another in this step.

**User:** One more thing. Here we are working with quantum states. The usual vectorial picture of a state. But, in general, working with density matrices would be more useful especially since we are dealing with thermal ensembles.

**Assistant:** Agreed. The doubled density matrix is $\rho_{LR}=U_\beta\rho_0U_\beta^\dagger$, still pure, and tracing out one copy gives the generally mixed $\rho_L$. In an orthonormal basis, if $|\Psi_\beta\rangle=\sum_{\mathbf n,\mathbf m}C_{\mathbf n\mathbf m}|\mathbf n\rangle_L|\mathbf m\rangle_R$, then $\rho_L=CC^\dagger$ with entries $(\rho_L)_{\mathbf n\mathbf n'}=\sum_{\mathbf m}C_{\mathbf n\mathbf m}C^*_{\mathbf n'\mathbf m}$. The doubled density matrix remains needed for observables acting on both copies.

**User:** Can we examine the behavior of the state coefficients as a function of $J$?

**Assistant:** For this question, hold the initial FL label $J$ fixed and examine final boson number $q$. With $r=q-2J+s$, the coefficient of a specified doubled occupation vector is the finite sum

$$
C_{\mathbf n\mathbf m}(\beta)=\sum_{s=\max(0,2J-q)}^{2J}
\frac{(-1)^st^{q-2J+2s}(1-t^2)^{2J+N-s}}
s!(q-2J+s)!\,
\langle\mathbf n,\mathbf m|K_+^{q-2J+s}K_-^s|\Psi_0\rangle.
$$

The final sector includes all coherent contributions with that $q$. An illustrative single pair action is

$$
a_{1L}^\dagger a_{1R}^\dagger|\mathbf n,\mathbf m\rangle
=\sqrt{(n_1^a+1)(m_1^a+1)}|\mathbf n+\mathbf e_{a_1},\mathbf m+\mathbf e_{a_1}\rangle.
$$

This shows why the factorial prefactors in the disentangled expression do not alone determine the coefficient trend: the occupation-basis matrix elements matter too.

**User:** How would you represent a state individually?

**Assistant:** Use normalized occupation-number basis states $|\mathbf n\rangle_X=\prod_i(a_{iX}^\dagger)^{n_i^a}(b_{iX}^\dagger)^{n_i^b}/\sqrt{n_i^a!n_i^b!}|0\rangle_X$, and doubled vectors $|\mathbf n,\mathbf m\rangle=|\mathbf n\rangle_L|\mathbf m\rangle_R$. Expand the FL product with coefficients $f_{\mathbf n}(\mathbf z)\overline{f_{\mathbf m}(\mathbf z)}$. A single $a_{1L}^\dagger a_{1R}^\dagger$ action multiplies an occupation vector by $\sqrt{(n_1^a+1)(m_1^a+1)}$ and increments those two occupations. The full $K_+$ sums this action over all paired modes. The first pair-created states have components $\Psi_0$, $K_+\Psi_0$, and $K_+^2\Psi_0$, but the actual squeezed-state sector also includes coherent annihilation-then-creation contributions.

**User:** Now in performing calculations with the thermal state or density matrices, you can't sum over $J\to\infty$, right?

**Assistant:** The initial FL $J$ stays fixed; the squeeze opens unbounded final occupation sectors $q$. In numerical calculations one truncates $q$ and checks convergence. A cutoff diagnostic is $\epsilon_{\rm tail}=1-\sum_{q=0}^{q_{\max}}\operatorname{Tr}\rho_{L,q}$. For area or volume, convergence of the observable contribution must also be checked because a small omitted probability alone does not control an unbounded observable.

## Area ensemble and sector probabilities

**User:** Here, the area is the most natural observable to serve as the Hamiltonian.

**Assistant:** With the FL total-area label $\widehat{\mathcal J}=N_L/2$, one can define $H_A=\lambda\widehat{\mathcal J}$. A sector with $q$ bosons per copy then has $\mathcal J=q/2$. In a canonical ensemble, an individual state receives weight proportional to $e^{-\beta\lambda q/2}$; the area-sector probability includes the number of states at that area. Whether the reduced density matrix of the selected excited-FL squeeze has this canonical form remains an open calculation. If one instead uses the standard LQG area proportional to $\sum_i\sqrt{j_i(j_i+1)}$, total occupation alone does not fix the energy.

The low-temperature comparison follows from the selected construction: for fixed positive $\lambda$, the unrestricted area-Hamiltonian Gibbs state approaches the $q=0$ vacuum as $\beta\to\infty$. The squeezed excited-FL family approaches its initial nonzero-$J$ FL state. These two families therefore cannot agree over all temperatures on that support.

**User:** It obviously will not be a decreasing exponential for all values of the area.

**Assistant:** Correct. For a canonical ensemble, the weight of an individual state is exponential in energy, but the probability of the whole energy or area sector is $P(\mathcal J)=g(\mathcal J)e^{-\beta\lambda\mathcal J}/Z$. Its trend reflects multiplicity and Boltzmann suppression together.

**User:** And the $g(J)$ factor is exactly what is causing the peaks in the $p_q$ vs $q$ curves.

**Assistant:** Exactly. In the vacuum example, $p_q=(1-e^{-b})^8\binom{q+7}{7}e^{-bq}$. The growing multiplicity produces the rise; exponential suppression eventually produces the fall. This accounts for the vacuum peaks. The excited FL distribution still requires its own coefficient and interference calculation.

**User:** Can you make some plots?

**Assistant:** The plot request was answered with three panels for the exact four-face $J=0$ squeezed vacuum: individual matched-basis amplitude, total occupation-sector probability, and probability discarded above a cutoff, at $b=2,1,0.5,0.25$. The curves are explicitly vacuum illustrations; they do not calculate the nonzero-$J$ FL distribution.

**User:** The Maxwell-like curve is completely unexpected.

**Assistant:** The sector multiplicity $g_q=\binom{q+7}{7}$ rises with $q$ and initially competes with the individual-state factor $e^{-bq}$. Their product can peak; at large $q$ its envelope is $q^7e^{-bq}$. Each individual matched-basis coefficient still decreases exponentially.

## End of preserved transcript

The transcript stops here, immediately before the user's subsequent request to write up the discussion. The note and the linked figure/code/data are the written-up result.
