"""Export the four-rotor comparison at print size, PDF and 300-dpi PNG."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'results/t11-quantum-planar-rotors'
OUT=ROOT/'figures/t11-quantum-planar-rotors'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    summary=json.loads((DATA/'summary.json').read_text())
    plt.rcParams.update({'font.size':9,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':8,'legend.fontsize':8,'pdf.fonttype':42})
    fig,axes=plt.subplots(2,2,figsize=(7.1,5.1),layout='constrained')
    for col,case in enumerate(summary['cases']):
        m=case['m']; cutoff=case['accepted_cutoff']
        q=json.loads((DATA/f'quantum-m{m}-c{cutoff}.json').read_text())['rows']
        c=json.loads((DATA/f'classical-m{m}.json').read_text())['rows']
        t=np.array([r['time'] for r in q]); qk=np.array([r['kinetic'] for r in q]); ck=np.array([r['kinetic'] for r in c])
        # The conservative sum of marginal SEs bounds the cold-pair SE.
        se=np.array([sum(r['kinetic_standard_error'][2:]) for r in c])/m**2
        ax=axes[0,col]; y=ck[:,2:].sum(axis=1)/m**2
        ax.plot(t,qk[:,2:].sum(axis=1)/m**2,color='#1769aa',label='Quantum',lw=1.6)
        ax.plot(t,y,'--',color='#d65f00',label='Classical ensemble',lw=1.4)
        ax.fill_between(t,y-2*se,y+2*se,color='#d65f00',alpha=.16,label='Conservative 2 SE band')
        ax.set_title(f'Packet kinetic energy = {m*m}'); ax.set_ylabel('Cold-pair kinetic energy\n/ initial packet energy')
        ax.set_ylim(bottom=0)
        ax=axes[1,col]
        for site,style,color in [(0,'-','#1769aa'),(2,'--','#d65f00')]:
            ax.plot(t,[r['entropy'][site] for r in q],style,color=color,label=f'Rotor {site+1}',lw=1.5)
        ax.set_ylabel('Single-rotor entropy (nats)'); ax.set_xlabel(r'Time $\tau=t\sqrt{\lambda/I}$'); ax.set_ylim(bottom=0); ax.legend()
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='outside upper center',ncol=3)
    for ax in axes.flat: ax.grid(alpha=.2); ax.set_xlim(0,20)
    fig.savefig(OUT/'energy-transfer.pdf'); fig.savefig(OUT/'energy-transfer.png',dpi=300)
    print('Exported vector PDF and 300-dpi PNG')

if __name__=='__main__': main()
