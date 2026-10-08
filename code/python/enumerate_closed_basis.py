"""List orthonormal four-face singlet basis labels at fixed linear area K.

Uses the existing spin/coupling enumerator without changing its historical
J-named API. Each CSV row specifies one state, with resultant spin J=0.
"""
import argparse
import csv
import json
from pathlib import Path

from fl_volume_labels import enumerate_total_area

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k-min", type=int, default=2)
    parser.add_argument("--k-max", type=int, default=4)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results" / "closed-state-enumeration")
    args = parser.parse_args()
    if not 0 <= args.k_min <= args.k_max:
        parser.error("require 0 <= k-min <= k-max")
    rows = []
    counts = []
    for area in range(args.k_min, args.k_max + 1):
        record = enumerate_total_area(area)
        basis = []
        for assignment in record["sectors"]:
            for coupling in assignment["intermediateK"]:
                basis.append({"K": area, "state_index_at_K": len(basis) + 1,
                              **dict(zip(["j1", "j2", "j3", "j4"], assignment["spins"])),
                              "k_pair": coupling, "J_total": 0,
                              "all_four_faces_active": assignment["allFacesNonzero"]})
        expected = (area + 1) * (area + 2)**2 * (area + 3) // 12
        assert len(basis) == expected
        assert len({(r["j1"], r["j2"], r["j3"], r["j4"], r["k_pair"]) for r in basis}) == expected
        for row in basis:
            assert sum(row[f"j{i}"] for i in range(1, 5)) == area
            for a, b in [(row["j1"], row["j2"]), (row["j3"], row["j4"])]:
                assert abs(a-b) <= row["k_pair"] <= a+b
                assert (a+b-row["k_pair"]).is_integer()
        counts.append({"K": area, "basis_states": len(basis),
                       "face_spin_assignments": len(record["sectors"]),
                       "all_four_faces_active": sum(r["all_four_faces_active"] for r in basis)})
        rows.extend(basis)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"basis_k{args.k_min}_k{args.k_max}.csv"
    with (args.output_dir / filename).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.output_dir / "summary.json").write_text(json.dumps({
        "notation": "K=sum_i j_i; J_total=0; k_pair is the intermediate pair spin",
        "faces": "four labelled faces; zero-spin faces permitted",
        "basis": "couple (j1,j2) to k_pair, (j3,j4) to k_pair, then to J_total=0",
        "interpretation": "One orthonormal basis state per row; arbitrary superpositions are not separately enumerated.",
        "csv": filename, "counts": counts,
        "checks": ["dimension formula", "unique basis labels", "total area", "pair triangle inequalities and parity"]
    }, indent=2) + "\n")
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
