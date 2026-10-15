"""Figures of saved free-hopping controls; no new dynamics calculation."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'results/fl-face-activation/dynamics.csv'
FIG=ROOT/'figures/fl-face-activation'


def main():
    FIG.mkdir(parents=True,exist_ok=True)
    rows=list(csv.DictReader(SOURCE.open()))
    def series(l,k,phase='baseline'):
        return [r for r in rows if int(r['channels'])==l and int(r['K'])==k and r['phase_case']==phase]
    def values(data,key):return np.array([float(r[key]) for r in data])
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'pdf.fonttype':42})
    fig,axes=plt.subplots(2,2,figsize=(7.3,5.9),layout='constrained')
    for k,style in [(2,':'),(20,'-.'),(100,'--'),(10000,'-')]:
        r=series(5,k)
        axes[0,0].plot(values(r,'period_fraction'),values(r,'expected_active_faces'),style,label=f'K={k}')
    axes[0,0].set(title='(a) A fifth channel becomes occupied',ylabel='Expected active channels',ylim=(2.3,5.1))
    axes[0,0].legend(fontsize=8,ncol=2)
    for l,phase,style in [(5,'baseline','-'),(5,'phase_shifted','--'),(6,'baseline','-.'),(6,'phase_shifted',':')]:
        r=series(l,10000,phase)
        axes[0,1].plot(values(r,'period_fraction'),values(r,'new_channel_mean_area')/10000,style,
                       label=f'L={l}, '+('original phases' if phase=='baseline' else 'shifted phases'))
    axes[0,1].set(title='(b) Area transferred to extra channels',ylabel='Fraction of total area',ylim=(0,.58))
    axes[0,1].legend(fontsize=7.5,ncol=2,loc='upper right')
    r=series(5,10000)
    for i,style in enumerate(['-','--','-.',':','-']):
        axes[1,0].plot(values(r,'period_fraction'),values(r,f'face_{i}_area')/10000,style,
                       label=f'Face {i+1}'+(' (new)' if i==4 else ''))
    axes[1,0].set(title='(c) Areas remain unequal and recur',ylabel=r'Mean face area / $K$',ylim=(0,.4))
    axes[1,0].legend(fontsize=7.5,ncol=3,loc='upper right')
    axes[1,1].plot(values(r,'period_fraction'),values(r,'local_energy_rms_deviation')/10000)
    axes[1,1].set(title='(d) Local energy sharing also recurs',ylabel=r'RMS face-energy deviation / $K$')
    for ax in axes.flat:
        ax.set_xlabel(r'Time / period ($2\pi/L$)');ax.grid(alpha=.22)
    for ext in ['pdf','png']:
        fig.savefig(FIG/f'face_activation_control.{ext}',dpi=300,bbox_inches='tight')
    plt.close(fig)
    (FIG/'plot_summary.json').write_text(json.dumps(dict(
        source='results/fl-face-activation/dynamics.csv',sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        png_dpi=300,figure='face_activation_control',
        scope='exact complete-graph free hopping; six-channel extra normals coincide; no equilibration claim'),indent=2)+'\n')
    print('Exported one vector PDF and one 300-dpi PNG from saved dynamics')


if __name__=='__main__':main()
