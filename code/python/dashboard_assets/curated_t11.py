"""Small, reproducible dashboard summaries derived from saved T11 results."""
import json
import statistics
from pathlib import Path


def read_json(root, relative):
    return json.loads((Path(root) / relative).read_text())


def source_hashes(root, paths):
    import hashlib

    return {
        path: hashlib.sha256((Path(root) / path).read_bytes()).hexdigest()
        for path in paths
    }


def quantum_planar_rows(root):
    """Summarize the accepted c=10 output and matched classical readouts."""
    root = Path(root)
    summary_path = "results/t11-quantum-planar-rotors/summary.json"
    summary = read_json(root, summary_path)
    rows = []
    for case in summary["cases"]:
        m = case["m"]
        series_path = f"results/t11-quantum-planar-rotors/quantum-m{m}-c10.json"
        quantum = read_json(root, series_path)
        late = [row for row in quantum["rows"] if 10.0 <= row["time"] <= 20.0]
        if not late:
            raise ValueError(f"No quantum late-window rows for m={m}")
        hot_entropy = statistics.mean(
            (row["entropy"][0] + row["entropy"][1]) / 2 for row in late
        )
        cold_entropy = statistics.mean(
            (row["entropy"][2] + row["entropy"][3]) / 2 for row in late
        )
        all_entropy = statistics.mean(
            value for row in late for value in row["entropy"]
        )
        rows.append({
            "display_id": f"m={m}",
            "m": m,
            "packet_energy": case["packet_energy"],
            "mean_total_energy": case["mean_total_energy"],
            "accepted_cutoff": case["accepted_cutoff"],
            "sector_dimension": case["dimension"],
            "late_quantum_cold_pair_fraction": case["quantum_late_cold_fraction"],
            "late_classical_cold_pair_fraction": case["classical_late_cold_fraction"],
            "late_quantum_entropy_hot_pair_nats": hot_entropy,
            "late_quantum_entropy_cold_pair_nats": cold_entropy,
            "late_quantum_entropy_per_rotor_nats": all_entropy,
            "max_quantum_norm_error": case["max_norm_error"],
            "max_quantum_energy_error": case["max_energy_error"],
            "max_classical_energy_error": case["classical_max_energy_error"],
            "max_classical_momentum_error": case["classical_max_momentum_error"],
            "series": f"initial momentum m={m}",
        })
    return sorted(rows, key=lambda row: row["m"])


def face_connectivity_rows(root):
    """Create explicit direct-hop and two-hop rows from saved witness records."""
    root = Path(root)
    primary_path = "results/t11-face-connectivity/L6-K3.json"
    primary = read_json(root, primary_path)
    rows = []
    for graph in ("ring", "complete"):
        graph_data = primary["graphs"][graph]
        for source_key, source_label, spin in (
            ("closed", "closed singlet", 0),
            ("open_highest_weight", "open J=3 highest weight", 3),
            ("open_M0", "open J=3, M=0", 3),
        ):
            chain = graph_data["directed_chain"][source_key]
            source_counts = chain["source_counts"]
            target5_counts = chain["target5_counts"]
            target6_counts = chain["target6_counts"]
            series = f"{graph}; {source_label}"
            common = {
                "L": primary["L"], "K": primary["K"], "graph": graph,
                "source_class": source_label, "source_spin": spin,
                "source_counts_label": "(" + ", ".join(map(str, source_counts)) + ")",
                "target5_counts_label": "(" + ", ".join(map(str, target5_counts)) + ")",
                "target6_counts_label": "(" + ", ".join(map(str, target6_counts)) + ")",
                "singlet_dimension": primary["singlet_dimension"],
                "full_dimension": primary["full_dimension"],
                "singlet_4_to_5_rank": graph_data["closed"]["4_to_5"]["rank"],
                "singlet_4_to_5_source_nullity": graph_data["closed"]["4_to_5"]["source_nullity"],
                "direct_4_to_6_block_norm": graph_data["full"]["4_to_6"]["frobenius_norm"],
                "series": series,
            }
            transitions = (
                ("4 to 5 (H)", 4, 5, "H", 1, chain["H_target5_source"]),
                ("5 to 6 (H)", 5, 6, "H", 1, chain["H_target6_target5"]),
                ("4 to 6 direct (H)", 4, 6, "H", 1,
                 0.0 if graph_data["full"]["4_to_6"]["frobenius_norm"] == 0 else None),
                ("4 to 6 through two hops (H squared)", 4, 6, "H^2", 2,
                 chain["H2_target6_source"]),
            )
            for label, start, end, operator, order, matrix_element in transitions:
                rows.append({
                    **common,
                    "display_id": f"{graph} · {source_label} · {label}",
                    "transition": label,
                    "from_active_channels": start,
                    "to_active_channels": end,
                    "operator": operator,
                    "operator_order": order,
                    "matrix_element": matrix_element,
                    "chart_matrix_magnitude": abs(matrix_element) if operator == "H" and matrix_element is not None else None,
                    "first_hop_norm": chain["first_hop_norm"],
                    "second_hop_norm": chain["second_hop_norm"],
                    "H2_target6_source": chain["H2_target6_source"],
                })

    for filename in ("L5-K3.json", "L6-K2.json"):
        control = read_json(root, f"results/t11-face-connectivity/{filename}")
        for graph in ("ring", "complete", "disconnected_receivers"):
            block = control["graphs"][graph]["closed"]["4_to_5"]
            target_count = 5 if control["K"] == 3 else 5
            rows.append({
                "display_id": f"L={control['L']}, K={control['K']} · {graph} · size control",
                "L": control["L"], "K": control["K"], "graph": graph,
                "source_class": "closed-sector block control",
                "source_spin": 0,
                "transition": "4 to 5 singlet block control",
                "from_active_channels": 4,
                "to_active_channels": target_count,
                "operator": "H",
                "operator_order": 1,
                "matrix_element": None,
                "chart_matrix_magnitude": None,
                "singlet_dimension": control["singlet_dimension"],
                "full_dimension": control["full_dimension"],
                "singlet_4_to_5_rank": block.get("rank", 0),
                "singlet_4_to_5_source_nullity": block.get("source_nullity", 0),
                "direct_4_to_6_block_norm": control["graphs"][graph]["full"]["4_to_6"]["frobenius_norm"],
                "singlet_4_to_5_block_frobenius_norm": block["frobenius_norm"],
                "series": f"{graph}; L={control['L']}, K={control['K']} control",
            })
    return rows
