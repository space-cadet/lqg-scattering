"""Follow-up controls selected after observing slow leakage at r=16."""
import csv,json
from t11_rotor_coupling_scan import OUT,run,table


def main():
    (OUT/'followup-protocol.json').write_text(json.dumps(dict(
        motivation='Initial long-time controls at r16 increased transfer. Check neighboring suppressed ratios and step sensitivity at the boundary.',
        selected_after_initial_scan=True,
        half_step_cases=[[8,16],[64,16]],duration_tau_half_step=2000,
        long_time_cases=[[8,18],[64,18],[64,20]],duration_tau_long=10000,seed=1701,
        note='These are targeted controls, not additional independent seeds or a full long-time scan.'),indent=2)+'\n')
    rows=list(csv.DictReader((OUT/'summary.csv').open()))
    # Existing rows have string values; DictWriter preserves their schema.
    for n,r in [(8,16.),(64,16.)]:
        rows.extend(run(n,r,1701,refinement=2.,kind='half_step'));table('summary.csv',rows)
    for n,r in [(8,18.),(64,18.),(64,20.)]:
        rows.extend(run(n,r,1701,duration=10000.,kind='long_time'));table('summary.csv',rows)
        print('Completed long-time follow-up',n,r,flush=True)

if __name__=='__main__':main()
