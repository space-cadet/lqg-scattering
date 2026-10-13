"""Plot the frozen U20 scan and resolve turning points from covariance."""
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import brentq

OUT=Path(__file__).resolve().parents[2]/'results/t11-size-comparison'
rows=list(csv.DictReader((OUT/'thermal_scan.csv').open()))
fig,axes=plt.subplots(1,2,figsize=(7.0,3.4),layout='constrained',sharey=True)
fig.suptitle('U/t = 20; equal mean boson occupation',fontsize=10)
extrema=[]
for ax,graph in zip(axes,['complete','ring']):
    for l,color,style in [(4,'#0072B2','-'),(5,'#D55E00','--')]:
        r=[x for x in rows if int(x['L'])==l and x['graph']==graph and x['case']=='U20'
           and 0<float(x['beta'])<float('inf')]
        beta=np.array([float(x['beta']) for x in r])
        volume=np.array([float(x['volume_per_triple']) for x in r])
        ax.plot(beta,volume,style,color=color,label=f'L={l}, K={l}')
        ground=next(x for x in rows if int(x['L'])==l and x['graph']==graph and x['case']=='U20' and float(x['beta'])==float('inf'))
        ax.plot(1e4,float(ground['volume_per_triple']),'o' if l==4 else 's',color=color,ms=4)
        archive=np.load(OUT/f'L{l}_K{l}_{graph}_U20.npz')
        e=archive['energies'];e=e-e.min();v=archive['volume_by_energy_state']
        def covariance(b):
            w=np.exp(-b*e);w/=w.sum()
            return float(w@((e-w@e)*v))
        c=np.array([covariance(b) for b in beta])
        for i in range(len(beta)-1):
            if c[i]*c[i+1]<0 and max(abs(c[i]),abs(c[i+1]))>1e-9:
                b=brentq(covariance,beta[i],beta[i+1],xtol=1e-12)
                w=np.exp(-b*e);w/=w.sum()
                extrema.append(dict(L=l,K=l,graph=graph,beta=b,mean_volume=float(w@v),
                    kind='maximum' if c[i]<0 else 'minimum'))
    ax.set_xscale('log');ax.set_xlim(1e-3,1e4)
    ax.set_title(graph.capitalize(),fontsize=10)
    ax.set_xlabel(r'$\beta t$',fontsize=10)
    ax.tick_params(labelsize=8)
    ax.grid(alpha=.2)
axes[0].set_ylabel('Mean RS volume per selected triple\n(project units)',fontsize=9)
fig.legend(*axes[0].get_legend_handles_labels(),fontsize=8,
           loc='outside lower center',ncol=2)
fig.savefig(OUT/'volume_comparison.pdf')
fig.savefig(OUT/'volume_comparison.png',dpi=300)
(OUT/'turning_points.json').write_text(json.dumps(extrema,indent=2)+'\n')
print(json.dumps(extrema,indent=2))
