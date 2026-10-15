"""Plot saved T9 entanglement data; this script does not rerun the study."""
from pathlib import Path
import csv
import json
import hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'results/thermal-closed-entanglement'
FIG=ROOT/'figures/thermal-closed-entanglement'


def main():
    FIG.mkdir(parents=True,exist_ok=True)
    rows=list(csv.DictReader((DATA/'temperature_summary.csv').open()))
    a={key:np.array([float(r[key]) for r in rows]) for key in rows[0]}
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'pdf.fonttype':42})
    t=a['temperature']
    fig,axes=plt.subplots(2,2,figsize=(7.3,5.9),layout='constrained')
    ax=axes[0,0]
    ax.plot(t,a['entropy_nats'],label='von Neumann',color='#164e83')
    ax.plot(t,a['renyi2_nats'],'--',label='Rényi 2',color='#a75013')
    ax.set(title='(a) Entanglement between closed copies',ylabel=r'Entropy / $k_B$ (nats)')
    ax.legend(fontsize=9)
    ax=axes[0,1]
    ax.plot(t,a['area_entropy_nats'],label='Area distribution',color='#a75013')
    ax.plot(t,a['within_area_entropy_nats'],'--',label='Within area sectors',color='#164e83')
    ax.set(title='(b) Where the entropy resides',ylabel=r'Entropy / $k_B$ (nats)')
    ax.legend(fontsize=9)
    ax=axes[1,0]
    ax.plot(t,a['joint_F12_creation_real'],color='#164e83')
    ax.set(title='(c) Coherent singlet creation on both sides',
           ylabel=r'$\mathrm{Re}\langle F^\dagger_{12,L}F^\dagger_{12,R}\rangle$')
    ax=axes[1,1]
    ax.plot(t,a['d_entropy_d_temperature'],color='#164e83')
    ax.set(title='(d) Entanglement response to heating',ylabel=r'$d(S_L/k_B)/dT_*$')
    for ax in axes.flat:
        ax.set_xlabel(r'$T_*=k_BT/(\hbar\omega)$');ax.grid(alpha=.22)
    for ext in ['pdf','png']:
        fig.savefig(FIG/f'entanglement_overview.{ext}',dpi=300)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(7.3,3.25),layout='constrained')
    sectors=list(csv.DictReader((DATA/'area_sectors.csv').open()))
    for i,t in enumerate([.5,1.,2.,5.]):
        saved=np.load(DATA/f'spectrum_T{t:g}.npz',allow_pickle=False)
        order=np.argsort(saved['eigenvalue'])[::-1]
        rank=np.cumsum(saved['multiplicity'][order])
        mass=np.cumsum(saved['multiplicity'][order]*saved['eigenvalue'][order])
        axes[0].plot(rank,mass,['-','--','-.',':'][i],label=f'$T_*={t:g}$')
        sub=[r for r in sectors if float(r['temperature'])==t]
        axes[1].plot([int(r['K']) for r in sub],[float(r['probability']) for r in sub],
                     ['-','--','-.',':'][i],label=f'$T_*={t:g}$')
    axes[0].set(xscale='log',xlabel='Schmidt rank (group endpoints)',ylabel='Cumulative probability',
                title='(a) Number of appreciably occupied modes',ylim=(0,1.02))
    axes[1].set(xlabel='Area K per copy',ylabel='Area-sector probability',
                title='(b) Distribution over closed areas',xlim=(0,55))
    for ax in axes:
        ax.legend(fontsize=8);ax.grid(alpha=.22)
    for ext in ['pdf','png']:
        fig.savefig(FIG/f'schmidt_and_area_distributions.{ext}',dpi=300)
    plt.close(fig)
    sources=list(DATA.glob('*.csv'))+list(DATA.glob('spectrum_*.npz'))
    (FIG/'plot_summary.json').write_text(json.dumps(dict(
        sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        figures=['entanglement_overview','schmidt_and_area_distributions'],
        png_dpi=300,physical_scope='four labelled faces, F12 reference, normalized double-singlet projection',
        rank_plot='multiplicities retained; lines join grouped eigenvalue endpoints'),indent=2)+'\n')
    print('Exported two vector PDFs and two 300-dpi PNGs from saved arrays')


if __name__=='__main__':main()
