"""Check delayed transfer across seeds and smaller integration steps."""
import csv,json
from t11_rotor_coupling_scan import OUT,run,table


def main():
    (OUT/'delayed-transfer-protocol.json').write_text(json.dumps(dict(
        reason='N8,r18 changes from <1% mean transfer through tau2000 to substantial transfer by tau10000; check seed and step dependence.',
        selected_after_initial_long_runs=True,
        cases=[dict(N=8,ratio=18,seed=s,duration=10000,refinement=1) for s in [1702,1703]]+
              [dict(N=8,ratio=18,seed=1701,duration=10000,refinement=2),dict(N=64,ratio=16,seed=1701,duration=10000,refinement=2)],
        note='Chaotic escape times can vary across numerical and initial-condition perturbations; do not infer a sharp escape time.'),indent=2)+'\n')
    rows=list(csv.DictReader((OUT/'summary.csv').open()))
    for seed in [1702,1703]:
        rows.extend(run(8,18,seed,duration=10000,kind='long_time'));table('summary.csv',rows)
    for n,r in [(8,18),(64,16)]:
        rows.extend(run(n,r,1701,duration=10000,refinement=2,kind='long_half_step'));table('summary.csv',rows)
        print('Completed long half-step',n,r,flush=True)

if __name__=='__main__':main()
