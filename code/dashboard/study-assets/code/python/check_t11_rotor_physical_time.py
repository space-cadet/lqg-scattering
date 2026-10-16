"""Separate coupling strength from observation-clock choices."""
import csv,json
import numpy as np
from t11_rotor_coupling_scan import OUT,run,table


def main():
    (OUT/'physical-time-protocol.json').write_text(json.dumps(dict(
        purpose='Supplement matched-scaled-time coupling checks with equal physical observation durations.',
        packet_energy=100,rotor_counts=[8,64],seed=1701,couplings=[5.,10.],
        physical_duration_target=2000,rounding='scaled duration rounded to nearest0.5; physical duration error <=0.112',
        lambda1='production r100 run already has physical duration2000',
        window='scaled time>=200 through full final duration; start therefore differs in physical units',
        selected_after_main_scan=True),indent=2)+'\n')
    rows=list(csv.DictReader((OUT/'summary.csv').open()))
    for n in [8,64]:
      for g in [5.,10.]:
        duration=round(2000*np.sqrt(g)*2)/2
        rows.extend(run(n,100/g,1701,coupling=g,duration=duration,kind='fixed_physical'));table('summary.csv',rows)
        print('Completed physical-time control',n,g,flush=True)

if __name__=='__main__':main()
