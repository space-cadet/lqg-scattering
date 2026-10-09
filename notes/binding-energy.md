# Four-site detachment energy

The calculation compares the intact four-site Schwinger Bose-Hubbard Hamiltonian with a three-site fragment plus an isolated fourth site. Both have four bosons and combined total spin zero. Separation deletes all hopping edges incident on site 3 and retains every onsite term and all eight modes. Complete-graph separation leaves a triangle; ring separation leaves a three-site chain.

$$H=-t\sum_{(i,j)}(E_{ij}+E_{ji})+\frac{U}{2}\sum_i n_i(n_i-1),\qquad E_{\mathrm{bind}}=E_{3}+E_1-E_{\mathrm{intact}}.$$

The intact state is the lowest-energy singlet, rather than the initial FL coherent state. The separated state is the lowest-energy state in a fixed isolated-face occupation sector, coupled to total spin zero. The main channel has three bosons in the fragment and one on the isolated face. Each subsystem has total spin one-half; they couple to a singlet. Their joint state can remain spin-entangled even though their Hamiltonian has no connecting hopping terms.

At $t=1,U=5$:

| Graph | Intact singlet ground energy | Three-plus-one threshold | Binding energy |
|---|---:|---:|---:|
| Complete | -1.844288770 | -1.075035470 | 0.769253300 |
| Ring | -1.844288770 | -1.049209993 | 0.795078777 |

The isolated one-boson face has zero onsite energy. The two-plus-two occupation channel also admits a combined singlet but has higher thresholds, respectively 2.000000000 and 3.086755804. A one-plus-three occupation channel cannot form a singlet: the one-boson fragment cannot balance the isolated spin-three-halves face. Thus three-plus-one is the lowest nonempty singlet channel at these parameters.

The original FL seed is not the interacting ground state: its intact mean energies are 1.734013676 and 3.367006838, respectively, and both energy uncertainties are 3.316624790. The positive ground-state detachment energy is not evidence that this prepared coherent state is stationary or bound below the threshold.

This is a finite graph detachment comparison. The graph has no separation coordinate or continuum scattering states. Local occupations within the connected fragment can fluctuate, including empty sites; the calculation does not constrain three faces to remain individually occupied. No geometric-volume characterization of the ground state was performed, so “tetrahedron” here specifies the four-site system, not an established semiclassical tetrahedral geometry. Total number and spin are fixed; additional shape or local-area constraints would define a different comparison.

## Reproduction and checks

Run `python code/python/binding_energy.py` in the numerical environment. Results are in `results/binding-energy/summary.json`, including $U/t=0,1,5,20$, channel dimensions, eigenstate residuals, and FL-seed energy uncertainties before and after cutting the links.

The singlet subspaces are obtained by diagonalizing total $J^2$ and the projected Hamiltonians. Full-space ground-state residuals are below $3\times10^{-14}$ at $U=5$. Tests independently reproduce the free one-particle-orbital thresholds and the zero-hopping, zero-detachment-cost limit.
