"""Publication-size figure connecting thermal volume and shape readouts."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parents[2]/'results/t11-geometric-interpretation'
with (OUT/'thermal_geometry.csv').open() as f: rows=list(csv.DictReader(f))
with (OUT/'state_summary.csv').open() as f: states={r['state']:r for r in csv.DictReader(f)}
fig,axes=plt.subplots(2,2,figsize=(7,5.6),layout='constrained')
fig.suptitle('Four-face singlets: K = 4, U/t = 20',fontsize=11)
for graph,color,style in [('complete','#0072B2','-'),('ring','#D55E00','--')]:
    r=[r for r in rows if r['graph']==graph and 0<float(r['beta'])<float('inf')]
    beta=np.array([float(r['beta']) for r in r])
    for ax,key in [(axes[0,0],'volume_mean'),(axes[0,1],'four_face_probability'),
                   (axes[1,0],'conditional_angle_rms_sd')]:
        ax.plot(beta,[float(row[key]) for row in r],style,color=color,label=graph.capitalize())
    if graph=='complete':
        for key,c,s,label in [('level0_probability','#0072B2','-','Ground'),
                             ('level1_probability','#009E73','--','First excited doublet'),
                             ('other_levels_probability','#999999',':','All higher levels')]:
            values=[float(row[key])+(float(row['level2_probability']) if key=='other_levels_probability' else 0)
                    for row in r]
            axes[1,1].plot(beta,values,s,color=c,label=label)
axes[0,0].axhline(float(states['FL_phi90']['volume_mean']),color='#666666',ls=':',lw=1,label='Regular FL reference')
axes[0,0].axhline(float(states['FL_phi0']['volume_mean']),color='#999999',ls='-.',lw=1,label='Flat-input FL reference')
titles=['Positive RS volume','Four-active-face weight','Angular fluctuations, conditioned on four faces','Complete-graph energy populations']
labels=['Mean volume (project units)','Probability','RMS of six angular standard deviations','Probability']
for ax,title,label in zip(axes.flat,titles,labels):
    ax.set_xscale('log');ax.set_xlim(1e-3,1e3)
    ax.set_title(title,fontsize=9);ax.set_ylabel(label,fontsize=8)
    ax.tick_params(labelsize=8);ax.grid(alpha=.2)
    ax.set_xlabel(r'$\beta t$',fontsize=10)
axes[0,0].legend(fontsize=6.5,loc='upper right')
axes[1,1].legend(fontsize=6.5,loc='upper left')
axes[0,0].set_ylim(0,.65)
axes[1,1].set_ylim(-.02,1.4)
axes[1,1].set_yticks(np.linspace(0,1,6))
fig.savefig(OUT/'thermal_geometric_diagnostics.pdf')
fig.savefig(OUT/'thermal_geometric_diagnostics.png',dpi=300)
print('Exported vector PDF and 300-dpi PNG')
