"""Publication-size figures for the exact geometric redistribution pilot."""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];DATA=ROOT/'results/t11-geometric-redistribution';OUT=ROOT/'figures/t11-geometric-redistribution'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with (DATA/'dynamics.csv').open() as f:rows=list(csv.DictReader(f))
    geometry=json.loads((DATA/'geometry.json').read_text())
    plt.rcParams.update({'font.size':9,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':8,'legend.fontsize':8,'pdf.fonttype':42})
    def selection(l,g,a,prep='regular_sharp'):
        return [r for r in rows if int(r['L'])==l and r['graph']==g and float(r['alpha'])==a and r['preparation']==prep]
    def save(fig,name):
        fig.savefig(OUT/f'{name}.pdf');fig.savefig(OUT/f'{name}.png',dpi=300);plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(7.2,4.8),layout='constrained',sharex=True,sharey=True)
    for i,g in enumerate(['ring','complete']):
        for j,a in enumerate([0,1,5]):
            ax=axes[i,j]
            for l,color,style in [(6,'#d65f00','--'),(8,'#1769aa','-')]:
                r=selection(l,g,a);ax.plot([float(v['time']) for v in r],[float(v['receiver_area_fraction']) for v in r],style,color=color,label=f'{l} channels')
            ax.set_title(f'{g.capitalize()}, '+r'$\alpha=$'+str(a));ax.set_xlim(0,20);ax.set_ylim(0,1);ax.grid(alpha=.2)
            if i==1:ax.set_xlabel('Time')
            if j==0:ax.set_ylabel('Area in initially empty channels\n/ conserved linear area')
    h,lab=axes[0,0].get_legend_handles_labels();fig.legend(h,lab,loc='outside upper center',ncol=2)
    save(fig,'area-transfer')
    fig,axes=plt.subplots(2,2,figsize=(7.1,5),layout='constrained')
    for g,color,style in [('ring','#1769aa','-'),('complete','#d65f00','--')]:
        for a,mark in [(1,'o'),(5,'s')]:
            r=selection(8,g,a);t=[float(v['time']) for v in r]
            label=f'{g}, '+r'$\alpha=$'+str(a)
            line=style if a==1 else (':' if g=='ring' else '-.')
            axes[0,0].plot(t,[sum(float(v[f'p_active_{n}']) for n in range(5,9)) for v in r],line,color=color,alpha=1 if a==1 else .55,label=label)
            gg=[v for v in geometry if v['L']==8 and v['graph']==g and v['alpha']==a and v['preparation']=='regular_sharp']
            times=[v['time'] for v in gg]
            axes[0,1].plot(times,[v['volume_mean'] for v in gg],line+mark,color=color,alpha=1 if a==1 else .55,label=label)
            axes[1,0].plot(times,[v['zero_volume_probability'] for v in gg],line+mark,color=color,alpha=1 if a==1 else .55)
    r=selection(8,'ring',1)
    for time,color,style in [(0,'#777777','-'),(2,'#d65f00','--'),(20,'#1769aa','-')]:
        v=next(v for v in r if abs(float(v['time'])-time)<1e-8)
        axes[1,1].plot(range(2,9),[float(v[f'p_active_{n}']) for n in range(2,9)],style+'o',color=color,label=f'Time {time}')
    axes[0,0].set_ylabel('Probability of at least\nfive occupied channels');axes[0,0].set_ylim(0,1)
    axes[0,1].set_ylabel('Mean positive RS volume\n(project normalization)')
    axes[1,0].set_ylabel('Zero-volume probability');axes[1,0].set_ylim(0,1)
    axes[1,1].set_ylabel('Probability');axes[1,1].set_xlabel('Occupied channels');axes[1,1].set_title(r'Eight-channel ring, $\alpha=1$');axes[1,1].legend()
    for ax in [axes[0,0],axes[0,1],axes[1,0]]:ax.set_xlabel('Time');ax.set_xlim(0,20)
    for ax in axes.flat:ax.grid(alpha=.2)
    h,lab=axes[0,0].get_legend_handles_labels();fig.legend(h,lab,loc='outside upper center',ncol=2)
    save(fig,'geometry-and-activation')
    print('Exported two vector PDFs and two 300-dpi PNGs')

if __name__=='__main__':main()
