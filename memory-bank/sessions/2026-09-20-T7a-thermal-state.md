# T7a Session Note: Single-Copy Thermal State
*2026-09-20 02:30 IST*

## What Happened
ORX session `chat_8f355bbc` completed T7a (single-copy thermal state experiment). Commits `b9c567c` and `b6523c8` merged into main at `ef2e9b2`.

## Numerical Results Summary
- **n=4** (dim=6435): Tr(rho_beta q) = 0 at all beta ∈ {0, 0.1, 0.5, 1, 2, 5, 10}
- **n=5** (dim=43758): Same null result
- Areas decrease with beta (thermal suppression of boundary geometry)
- Volume fluctuation q^2 → 0 as beta → ∞ (state thermalizes to vacuum)

## Files
- `t7a_thermal.py` — experiment script
- `t7a_results.json` — full numerical data

## Next
T7b (TFD construction + two-sided correlator) already has 2 commits on the same session. Monitor continues for T7b completion.
