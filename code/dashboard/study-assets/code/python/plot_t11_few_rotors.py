"""Exact pair-transfer barrier and generic 3D coupling controls."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from t11_few_rotors import pair_bound,OUT,ROOT


def main():
    figdir=ROOT/'figures/t11-few-rotors';figdir.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':9,'axes.labelsize':9,'axes.titlesize':10,'legend.fontsize':8,'xtick.labelsize':8,'ytick.labelsize':8,'pdf.fonttype':42})
    fig,axes=plt.subplots(1,3,figsize=(10,3.1),layout='constrained')
    colors=['#0072B2','#009E73','#D55E00']
    for ratio,color,style in zip([1.,10.,100.],colors,['-','--','-.']):
        ar=np.load(OUT/f'pair_ratio_{ratio:g}.npz')
        mask=ar['tau']<=20
        axes[0].plot(ar['tau'][mask],ar['kinetic'][mask,1]/ratio,color=color,ls=style,label=f'r = {ratio:g}')
    axes[0].set(title='A  Initially resting rotor',xlabel=r'Scaled time $\tau$',ylabel=r'Kinetic energy $T_2/T_0$',ylim=(-.03,1.04));axes[0].legend(frameon=False)
    r=np.geomspace(.3,1000,1000)
    axes[1].loglog(r,[pair_bound(x) for x in r],color='black',lw=1.5,label='Exact maximum')
    pairs=list(csv.DictReader((OUT/'pair-summary.csv').open()))
    unique=[x for x in pairs if x['case'].startswith('ratio')]
    axes[1].scatter([float(x['ratio']) for x in unique],[float(x['sampled_max_receiver_fraction']) for x in unique],color='#0072B2',marker='x',label='Numerical maximum',zorder=3)
    axes[1].axvline(4,color='gray',ls=':',lw=1)
    axes[1].text(4.8,.4,'r = 4',fontsize=8)
    axes[1].set(title='B  Exact transfer bound',xlabel=r'Initial kinetic energy / coupling, $r$',ylabel=r'Maximum $T_2/T_0$')
    axes[1].legend(frameon=False,loc='lower left')
    rows=list(csv.DictReader((OUT/'few-summary.csv').open()))
    for graph,color,marker,style,label in zip(['triangle','four_open','four_ring'],colors,['o','s','^'],['-','--','-.'],['3D triangle','3D four-site open chain','3D four-site ring']):
        gs=sorted(set(float(x['coupling']) for x in rows));values=[];lo=[];hi=[]
        for g in gs:
            a=[float(x['mean_cold_kinetic_over_initial_packet']) for x in rows if x['graph']==graph and float(x['coupling'])==g]
            values.append(np.mean(a));lo.append(min(a));hi.append(max(a))
        axes[2].plot(gs,values,color=color,marker=marker,ls=style,label=label)
        axes[2].fill_between(gs,lo,hi,color=color,alpha=.12)
    axes[2].set(xscale='log',title='C  Zero-total-J 3D controls',xlabel=r'Coupling $\lambda$; packet energy = 100',ylabel='Mean cold-rotor kinetic energy / 100',ylim=(-.01,.4))
    axes[2].legend(frameon=False,loc='upper left',fontsize=7)
    fig.suptitle('A–B: aligned planar pair, one bond. C: three orientation seeds; scaled-time window 20–200.',fontsize=9)
    fig.savefig(figdir/'few-rotor-transfer.pdf',bbox_inches='tight')
    fig.savefig(figdir/'few-rotor-transfer.png',dpi=300,bbox_inches='tight')
    print('Exported vector PDF and 300-dpi PNG.')

if __name__=='__main__':main()
