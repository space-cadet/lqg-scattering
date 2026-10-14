"""Publication-size overview of the saved T9a pilot; no numerical rerun."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'figures/t9a-singlet-exchange'


def main():
    rows = list(csv.DictReader((ROOT/'results/t9a-singlet-exchange/dynamics.csv').open()))
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 8, 'axes.labelsize': 8, 'xtick.labelsize': 7,
                         'ytick.labelsize': 7, 'legend.fontsize': 7, 'pdf.fonttype': 42})
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 4.8), constrained_layout=True)
    styles = [('resonant', 'Resonant', '#0072B2', '-'),
              ('repulsive', 'Repulsive', '#D55E00', '--'),
              ('detuned', 'Detuned', '#009E73', ':')]
    panels = [('unequal_regular', 'area_left', '(a) Unequal regular inputs', r'$\langle A_L\rangle$'),
              ('equal_regular', 'area_variance', '(b) Equal regular inputs', r'$\mathrm{Var}(A_L)$'),
              ('unequal_regular', 'entropy_nats', '(c) Unequal regular inputs', 'Entanglement entropy (nats)'),
              ('equal_deformed_right', 'volume_R', '(d) Deformed right input', r'$\langle V_R\rangle$ (project units)')]
    for ax, (prep, quantity, title, label) in zip(axes.flat, panels):
        for case, legend, color, linestyle in styles:
            selected = [r for r in rows if r['case']==case and r['preparation']==prep]
            t = np.array([float(r['time']) for r in selected])
            y = np.array([float(r[quantity]) for r in selected])
            assert len(t)==101 and np.all(np.isfinite(y))
            ax.plot(t, y, label=legend, color=color, linestyle=linestyle, linewidth=1.2)
        ax.set(title=title, xlabel=r'Time ($\hbar=1$)', ylabel=label, xlim=(0,20))
        ax.grid(alpha=.2)
    fig.legend(*axes[0,0].get_legend_handles_labels(), loc='outside upper center', ncol=3, frameon=False)
    fig.savefig(OUT/'exchange-overview.pdf')
    fig.savefig(OUT/'exchange-overview.png', dpi=300)
    print('Exported vector PDF and 300-dpi PNG')


if __name__ == '__main__':
    main()
