"""Coupling-scaled transfer crossover and delayed-escape controls."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from t11_rotor_coupling_scan import ROOT,OUT


def main():
    figdir=ROOT/'figures/t11-rotor-coupling';figdir.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':9,'axes.labelsize':9,'axes.titlesize':10,'legend.fontsize':8,'xtick.labelsize':8,'ytick.labelsize':8,'pdf.fonttype':42})
    groups=list(csv.DictReader((OUT/'grouped-scan.csv').open()));rows=list(csv.DictReader((OUT/'summary.csv').open()))
    fig,axes=plt.subplots(1,3,figsize=(10,3.3),layout='constrained')
    colors=['#0072B2','#009E73','#D55E00','#CC79A7'];styles=['-','--','-.',':']
    for n,color,style in zip([8,16,32,64],colors,styles):
        rs=[r for r in groups if int(r['N'])==n and float(r['window_end'])==2000]
        x=np.array([float(r['ratio']) for r in rs]);y=np.array([float(r['mean']) for r in rs]);lo=np.array([float(r['minimum']) for r in rs]);hi=np.array([float(r['maximum']) for r in rs])
        axes[0].plot(x,y,color=color,ls=style,marker='.',label=f'N={n}')
        axes[0].fill_between(x,lo,hi,color=color,alpha=.12)
    axes[0].axhline(.1,color='gray',ls=':',lw=1);axes[0].axhline(.01,color='gray',ls='--',lw=1)
    axes[0].set(xscale='log',yscale='log',title='A  Transfer crossover',xlabel=r'Packet energy / coupling, $r$',ylabel='Mean cold kinetic energy / packet',ylim=(1e-4,.8));axes[0].legend(frameon=False,loc='lower left')
    for n,color,style in [(8,colors[0],'-'),(64,colors[3],':')]:
        a=[r for r in rows if r['kind']=='scan' and int(r['N'])==n and r['seed']=='1701' and float(r['window_end'])==2000]
        x=np.array([100/float(r['ratio']) for r in a]);y=np.array([float(r['mean_cold_kinetic_fraction']) for r in a]);order=np.argsort(x)
        axes[1].plot(x[order],y[order],color=color,ls=style,label=f'N={n}, scaled prediction')
        a=[r for r in rows if r['kind']=='physical_coupling' and int(r['N'])==n and float(r['window_end'])==2000]
        axes[1].scatter([float(r['coupling']) for r in a],[float(r['mean_cold_kinetic_fraction']) for r in a],facecolors='none',edgecolors=color,s=45,zorder=3)
    axes[1].scatter([],[],facecolors='none',edgecolors='black',label='Direct coupling runs')
    axes[1].set(xscale='log',yscale='log',title='B  Fixed packet energy = 100',xlabel=r'Coupling $\lambda$',ylabel='Mean cold kinetic energy / 100',ylim=(1e-4,.8));axes[1].legend(frameon=False,loc='lower right',fontsize=7)
    cases=[('long_time_N8_R18_S1701_L1',18,colors[0],'-','N=8, r=18'),('long_time_N64_R16_S1701_L1',16,colors[3],':','N=64, r=16'),('long_time_N64_R20_S1701_L1',20,colors[2],'-.','N=64, r=20')]
    for name,r,color,style,label in cases:
        ar=np.load(OUT/f'{name}.npz');t=ar['tau'];y=ar['readouts'][:,4]/r
        width=200;count=(len(t)-1)//width;tt=t[1:1+width*count].reshape(-1,width).mean(axis=1);yy=y[1:1+width*count].reshape(-1,width).mean(axis=1)
        axes[2].plot(tt,yy,color=color,ls=style,label=label)
    axes[2].axvline(2000,color='gray',ls='--',lw=1)
    axes[2].set(title='C  Delayed transfer',xlabel=r'Scaled time $\tau=t\sqrt{\lambda/I}$',ylabel='Cold kinetic energy / packet',ylim=(0,.65));axes[2].legend(frameon=True,framealpha=.95,edgecolor='white',loc='upper left',fontsize=7)
    fig.suptitle('A: three seeds, window 200–2000. B: seed 1701, same scaled window. C: 100-time-unit block means.',fontsize=9)
    fig.savefig(figdir/'coupling-crossover.pdf',bbox_inches='tight');fig.savefig(figdir/'coupling-crossover.png',dpi=300,bbox_inches='tight')
    print('Exported vector PDF and 300-dpi PNG.')

if __name__=='__main__':main()
