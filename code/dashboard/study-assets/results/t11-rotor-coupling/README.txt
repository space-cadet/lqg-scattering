# Larger-ring coupling and transfer-crossover scan

See [the illustrated physical account](../../notes/rotor-coupling-crossover.md) for the scaling derivation, cutoff definitions, measured bands and delayed-transfer result.

The study has 168 primary runs: four sizes, 14 packet-energy/coupling ratios and three seeds. An additional 29 histories test explicit physical coupling, integration steps, longer observation times and equal physical durations. There are 197 histories and 409 saved window summaries. The key result is a finite-time crossover with substantial delayed release in some apparently trapped states.

## Reproduce

From the repository root with NumPy, SciPy and clang++:

```sh
OPENBLAS_NUM_THREADS=1 PYTHONPATH=code/python python3 code/python/t11_rotor_coupling_scan.py > /tmp/t11-rotor-coupling.log 2>&1
OPENBLAS_NUM_THREADS=1 PYTHONPATH=code/python python3 code/python/extend_t11_rotor_coupling.py > /tmp/rotor-coupling-followup.log 2>&1
OPENBLAS_NUM_THREADS=1 PYTHONPATH=code/python python3 code/python/check_t11_rotor_delayed_transfer.py > /tmp/rotor-delayed-transfer.log 2>&1
OPENBLAS_NUM_THREADS=1 PYTHONPATH=code/python python3 code/python/check_t11_rotor_physical_time.py > /tmp/rotor-physical-time.log 2>&1
OPENBLAS_NUM_THREADS=1 PYTHONPATH=code/python python3 code/python/analyze_t11_rotor_coupling.py > /tmp/rotor-coupling-analysis.log 2>&1
OPENBLAS_NUM_THREADS=1 PYTHONPATH=code/python python3 -m unittest discover -s code/python -p 'test_*.py' > /tmp/rotor-coupling-tests.log 2>&1
```

Run the mutation scripts sequentially because they append to the same summary table. Each follow-up script writes its own protocol before calculation, explaining why those cases were selected. Re-running the initial driver resets the summary before the follow-ups are appended. `plot_t11_rotor_coupling.py` additionally requires Matplotlib and exports vector PDF and 300-dpi PNG.

## Protocols and analysis files

- `protocol.json`: initial scan and predefined controls.
- `followup-protocol.json`: neighboring long-time and boundary-step checks selected after seeing slow leakage.
- `delayed-transfer-protocol.json`: extra seeds and longer half-step checks selected after observing release.
- `physical-time-protocol.json`: common-physical-duration controls.
- `analysis-protocol.json`: predefined 10%/1% diagnostics, threshold sensitivity and explicitly post-inspection half-response summary.
- `summary.csv`: individual late-window means, maxima and conserved-quantity checks.
- `grouped-scan.csv`: three-seed means and ranges of the primary scan.
- `crossover-brackets.csv`: per-seed significant/suppressed brackets and secondary half-response brackets.
- `threshold-sensitivity.csv`: persistent-below-threshold grid brackets at five transfer thresholds.
- `coupling-comparison.csv`: direct physical-coupling histories versus normalized predictions; early trajectory errors and late mean differences kept separate.
- `fixed-physical-summary.csv`: matched physical late windows for seed1701 at N8,64 and lambda1,5,10.
- `step-refinement.csv`: short-window half-step sensitivity.
- `independent-validation.json`: independent energy/accounting audits over all saved arrays.
- `verification.json`, `provenance.json`, `sha256.json`: numerical evidence, runtime/source identities and artifact hashes.

## Trajectory arrays

Each local-only `.npz` contains scaled time `tau`, `readouts`, initial/final orientations and momenta, and the actual physical integration step. These large per-run archives are omitted from Git and the dashboard package. N is encoded in the name. The final `_L...` suffix is the physical coupling lambda, not system size. Prefixes distinguish primary, physical-coupling, half-step, long-time and common-physical-duration controls.

`readouts` columns are total energy; kinetic fraction; original-pair local-energy fraction; concentration; **kinetic energy outside the original pair in physical units**; total-angular-momentum norm; orientation norm error; tangency error; N local total energies; and N kinetic energies. Column4 therefore differs from the earlier ring study's spatial second moment. I=1 throughout. The reported transfer fraction divides column4 by the initial packet kinetic energy.

Primary scaled windows end at 1,000 and 2,000 and begin at 200. Longer runs also save full-duration windows. Initial potential energy is additional to the packet and is included in total energy. A finite-time transfer bracket is not an equilibrium or infinite-time localization result.

The main driver including its initial controls took approximately 57 seconds on this host; later targeted controls were separate. The full trajectory package is about 503 MiB and remains local, omitted from Git and the website. Compact summaries, protocols, validation reports and hashes are versioned; selected summaries and figures appear in the dashboard package. No remote compute was used.
