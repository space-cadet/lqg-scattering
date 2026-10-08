# T9 four-face $J_{\mathrm{in}}=1$ spin distribution

Recorded on 2026-10-08 by **GPT 6.1 Sol**. This session implements the next small-sector calculation proposed in the thermal-area discussion and updates [`notes/thermal-area-sectors.md`](../../notes/thermal-area-sectors.md).

For the four-face $J_{\mathrm{in}}=1$ input, the one-copy occupation/resultant-spin joint probability $P(q,S)$ was implemented by two methods: explicit coupling of the four face spins, and magnetic-component occupation counting followed by a finite difference in $M$. Both use the derived occupation-sector coefficient matrix. The methods were compared at $q=0,\ldots,160$ for $\beta\hbar\omega=0.5,1,2,4,8$, totaling 32,805 entries; their maximum absolute discrepancy is $2.671474153\times10^{-16}$.

The checks also compare the oscillator-exponential occupation coefficients against an independent expression and direct Casimir projectors through $q=4$. Normalization, occupation moments, nonnegativity, and positive tail bounds were checked. Temperature plots show broader occupation and spin distributions at higher temperature, plus the marginal distributions, method agreement, and the per-copy singlet probability.

There is no exact high-$q$ cutoff at finite positive temperature. For every kinematically allowed $(q,S)$, an explicit positive lower bound proves $P(q,S)>0$. The restrictions $S\le q/2$ and the occupation-spin parity rule are kinematic; apparent truncations in the figures come from chosen display ranges or numerical precision.

The calculation is the one-copy marginal distribution for the four-face $J_{\mathrm{in}}=1$ construction. It does not yet form all two-copy coefficient blocks $C_qC_q^\dagger$, determine the reduced-state spectrum or entropy, test geometric observables, or establish a general result for higher initial $J$. See the source, comparison outputs, and plots linked from the research note.
