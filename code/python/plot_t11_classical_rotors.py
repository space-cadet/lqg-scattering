"""Vector PDF and 300-dpi PNG figures from saved classical rotor data."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/t11-classical-rotors'
FIG=ROOT/'figures/t11-classical-rotors'
COLORS=['#0072B2','#009E73','#D55E00']


def export(fig,name):
    FIG.mkdir(parents=True,exist_ok=True)
    fig.savefig(FIG/f'{name}.pdf',bbox_inches='tight')
    fig.savefig(FIG/f'{name}.png',dpi=300,bbox_inches='tight')
    plt.close(fig)


def main():
    plt.rcParams.update({'font.size':9,'axes.labelsize':9,'axes.titlesize':10,'legend.fontsize':8,'xtick.labelsize':8,'ytick.labelsize':8,'pdf.fonttype':42})
    fig,ax=plt.subplots(2,2,figsize=(7.2,5.3),layout='constrained')
    for ratio,color,style in zip([1,10,100],COLORS,['-', '--', '-.']):
        ar=np.load(OUT/f'N32_R{ratio}_fixed_packet_S1701.npz');d=ar['readouts'];t=ar['times']
        # Nonoverlapping 20-time-unit block means, including initial point separately.
        count=(len(t)-1)//40
        tt=t[1:1+40*count].reshape(-1,40).mean(axis=1)
        for panel,values in [(ax[0,0],d[:,2]),(ax[0,1],1/(32*d[:,3]))]:
            vv=values[1:1+40*count].reshape(-1,40).mean(axis=1)
            panel.plot(np.r_[0,tt],np.r_[values[0],vv],color=color,ls=style,label=f'Packet energy {ratio}')
        mc=ar['microcanonical_readouts'];reference=np.mean(1/(32*mc[:,:,3]))
        ax[0,1].axhline(reference,color=color,ls=':',lw=1,alpha=.7)
    ax[0,0].axhline(2/32,color='black',ls=':',label='Equilibrium mean 2/N')
    ax[0,0].set(title='A  Energy in the original pair',ylabel='Fraction of total energy',xlabel='Time',ylim=(0,1.04))
    ax[0,0].legend(loc='center right',frameon=False)
    ax[0,1].set(title='B  Energy participation',ylabel=r'$1/[N\sum_i(e_i/E)^2]$',xlabel='Time',ylim=(0,1.04))
    ax[0,1].text(.98,.95,'Dotted: equilibrium means',transform=ax[0,1].transAxes,ha='right',va='top',fontsize=8)
    for a,ratio,letter in [(ax[1,0],10,'C'),(ax[1,1],100,'D')]:
        ar=np.load(OUT/f'N32_R{ratio}_fixed_packet_S1701.npz');d=ar['readouts'];e=d[:,8:]/d[:,0,None]
        im=a.imshow(e[::10].T,origin='lower',aspect='auto',extent=[0,2000,-.5,31.5],cmap='magma',norm=LogNorm(vmin=1e-5,vmax=.5))
        a.set(title=f'{letter}  Local energy, packet energy {ratio}',xlabel='Time',ylabel='Rotor index')
        fig.colorbar(im,ax=a,label=r'Local energy fraction $e_i/E$',shrink=.85)
    fig.suptitle('32 rotors; fixed packet energy; orientation seed 1701',fontsize=9)
    export(fig,'rotor-dynamics')
    rows=list(csv.DictReader((OUT/'grouped-summary.csv').open()))
    fig,ax=plt.subplots(2,2,figsize=(7.2,5.0),layout='constrained')
    for col,scaling in enumerate(['fixed_packet','fixed_density']):
      for ratio,color,style in zip([1,10,100],COLORS,['-', '--', '-.']):
        rr=[r for r in rows if r['scaling']==scaling and float(r['ratio'])==ratio];n=np.array([int(r['N']) for r in rr])
        for a,name in [(ax[0,col],'mean_hot_fraction'),(ax[1,col],'residence_region90')]:
            y=np.array([float(r[name+'_mean']) for r in rr]);lo=np.array([float(r[name+'_min']) for r in rr]);hi=np.array([float(r[name+'_max']) for r in rr])
            a.plot(n,y,marker='o',color=color,ls=style,label=f'Energy parameter {ratio}')
            a.fill_between(n,lo,hi,color=color,alpha=.15)
      ax[0,col].plot(n,2/n,':',color='black',label='Equilibrium 2/N')
      ax[1,col].axhline(.9,ls=':',color='black')
      title='Fixed packet energy' if col==0 else 'Fixed energy density (approximately)'
      ax[0,col].set(title=title,ylabel='Original-pair energy fraction',ylim=(0,1.04))
      ax[1,col].set(ylabel='Equilibrium-region residence',xlabel='Number of rotors N',ylim=(0,1.04))
      for a in ax[:,col]:a.set_xscale('log',base=2);a.set_xticks([8,16,32,64],['8','16','32','64'])
    ax[0,0].legend(frameon=False,fontsize=7,loc='center right')
    fig.suptitle('Three orientation seeds; shaded bands show their range; time window 200–2000',fontsize=9)
    export(fig,'rotor-scaling')
    print('Exported two figures as vector PDF and 300-dpi PNG.')

if __name__=='__main__':main()
