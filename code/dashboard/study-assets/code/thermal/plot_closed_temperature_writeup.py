"""Pedagogical figures from the saved closed-projection data; no physics rerun."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'results/thermal-closed-projection'
OUT=ROOT/'figures/thermal-closed-projection'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    summary=list(csv.DictReader((DATA/'temperature_summary.csv').open()))
    distributions=list(csv.DictReader((DATA/'area_distribution.csv').open()))
    plt.rcParams.update({'font.size':10,'axes.labelsize':10,'axes.titlesize':11,'legend.fontsize':9,'pdf.fonttype':42})
    colors=['#0072B2','#D55E00','#009E73','#CC79A7']
    styles=['-','--','-.',':']
    fig,axes=plt.subplots(1,2,figsize=(8,3.5),layout='constrained')
    checks=[]
    for b,color,style in zip([4,2,1,.5],colors,styles):
        rows=[r for r in distributions if float(r['beta_hbar_omega'])==b]
        a=np.array([int(r['area']) for r in rows])
        p=np.array([float(r['probability']) for r in rows])
        assert np.min(p)>-2e-12 and abs(p.sum()-1)<2e-12
        axes[0].plot(a,p,color=color,ls=style,lw=1.8,marker='o',ms=2.5,label=rf'$T_*={1/b:g}$')
        ref=min(summary,key=lambda r:abs(float(r['beta_hbar_omega'])-b))
        assert abs(np.dot(a,p)-float(ref['conditional_mean_area']))<2e-10
        checks.append(dict(beta=b,normalization=float(p.sum()),mean_area=float(np.dot(a,p)),display_tail=float(p[a>30].sum())))
    axes[0].set_xlim(-.25,30);axes[0].set_ylim(bottom=0)
    axes[0].set_xlabel(r'Total linear area $A=q/2$');axes[0].set_ylabel('Probability after closure projection')
    axes[0].set_title('(a) Heating broadens the area distribution');axes[0].legend(frameon=False)
    t=np.array([float(r['temperature_kBT_over_hbar_omega']) for r in summary])
    four=np.array([float(r['conditional_four_active_faces_lower']) for r in summary])
    volume=1-np.array([float(r['conditional_kernel_probability_upper']) for r in summary])
    assert np.all(volume>=-2e-10) and np.all(volume<=four+2e-10)
    axes[1].plot(t,four,color=colors[0],lw=2,label='Four nonzero-area faces')
    axes[1].plot(t,volume,color=colors[1],ls='--',lw=2,label='Nonzero positive volume')
    axes[1].set_ylim(0,.55);axes[1].set_xlabel(r'Temperature $T_*=k_BT/(\hbar\omega)$')
    axes[1].set_ylabel('Probability within the closed state');axes[1].set_title('(b) Active faces and nonzero volume')
    axes[1].legend(frameon=False,loc='upper left')
    for ax in axes:ax.grid(alpha=.25)
    fig.savefig(OUT/'closed_projection_distributions.pdf',bbox_inches='tight')
    fig.savefig(OUT/'closed_projection_distributions.png',dpi=300,bbox_inches='tight');plt.close(fig)
    source_paths=[DATA/'temperature_summary.csv',DATA/'area_distribution.csv',Path(__file__)]
    (OUT/'writeup_plot_checks.json').write_text(json.dumps(dict(distribution_checks=checks,
        checks='normalized distributions; saved mean parity; nonzero-volume probability <= four-active-face probability',
        hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}),indent=2)+'\n')
    print('PASS: four normalized area distributions and geometric-support probabilities; PDF and 300-dpi PNG written.')


if __name__=='__main__':main()
