"""Package saved studies and plots for the standalone numerics dashboard.

Run with conda run -n qc-diff python code/python/dashboard_assets/build_research_catalogue.py.
No scientific calculation is rerun. Historical figures are drawn from saved arrays.
"""
import csv
import argparse
import gzip
import hashlib
import json
import math
import re
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from curated_t11 import face_connectivity_rows, quantum_planar_rows, source_hashes

ROOT = Path(__file__).resolve().parents[3]
DASH = ROOT / "code/dashboard"
HISTORY = ROOT / "figures/dashboard-history"
STUDIES = []
PLOT_SOURCES = {}
FIGURE_TITLES = {
    "ground_energy_vs_repulsion":"Ground energy versus onsite repulsion",
    "ground_energy_graph_difference":"Ground-energy difference: complete graph minus ring",
    "thermal_volume_u5":"Thermal volume at U/t=5",
    "k4_thermal_volume_scan":"K=4 mean volume and zero-volume probability versus inverse temperature",
    "k4_low_energy_volume_spectrum":"K=4 volume of low-energy eigenspaces",
    "basis_state_volumes_k2_k4":"Four-face recoupling-basis volume expectations, K=2,3,4",
    "fixed_area_ensemble_volume":"Equal-weight complete closed-basis volume versus area",
    "regular_volume_area":"Regular FL state volume versus area",
    "weighted_volume_area":"Weighted FL state volume versus area",
    "closed_state_counts":"Closed, zero-volume and positive-volume state counts",
    "rs_volume_distributions":"Variable-face RS volume eigenvalue distributions",
    "rs_volume_means":"Variable-face mean RS volume",
    "thermal_coefficients_vacuum":"Squeezed-vacuum area-sector distributions",
    "thermal_vacuum_spin":"Vacuum-seed per-copy resultant-spin distributions",
    "j1_spin_joint_maps":"Excited-seed joint boson-number and resultant-spin distributions",
    "j1_spin_temperature":"Excited-seed area and spin distributions versus temperature",
    "volume_comparison":"Four versus five sites: volume per selected triple at U/t=20",
    "thermal_geometric_diagnostics":"Four-face FL references and thermal geometric diagnostics",
    "four-and-five-site-graphs":"Complete and ring interaction graphs, with one selected volume triple",
    "candidate_ground_energy_shifts":"Hamiltonian ground-energy shifts relative to the baseline",
    "candidate_ground_state_response":"Ground-state volume and signed-grasp response",
    "candidate_thermal_response_u20":"Thermal volume and grasp response at U/t=20",
    "ring_topology_control":"Ring hopping topology control",
    "prepared_FL_early_dynamics_u20":"Early evolution of prepared FL states at U/t=20",
    "rotor-dynamics":"Packet spreading and persistent high-energy concentration",
    "rotor-scaling":"Rotor-size and preparation comparison",
    "few-rotor-transfer":"Planar-pair transfer and three-dimensional controls",
    "coupling-crossover":"Finite-time coupling crossover and delayed release",
    "energy-transfer":"Quantum and matched classical planar-rotor energy transfer",
    "area-transfer":"Area redistribution across exact singlet trajectories",
    "geometry-and-activation":"Geometry samples and active-channel redistribution",
}


def read(path):
    return json.loads((ROOT / path).read_text())


def csv_records(path):
    with (ROOT / path).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def csv_value(value):
    if value == "":
        return None
    if value in ("True", "False"):
        return value == "True"
    if re.fullmatch(r"[+-]?\d+", value):
        return int(value)
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except ValueError:
        return value


def clean(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    return value


def export(source):
    source = Path(source)
    target = DASH / "study-assets" / source
    if source.parts[0] == "memory-bank":
        # Deployment also excludes directories named memory-bank.
        target = DASH / "study-assets" / "study-records" / Path(*source.parts[1:])
    # The website deployment excludes *.md. Serve the same bytes as text,
    # retaining the original source name in the download manifest.
    if source.suffix == ".md":
        target = target.with_suffix(".txt")
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix == ".json":
        target.write_text(json.dumps(clean(read(source)), indent=2, allow_nan=False) + "\n")
    else:
        shutil.copy2(ROOT / source, target)
    return {"name": source.name, "path": target.relative_to(DASH).as_posix(),
            "source": source.as_posix(),
            "sourceSha256": hashlib.sha256((ROOT / source).read_bytes()).hexdigest()}


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def export_gzip(source):
    source = Path(source)
    raw = ROOT / source
    target = DASH / "study-assets" / source
    target = target.with_name(target.name + ".gz")
    target.parent.mkdir(parents=True, exist_ok=True)
    with raw.open("rb") as input_stream, target.open("wb") as output_stream:
        with gzip.GzipFile(filename="", mode="wb", fileobj=output_stream, compresslevel=6, mtime=0) as compressed:
            shutil.copyfileobj(input_stream, compressed, length=1024 * 1024)
    return {"name": source.name + ".gz", "path": target.relative_to(DASH).as_posix(),
            "source": source.as_posix(), "sourceSha256": sha256_file(raw),
            "packageSha256": sha256_file(target), "compression": "gzip"}


def plot(name, title, xlabel, ylabel, series, sources, xlog=False, ylog=False):
    fig, ax = plt.subplots(figsize=(7.2, 3.6), layout="constrained")
    for index, (label, xs, ys) in enumerate(series):
        ax.plot(xs, ys, label=label, marker=["o", "s", "^", "D"][index % 4],
                linestyle=["-", "--", "-.", ":"][index % 4], markersize=4)
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    if xlog:
        ax.set_xscale("log")
    if ylog:
        ax.set_yscale("log")
    ax.grid(alpha=.22)
    if len(series) > 4:
        fig.set_size_inches(7.2, 4.8)
        ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(.5, -.2), ncol=2)
    else:
        ax.legend(fontsize=8, loc="best")
    HISTORY.mkdir(parents=True, exist_ok=True)
    for ext in ["pdf", "png"]:
        fig.savefig(HISTORY / f"{name}.{ext}", dpi=300)
    plt.close(fig)
    PLOT_SOURCES[name] = sources


def historical_plots():
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "pdf.fonttype": 42})
    d = read("results/t5a_mag_results.json")
    rows = sorted(d["results"], key=lambda x: x["M"])
    plot("magnetization", "Magnetization pilot: signed triple-grasp magnitudes", "Magnetization M",
         "Mean / maximum absolute signed grasp", [(field, [r["M"] for r in rows], [r[field] for r in rows])
         for field in ["mean_abs", "max_abs"]], ["results/t5a_mag_results.json"])
    d = read("results/t5a_prime_results.json")
    plot("chirality", "Local-chirality pilot: agreement over sampled planes", "Valence n", "Mean sign agreement",
         [(channel, [r["n"] for r in d["runs"] if r["channel"] == channel],
           [r["mean_agree_all"] for r in d["runs"] if r["channel"] == channel])
          for channel in sorted({r["channel"] for r in d["runs"]})], ["results/t5a_prime_results.json"])
    d = read("results/t5b_results.json")
    plot("perturbation", "Imaginary perturbation: signed-mean proxy", "Perturbation epsilon", "Proxy (project units)",
         [(f"n={n}", r["eps"], r["V"]) for n, r in d["n"].items()], ["results/t5b_results.json"], True, True)
    d = read("results/t5d_phase_scan_results.json")
    rows = sorted(d["points"], key=lambda x: x["phaseDefect"])
    plot("phase", "Cocycle-phase pilot", "Gauge-invariant phase defect", "Signed grasp q012",
         [("Saved samples", [r["phaseDefect"] for r in rows], [r["signedGrasp"] for r in rows])],
         ["results/t5d_phase_scan_results.json"])
    d = read("results/t5e_results.json")
    plot("large_k", "Recorded large-K families: signed-mean proxy", "Historical K (total boson number)", "Proxy (project units)",
         [(label, [r["K"] for r in f["points"]], [r["V"] for r in f["points"]])
          for label, f in d["families"].items()], ["results/t5e_results.json"], True, True)
    for stem, key, ylabel in [("t7a", "q2", "Gibbs mean squared grasp"),
                              ("t7b", "corr", "Two-copy grasp correlation")]:
        d = read(f"results/{stem}_results.json")
        series = []
        for n, case in d["n"].items():
            rows = case["rows"]
            series.append((f"n={n}", [r["beta"] for r in rows],
                           [r["gibbs"][key] if stem == "t7a" else r[key] for r in rows]))
        plot(stem, "Historical capped-Fock thermal study", "Inverse temperature beta", ylabel, series,
             [f"results/{stem}_results.json"])
    d = read("results/t7e_results.json")
    plot("t7e", "Historical complexified purification", "Perturbation epsilon", "Saved correlation at beta=1",
         [(f"n={n}", [r["eps"] for r in c["rows"]], [r["corr"]["1.0"] for r in c["rows"]])
          for n, c in d["n"].items()], ["results/t7e_results.json"], True)
    d = read("results/t7_geometry_thermal_results.json")
    series = []
    for c in d["cases"]:
        for model, label in [("unprojected_draft", "draft"), ("double_singlet_conditional_candidate", "postselected")]:
            series.append((f'{c["shape"]}, J={c["J"]}, {label}', [r["beta"] for r in c["rows"]],
                           [r[model]["V_RS"] for r in c["rows"]]))
    plot("geometry_audit", "Small-sector geometry audit: distinct state constructions", "Inverse temperature beta",
         "Mean positive RS volume (project units)", series, ["results/t7_geometry_thermal_results.json"])
    d = read("results/t5c_degenerate_limits_highJ_results.json")
    series = []
    for phi in sorted({r["phiRadians"] for r in d["pythonResults"]}):
        rows = sorted([r for r in d["pythonResults"] if r["phiRadians"] == phi], key=lambda r:r["J"])
        series.append((f"Python, phi={phi:g}", [r["J"] for r in rows], [r["rs"]["geometryMatchedMeanOverJ32"] for r in rows]))
    for field in ["rsGeometryMatched", "alGeometryMatched"]:
        rows = sorted([r for r in d["rustResults"] if r["phiRadians"] == 0], key=lambda r:r["J"])
        series.append((f"Rust flat, {field[:2].upper()}", [r["J"] for r in rows], [r[field] for r in rows]))
    plot("high_j_boundary", "Higher-J boundary probes (RS comparison unresolved at J=10)", "FL area label J",
         "Geometry-matched positive mean / J^(3/2)", series, ["results/t5c_degenerate_limits_highJ_results.json"])
    d = read("results/volume_prescription_results.json")["results"]
    plot("volume_controls", "Positive-volume implementation controls", "Control state", "Volume (project units)",
         [(label, ["Paired singlet", "Collinear product"],
           [d["paired_spin_half_singlet"][key], d["collinear_up_product"][key]])
          for label, key in [("Positive RS", "rovelli_smolin"), ("Positive AL", "ashtekar_lewandowski")]],
         ["results/volume_prescription_results.json"])
    d = read("results/t5c_covariance_probe_results.json")["records"]
    plot("covariance_pilot", "Initial flux-Gram shape diagnostic", "FL area label J", "Maximum normalized-Gram error",
         [(shape, [r["J"] for r in d if r["shape"] == shape],
           [r["normalizedGramMaxAbsDifferenceFromInputNormals"] for r in d if r["shape"] == shape])
          for shape in sorted({r["shape"] for r in d})], ["results/t5c_covariance_probe_results.json"])
    (HISTORY / "plot_summary.json").write_text(json.dumps({"method": "plots of saved arrays; no physics rerun", "matplotlib": matplotlib.__version__, "png_dpi": 300,
        "plots": {k:[{"path":p,"sha256":hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in v] for k,v in PLOT_SOURCES.items()}}, indent=2)+"\n")


def add(identifier, task, title, description, limits, sources, figures=(), table=None, status="Saved calculation", catalogue_date="2026-10-09", compressed_sources=(), chart=None, source_hashes_map=None, document_notes=None):
    files = []
    for source in sources:
        path = ROOT / source
        if path.is_dir():
            files.extend(export(p.relative_to(ROOT)) for p in sorted(path.iterdir()) if p.is_file() and p.suffix in [".json", ".csv", ".md", ".npz"])
        else:
            files.append(export(source))
    files.extend(export_gzip(source) for source in compressed_sources)
    images = []
    for source in figures:
        path = ROOT / source
        candidates = sorted(path.glob("*.png")) if path.is_dir() else [path]
        for candidate in candidates:
            item = export(candidate.relative_to(ROOT))
            item["title"] = FIGURE_TITLES.get(candidate.stem, candidate.stem.replace("_", " ").capitalize())
            with Image.open(candidate) as image:
                item["width"], item["height"] = image.size
            item["wide"] = item["width"] / item["height"] >= 2.3
            pdf = candidate.with_suffix(".pdf")
            if pdf.exists():
                item["pdf"] = export(pdf.relative_to(ROOT))["path"]
            images.append(item)
    study = {"id":identifier,"task":task,"title":title,"description":description,
             "limits":limits,"status":status,"catalogueDate":catalogue_date,
             "files":files,"figures":images,"table":table}
    if source_hashes_map:
        study["sourceHashes"] = source_hashes_map
    if document_notes is not None:
        study["documentNotes"] = document_notes
    if chart:
        study["chart"] = chart
    STUDIES.append(study)


def prune_curated_result_copies():
    """Remove old generated dashboard copies of arrays excluded from the release."""
    keep_by_directory = {
        "results/fl-face-activation": {"README.txt", "protocol.json", "provenance.json", "summary.csv", "verification.json"},
        "results/thermal-closed-entanglement": {"README.txt", "protocol.json", "provenance.json", "temperature_summary.csv", "verification.json"},
        "results/thermal-closure-temperature": {"README.txt", "closure_temperature.csv", "protocol.json", "verification.json"},
        "results/thermal-closed-projection": {"README.txt", "area_distribution.csv", "protocol.json", "temperature_fit.json", "temperature_summary.csv", "verification.json"},
        "results/thermal-j1-spin": {"j1_spin_method_summary.json"},
        "results/t9a-singlet-exchange": {"README.txt", "ground_states.csv", "independent_verification.json", "provenance.json", "summary.json", "thermal.csv"},
        "results/t11-equilibration": {"README.txt", "independent-validation.json", "protocol.json", "provenance.json", "summary.csv", "validation.json"},
        "results/t11-classical-rotors": {"README.txt", "analysis-protocol.json", "grouped-summary.csv", "independent-validation.json", "protocol.json", "provenance.json", "verification.json"},
        "results/t11-few-rotors": {"README.txt", "few-summary.csv", "pair-summary.csv", "protocol.json", "provenance.json", "validation.json", "verification.json"},
        "results/t11-rotor-coupling": {"README.txt", "analysis-protocol.json", "coupling-comparison.csv", "crossover-brackets.csv", "delayed-transfer-protocol.json", "fixed-physical-summary.csv", "followup-protocol.json", "grouped-scan.csv", "independent-validation.json", "physical-time-protocol.json", "protocol.json", "provenance.json", "threshold-sensitivity.csv", "verification.json"},
    }
    for relative, keep in keep_by_directory.items():
        package_directory = DASH / "study-assets" / relative
        if not package_directory.exists():
            continue
        for path in package_directory.rglob("*"):
            if path.is_file() and path.name not in keep:
                path.unlink()
        for path in sorted(package_directory.rglob("*"), reverse=True):
            if path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    pass


def main(reuse_history=False):
    if not reuse_history:
        historical_plots()
    prune_curated_result_copies()

    # Keep the finite-area channel pilot separate from the classical rotor
    # results. These rows are selected from the saved late-window summaries.
    channel_source = "results/t11-equilibration/summary.csv"
    channel_rows = []
    for source_row in csv_records(channel_source):
        if int(source_row["K"]) != 3 or float(source_row["window_end"]) != 200:
            continue
        phase = source_row["phase"]
        interaction = float(source_row["U"])
        if phase == "regular" or (phase == "phase_shifted" and interaction == 5):
            channels = int(source_row["L"])
            channel_rows.append({
                "channels": channels, "K": 3, "U": interaction,
                "phase": phase, "window_end": 200,
                "residence_fraction_0_05": float(source_row["residence_0.05"]),
                "mean_readout_distance": float(source_row["mean_distance"]),
                "mean_concentration": float(source_row["mean_concentration"]),
                "dephased_concentration": float(source_row["dephased_concentration"]),
                "active_count_TV_from_canonical": float(source_row["canonical_active_count_TV"]),
                "maximum_return_after_20": float(source_row["max_return_after20"]),
                "series": f"{phase.replace('_', ' ')}, U={interaction:g}",
            })
    channel_rows.sort(key=lambda row: (row["phase"] != "regular", row["U"], row["channels"]))
    add("t11-channel-equilibration", "T11", "Small-area face-channel equilibration pilot",
        "Representative K=3 late-window readouts from the finite-area quantum pilot. The regular input covers L=4,5,6 at U=0,1,5; a phase-shifted U=5 control shows preparation dependence. The study asks how readouts approach the exact dephased reference, not whether a canonical state is reached.",
        "Finite K=2,3 sectors, uniform complete-graph hopping with fixed row sum, two FL phase choices, three interaction strengths, and selected windows ending at t=200. Residence depends on the readout tolerance and observation window; phase-shifted cases are not energy matched. No large-area equilibration claim.",
        ["results/t11-equilibration/README.md", "results/t11-equilibration/protocol.json",
         "results/t11-equilibration/provenance.json", channel_source,
         "results/t11-equilibration/validation.json", "results/t11-equilibration/independent-validation.json",
         "notes/classical-rotor-equilibration.md", "code/python/t11_equilibration.py",
         "code/python/verify_t11_equilibration.py"],
        table={"columns": list(channel_rows[0]), "rows": channel_rows},
        status="42 trajectories passed; 252,840 independent comparisons (714 analytic); maximum residual 1.88e-13; prior 46-test suite passed",
        catalogue_date="2026-10-16",
        chart={"type": "line", "x": "parameters.channels", "y": "results.residence_fraction_0_05",
               "groupBy": "results.series",
               "labels": {"parameters.channels": "Available face channels L",
                          "results.residence_fraction_0_05": "Residence near the dephased readout, d ≤ 0.05",
                          "results.series": "Input phase and interaction U"}})

    # The compact grouped table averages three orientation seeds and preserves
    # the two different packet preparations as separate chart series.
    rotor_source = "results/t11-classical-rotors/grouped-summary.csv"
    rotor_rows = []
    for source_row in csv_records(rotor_source):
        ratio = float(source_row["ratio"])
        preparation = source_row["scaling"]
        preparation_label = "fixed packet" if preparation == "fixed_packet" else "fixed energy density"
        rotor_rows.append({
            "N": int(source_row["N"]), "packet_scale_at_N8": ratio,
            "preparation": preparation, "seed_count": int(source_row["seeds"]),
            "equilibrium_hot_fraction": float(source_row["equilibrium_hot"]),
            "hot_pair_fraction_mean": float(source_row["mean_hot_fraction_mean"]),
            "hot_pair_fraction_min": float(source_row["mean_hot_fraction_min"]),
            "hot_pair_fraction_max": float(source_row["mean_hot_fraction_max"]),
            "participation_fraction_mean": float(source_row["mean_participation_fraction_mean"]),
            "equilibrium_participation_fraction_mean": float(source_row["reference_participation_fraction_mean"]),
            "equilibrium_region90_residence_mean": float(source_row["residence_region90_mean"]),
            "equilibrium_region90_residence_min": float(source_row["residence_region90_min"]),
            "equilibrium_region90_residence_max": float(source_row["residence_region90_max"]),
            "hot_fraction_KS_mean": float(source_row["hot_fraction_KS_mean"]),
            "series": f"{preparation_label}; packet scale at N=8: {ratio:g}",
        })
    rotor_rows.sort(key=lambda row: (row["preparation"], row["packet_scale_at_N8"], row["N"]))
    add("classical-rotor-equilibration", "T11", "Classical rotor spreading and equilibrium comparison",
        "Grouped late-time summaries compare four ring sizes, three packet-energy scales and fixed-packet versus fixed-density preparation. At packet energy 10, the hot-pair fraction follows the microcanonical value 2/N and equilibrium-region residence is 87.2–90.4%. At packet energy 100, the hot pair retains 98.7–99.0% of local energy through t=2000.",
        "Classical I=1 nearest-neighbor rings, equal-and-opposite initial hot pair, three related orientation seeds, and finite observation windows. The fixed-density series raises the initial packet energy with N; N=8 cases overlap between preparations. Late-time trapping is not permanent localization, and no quantum rotor evolution is included.",
        ["results/t11-classical-rotors/README.md", "results/t11-classical-rotors/protocol.json",
         "results/t11-classical-rotors/analysis-protocol.json", rotor_source,
         "results/t11-classical-rotors/provenance.json", "results/t11-classical-rotors/verification.json",
         "results/t11-classical-rotors/independent-validation.json",
         "results/t11-equilibration/README.md", "notes/classical-rotor-equilibration.md",
         "notes/few-rotor-energy-transfer.md", "notes/rotor-coupling-crossover.md",
         "code/python/t11_classical_rotors.py", "code/python/analyze_t11_classical_rotors.py",
         "code/python/verify_t11_classical_rotors.py", "code/python/plot_t11_classical_rotors.py",
         "code/python/lqg_scattering/classical_rotors.py", "code/python/t11_equilibration.py",
         "code/python/verify_t11_equilibration.py"],
        ["figures/t11-classical-rotors"],
        {"columns": list(rotor_rows[0]), "rows": rotor_rows},
        status="72 production runs (63 unique preparations), 144 microcanonical chains, and ten full-duration half-step controls; verification records included",
        catalogue_date="2026-10-16",
        chart={"type": "line", "x": "parameters.N", "y": "results.hot_pair_fraction_mean",
               "groupBy": "results.series",
               "labels": {"parameters.N": "Rotors N",
                          "results.hot_pair_fraction_mean": "Late-time hot-pair local-energy fraction",
                          "results.series": "Packet preparation and energy scale"}})

    # Keep the exact planar benchmark and one representative three-dimensional
    # seed in distinct series. Their ratios are compatible, while their
    # conserved quantities and preparation types remain explicitly labelled.
    pair_source = "results/t11-few-rotors/pair-summary.csv"
    graph_source = "results/t11-few-rotors/few-summary.csv"
    pair_samples = {1.0, 3.9, 4.0, 4.1, 10.0, 100.0}
    few_rows = []
    selected_pair_keys = set()
    for source_row in csv_records(pair_source):
        ratio = float(source_row["ratio"])
        if ratio not in pair_samples:
            continue
        key = ratio
        if key in selected_pair_keys:
            continue
        selected_pair_keys.add(key)
        few_rows.append({
            "rotor_count": 2, "graph": "planar_pair",
            "coupling": float(source_row["coupling"]), "initial_packet_energy": float(source_row["T0"]),
            "energy_coupling_ratio": ratio, "control_type": "aligned planar pair; one initially resting rotor",
            "regime": source_row["regime"],
            "maximum_transfer_fraction": float(source_row["sampled_max_receiver_fraction"]),
            "exact_transfer_bound_fraction": float(source_row["exact_max_receiver_fraction"]),
            "mean_transfer_fraction": float(source_row["mean_receiver_fraction"]),
            "series": "N=2 planar pair; sampled maxima",
        })
    for source_row in csv_records(graph_source):
        if source_row["seed"] != "1701":
            continue
        graph = source_row["graph"]
        rotor_count = 3 if graph == "triangle" else 4
        graph_label = {"triangle": "triangle", "four_open": "open chain", "four_ring": "ring"}[graph]
        coupling = float(source_row["coupling"])
        few_rows.append({
            "rotor_count": rotor_count, "graph": graph,
            "coupling": coupling, "initial_packet_energy": float(source_row["packet_energy"]),
            "energy_coupling_ratio": float(source_row["ratio"]),
            "control_type": "3D zero-total-angular-momentum; equal-and-opposite hot pair; seed 1701",
            "regime": "three-dimensional control",
            "maximum_transfer_fraction": float(source_row["maximum_cold_kinetic_over_initial_packet"]),
            "mean_transfer_fraction": float(source_row["mean_cold_kinetic_over_initial_packet"]),
            "series": f"N={rotor_count} {graph_label}; 3D control; seed 1701",
        })
    few_rows.sort(key=lambda row: (row["control_type"].startswith("3D"), row["graph"], row["energy_coupling_ratio"]))
    add("few-rotor-energy-transfer", "T11", "Few-rotor transfer: planar bound and 3D controls",
        "Six representative planar-pair ratios sample the exact pendulum bound and its numerical check. Three-dimensional zero-angular-momentum controls use seed 1701 across a triangle, open four-rotor chain and four-rotor ring at seven couplings. The common chart parameter is initial packet energy divided by coupling; series keep rotor count, topology and preparation separate.",
        "The planar pair is aligned and has one initially resting rotor; its exact threshold is T0=4λ and its maximum is an all-time bound. The 3D controls instead start with an equal-and-opposite hot pair and summarize finite-time cold kinetic energy. Their preparations and conserved quantities differ; they do not establish thermalization. The figure bands use all three seeds, while this downloadable sample fixes seed 1701.",
        ["results/t11-few-rotors/README.md", "results/t11-few-rotors/protocol.json",
         "results/t11-few-rotors/provenance.json", pair_source, graph_source,
         "results/t11-few-rotors/validation.json", "results/t11-few-rotors/verification.json",
         "notes/few-rotor-energy-transfer.md", "notes/classical-rotor-equilibration.md",
         "code/python/t11_few_rotors.py", "code/python/plot_t11_few_rotors.py",
         "code/python/test_few_rotors.py", "code/python/lqg_scattering/classical_rotors.py"],
        ["figures/t11-few-rotors"],
        {"columns": list(few_rows[0]), "rows": few_rows},
        status="14 planar-pair runs and 63 three-dimensional runs; six half-step controls, a symmetric-triangle control, and scalar-ODE/conservation checks recorded",
        catalogue_date="2026-10-16",
        chart={"type": "line", "x": "parameters.energy_coupling_ratio", "y": "results.maximum_transfer_fraction",
               "groupBy": "results.series",
               "labels": {"parameters.energy_coupling_ratio": "Initial packet energy / coupling",
                          "results.maximum_transfer_fraction": "Maximum receiver kinetic-energy fraction",
                          "results.series": "Rotor count and control type"}})

    # Plot the full three-seed ratio summary at the saved late window and add
    # the eight direct-coupling checks as distinct fixed-physical-time series.
    coupling_source = "results/t11-rotor-coupling/grouped-scan.csv"
    direct_source = "results/t11-rotor-coupling/coupling-comparison.csv"
    coupling_rows = []
    for source_row in csv_records(coupling_source):
        if float(source_row["window_end"]) != 2000:
            continue
        rotor_count = int(source_row["N"])
        ratio = float(source_row["ratio"])
        coupling_rows.append({
            "N": rotor_count, "energy_coupling_ratio": ratio, "coupling": 1.0,
            "initial_packet_energy": ratio, "seed_count": 3,
            "control_type": "primary scaled-time scan; λ=1; three seeds",
            "mean_transfer_fraction": float(source_row["mean"]),
            "transfer_fraction_min": float(source_row["minimum"]),
            "transfer_fraction_max": float(source_row["maximum"]),
            "series": f"N={rotor_count}; primary scaled-time scan",
        })
    for source_row in csv_records(direct_source):
        rotor_count = int(source_row["N"])
        coupling = float(source_row["coupling"])
        coupling_rows.append({
            "N": rotor_count, "energy_coupling_ratio": float(source_row["ratio"]),
            "coupling": coupling, "initial_packet_energy": float(source_row["packet_energy"]),
            "seed": 1701, "control_type": "direct coupling; fixed physical-time window; seed 1701",
            "mean_transfer_fraction": float(source_row["direct_mean"]),
            "equivalent_scaled_mean": float(source_row["normalized_mean"]),
            "early_scaled_history_max_error": float(source_row["early_max_transfer_error"]),
            "late_mean_difference": float(source_row["late_mean_error"]),
            "series": f"N={rotor_count}; direct coupling control",
        })
    coupling_rows.sort(key=lambda row: (row["N"], row["control_type"].startswith("direct"), row["energy_coupling_ratio"]))
    add("rotor-coupling-crossover", "T11", "Rotor coupling crossover and delayed release",
        "The dashboard plots 56 grouped three-seed cases at the primary late window, plus eight direct-coupling checks. The ratio scan spans N=8,16,32,64 and 14 packet-energy-to-coupling ratios; separate direct controls vary λ at fixed packet energy and physical observation time.",
        "Three related orientation seeds and one equal-and-opposite hot-pair preparation. Significant/suppressed thresholds and the post-inspection half-response bracket are finite-grid diagnostics, not phase-transition estimates. Longer trajectories show delayed transfer, but release timing is step-sensitive; neither permanent localization nor universal equilibration is established.",
        ["results/t11-rotor-coupling/README.md", "results/t11-rotor-coupling/protocol.json",
         "results/t11-rotor-coupling/analysis-protocol.json", coupling_source, direct_source,
         "results/t11-rotor-coupling/fixed-physical-summary.csv",
         "results/t11-rotor-coupling/crossover-brackets.csv",
         "results/t11-rotor-coupling/threshold-sensitivity.csv",
         "results/t11-rotor-coupling/followup-protocol.json",
         "results/t11-rotor-coupling/delayed-transfer-protocol.json",
         "results/t11-rotor-coupling/physical-time-protocol.json",
         "results/t11-rotor-coupling/provenance.json",
         "results/t11-rotor-coupling/independent-validation.json",
         "results/t11-rotor-coupling/verification.json",
         "notes/rotor-coupling-crossover.md", "notes/classical-rotor-equilibration.md",
         "code/python/t11_rotor_coupling_scan.py", "code/python/analyze_t11_rotor_coupling.py",
         "code/python/plot_t11_rotor_coupling.py", "code/python/extend_t11_rotor_coupling.py",
         "code/python/check_t11_rotor_delayed_transfer.py", "code/python/check_t11_rotor_physical_time.py",
         "code/python/lqg_scattering/classical_rotors.py"],
        ["figures/t11-rotor-coupling"],
        {"columns": list(coupling_rows[0]), "rows": coupling_rows},
        status="168 primary trajectories plus 29 follow-up histories; 409 window summaries; finite-time brackets and delayed-transfer checks recorded",
        catalogue_date="2026-10-16",
        chart={"type": "line", "x": "parameters.energy_coupling_ratio", "y": "results.mean_transfer_fraction",
               "groupBy": "results.series",
               "labels": {"parameters.energy_coupling_ratio": "Initial packet energy / coupling",
                          "results.mean_transfer_fraction": "Mean transferred kinetic-energy fraction",
                          "results.series": "Rotor count and observation/control protocol"}})

    export('notes/face-energy-equipartition.md')
    add('fl-face-activation', 'T11', 'Large-area tetrahedron: face activation and recurrence',
        'Exact FL free-hopping control on five/six channels, with four initial tetrahedral spinors and vacuum extras. Twenty controls span K=2..10000 and two phase choices. A fifth channel can take 29.06% of area, while individual areas and local energies recur.',
        'Unit complete-graph hopping, U=0, pure FL manifold. Direct sparse occupation evolution verifies K=1,2. No irreversible equipartition or interacting thermalization established. The two extra symmetric six-channel rows have the same normal, leaving only five distinct classical directions. Phase controls have different conserved initial energies.',
        ['results/fl-face-activation/README.md', 'results/fl-face-activation/protocol.json',
         'results/fl-face-activation/provenance.json', 'results/fl-face-activation/summary.csv',
         'results/fl-face-activation/verification.json', 'notes/face-energy-equipartition.md',
         'code/python/fl_face_activation.py','code/python/verify_fl_face_activation.py',
         'code/python/plot_fl_face_activation.py','code/python/lqg_scattering/intertwiners.py',
         'code/python/lqg_scattering/spinors.py'],
        ['figures/fl-face-activation'],status='360 direct-state, occupation, energy, geometry and recurrence checks passed',
        catalogue_date='2026-10-16')
    add('thermal-closed-entanglement', 'T9', 'Entanglement of separately closed thermal polyhedra',
        '86 temperatures over T*=0.05..5. Exact Schmidt eigenvalues and multiplicities yield entropy, area-sector decomposition, purity, Renyi-2 entropy and coherent joint singlet creation. Within-area entanglement exceeds area-distribution entropy at T*=1,2,5.',
        'Normalized double-singlet projection of the area-one F12 reference; initially only two active faces. Ordinary left/right tensor factorization. Adaptive area cutoffs 12..140; entropy truncation estimate below 6.4e-12 nats. Temperature slopes are prepared-state responses; fixed single-copy Gibbs and AdS interpretations are not assumed. General four-face FL inputs remain open.',
        ['results/thermal-closed-entanglement/README.md',
         'results/thermal-closed-entanglement/temperature_summary.csv',
         'results/thermal-closed-entanglement/protocol.json',
         'results/thermal-closed-entanglement/provenance.json',
         'results/thermal-closed-entanglement/verification.json',
         'notes/thermal-entanglement.md', 'notes/thermal-geometry-and-singlet-exchange.md',
         'code/python/lqg_scattering/thermal_projection.py', 'code/python/lqg_scattering/thermal_entanglement.py',
         'code/thermal/closed_entanglement_study.py', 'code/thermal/verify_closed_entanglement.py',
         'code/thermal/plot_closed_entanglement.py'],
        ['figures/thermal-closed-entanglement'],
        status='802 oscillator, spectrum, geometry and convergence comparisons passed', catalogue_date='2026-10-16')
    add('thermal-closure-temperature', 'T9', 'Ordinary closure versus temperature',
        '125 temperatures quantify per-copy Gauss defect and declining singlet fraction for the selected area-one two-copy reference.',
        'Ordinary per-copy closure differs from combined dual-copy and transformed closure. Full unprojected oscillator state; temperature is the squeeze preparation parameter.',
        ['results/thermal-closure-temperature/README.md',
         'results/thermal-closure-temperature/closure_temperature.csv',
         'results/thermal-closure-temperature/protocol.json',
         'results/thermal-closure-temperature/verification.json',
         'notes/thermal-geometry-and-singlet-exchange.md',
         'code/thermal/closure_temperature_sweep.py'],
        ['figures/thermal-closure-temperature'], catalogue_date='2026-10-13')
    add('thermal-closed-projection', 'T9', 'Heating separately closed area and positive RS volume',
        '85 temperatures over T*=0.05..2: retained probability, conditional area and positive RS-volume distributions. Exact high-temperature mean-area coefficient 57/14.',
        'F12 reference with separate singlet projection. Volume traces through area 50 and occupation probabilities through q=160; model RS units. The fixed-H Gibbs obstruction applies to this reference.',
        ['results/thermal-closed-projection/README.md',
         'results/thermal-closed-projection/area_distribution.csv',
         'results/thermal-closed-projection/protocol.json',
         'results/thermal-closed-projection/temperature_fit.json',
         'results/thermal-closed-projection/temperature_summary.csv',
         'results/thermal-closed-projection/verification.json',
         'notes/thermal-geometry-and-singlet-exchange.md',
         'code/thermal/closed_projection_study.py', 'code/thermal/fit_closed_temperature.py',
         'code/thermal/plot_closed_temperature_writeup.py',
         'code/python/lqg_scattering/thermal_projection.py'],
        ['figures/thermal-closed-projection'], catalogue_date='2026-10-13')
    add('t9a-singlet-exchange', 'T9a', 'Singlet exchange between closed FL polyhedra',
        'Fixed combined area K=4, dimension 1210; four Hamiltonians and three FL inputs. Twelve trajectories follow area current, entropy, coherence and positive RS volume; twenty canonical controls retain full joint Gibbs entropy.',
        'Finite isolated pair; prepared-state entanglement differs from mixed-state Gibbs entropy. No reservoir relaxation or equivalence to the T9 squeezed family established. Project volume and model energy units.',
        ['results/t9a-singlet-exchange/README.md',
         'results/t9a-singlet-exchange/ground_states.csv',
         'results/t9a-singlet-exchange/independent_verification.json',
         'results/t9a-singlet-exchange/provenance.json',
         'results/t9a-singlet-exchange/summary.json',
         'results/t9a-singlet-exchange/thermal.csv',
         'notes/t9a-singlet-exchange.md', 'notes/thermal-geometry-and-singlet-exchange.md'],
        ['figures/t9a-singlet-exchange'],
        status='46 recorded regression tests and 1792 independent comparisons passed', catalogue_date='2026-10-14')
    size_rows = list(csv.DictReader((ROOT / "results/t11-size-comparison/summary.csv").open()))
    add("t11-size-comparison", "T11", "Four versus five sites: thermal-volume persistence",
        "Matched mean occupation 2K/L=2: (L,K)=(4,4) and (5,5), singlet dimensions 105 and 1,176. Complete and ring graphs at t=1,U=20, plus free and no-hopping controls. Intermediate-temperature nonmonotonicity persists; the pronounced four-site complete-graph low-temperature collapse does not.",
        "The plot reports volume per selected triple; CSV files also retain total volume. Triple counts: 4 for both four-site graphs, 10 for five-site complete, 5 for five-site ring. Unit hopping per bond, g=0. Coordination changes and the odd ring make this a persistence test, not clean finite-size scaling. Six sites were not calculated.",
        ["results/t11-size-comparison", "code/python/t11_size_comparison.py", "code/python/verify_t11_size_comparison.py", "code/python/plot_t11_size_comparison.py"],
        ["results/t11-size-comparison/volume_comparison.png", "figures/hamiltonian-systems/four-and-five-site-graphs.png"],
        {"columns":["L","K","graph","case","dimension","triples","gap","ground_degeneracy","ground_volume","peak_volume"], "rows":size_rows},
        "Calculated and independently checked; prior 38-test suite passed", catalogue_date="2026-10-11")
    state_rows = list(csv.DictReader((ROOT / "results/t11-geometric-interpretation/state_summary.csv").open()))
    add("t11-geometric-interpretation", "T11", "Prepared tetrahedral FL states and the volume crossover",
        "Five explicitly constructed K=4 FL references: equal input face areas, phi=90,60,30,10,0 degrees. Saved face-spin distributions, pair correlations, angular fluctuations, volume distributions and overlaps; comparisons with the first three energy groups of complete/ring Hamiltonians at t=1,U=20. The complete ground is kernel-dominated despite nearly unit four-face weight.",
        "FL references are prepared states; energy groups and Gibbs mixtures are separate comparisons. This record contains static readouts; the separate T11 candidate-Hamiltonian record includes geometric-coupling scans and time evolution. Angular normalization is assignment-specific and conditioning retains coherence and selection probabilities. Geometric volume uses the established sqrt(2)/12 four-valent conversion. The Hamiltonian in this record uses g=0. No new independent Rust run.",
        ["results/t11-geometric-interpretation", "notes/t11-geometric-interpretation.md", "code/python/lqg_scattering/geometric_diagnostics.py", "code/python/t11_geometric_interpretation.py", "code/python/verify_t11_geometric_interpretation.py", "code/python/plot_t11_geometric_interpretation.py", "code/python/test_geometric_diagnostics.py"],
        ["results/t11-geometric-interpretation/thermal_geometric_diagnostics.png"],
        {"columns":["state","four_face_probability","volume_mean","geometric_volume_mean","probability_zero_volume","conditional_angle_rms_sd"], "rows":state_rows},
        "Calculated and independently checked; prior 42-test suite passed", catalogue_date="2026-10-11")
    model_rows = list(csv.DictReader((ROOT / "results/t11-candidate-hamiltonians/model_summary.csv").open()))
    selected = []
    for row in model_rows:
        alpha = float(row["alpha"])
        candidate = row["candidate"]
        graph = row["graph"]
        if row["U_over_t"] != "20.0":
            continue
        if graph == "complete" and ((candidate == "positive_volume" and alpha in (-1, 0, 1)) or
                                     (candidate == "signed_grasp" and alpha in (-1, 1))):
            selected.append(row)
        elif graph == "ring" and candidate == "positive_volume" and alpha in (-1, 0, 1):
            selected.append(row)
    candidate_table = {
        "columns": ["graph", "candidate", "alpha", "ground_energy", "first_distinct_gap",
                    "ground_volume_mean_project_units", "ground_probability_zero_volume", "ground_Q_chi_mean"],
        "rows": [{key: row[key] for key in ["graph", "candidate", "alpha", "ground_energy", "first_distinct_gap",
                                                 "ground_volume_mean_project_units", "ground_probability_zero_volume", "ground_Q_chi_mean"]}
                 for row in selected],
    }
    add("t11-candidate-hamiltonians", "T11", "Candidate geometric Hamiltonians and prepared-FL dynamics",
        "Exact K=4, total-spin-zero study (dimension 105). The baseline is complete-graph face-to-face area exchange plus on-site repulsion, with equal hopping strength on each bond. We added the positive RS-volume term and the signed triple-grasp term as separate candidate Hamiltonians, then evolved five explicitly prepared FL references under the baseline and both signed couplings. The 62 parameter settings cover U/t=0,1,5,20 and normalized coupling alpha=-2,-1,-0.5,0,0.5,1,2; the ring is included only as a sparse-hopping control. The study contains 6,510 saved energy levels and 50 prepared-state trajectories.",
        "The complete graph represents tetrahedral face adjacency; the ring is a hopping control, not a proposed tetrahedron. The positive-volume and signed-grasp additions are tested candidate models, not derived physical interactions. Results use one copy, fixed K=4, project-normalized volume, and t=1; no physical coupling calibration or phase-transition claim is implied. The long-time dynamics are exact energy-basis samples with adaptive logarithmic coverage, not a uniformly resolved trace of every fast oscillation. Large thermal and dynamics CSVs are gzip-compressed for download; their source and package checksums are both listed.",
        ["results/t11-candidate-hamiltonians/README.md", "results/t11-candidate-hamiltonians/model_summary.csv",
         "results/t11-candidate-hamiltonians/energy_levels.csv", "results/t11-candidate-hamiltonians/fl_energy_populations.csv",
         "results/t11-candidate-hamiltonians/thermal_volume_outcomes.csv", "results/t11-candidate-hamiltonians/state_geometry.csv",
         "results/t11-candidate-hamiltonians/state_volume_distributions.csv", "results/t11-candidate-hamiltonians/dynamics_schedule.csv",
         "results/t11-candidate-hamiltonians/validation.json", "results/t11-candidate-hamiltonians/verification.json",
         "results/t11-candidate-hamiltonians/protocol.json", "results/t11-candidate-hamiltonians/provenance.json",
         "code/python/t11_candidate_hamiltonians.py", "code/python/verify_t11_candidate_hamiltonians.py",
         "code/python/plot_t11_candidate_hamiltonians.py", "notes/hamiltonian-studies.md"],
        ["results/t11-candidate-hamiltonians/candidate_ground_energy_shifts.png",
         "results/t11-candidate-hamiltonians/candidate_ground_state_response.png",
         "results/t11-candidate-hamiltonians/candidate_thermal_response_u20.png",
         "results/t11-candidate-hamiltonians/ring_topology_control.png",
         "results/t11-candidate-hamiltonians/prepared_FL_early_dynamics_u20.png"],
        candidate_table,
        "62 Hamiltonian parameter settings and 50 FL trajectories calculated; 1,510 independent checks passed (maximum residual 1.07e-12)",
        catalogue_date="2026-10-11",
        compressed_sources=["results/t11-candidate-hamiltonians/state_area_assignments.csv",
                            "results/t11-candidate-hamiltonians/thermal_area_assignments_selected.csv",
                            "results/t11-candidate-hamiltonians/thermal_scan.csv",
                            "results/t11-candidate-hamiltonians/dynamics_scan.csv"])
    spectra = list(csv.DictReader((ROOT / "results/hamiltonian-studies/spectra.csv").open()))
    add("hamiltonian", "T11", "Four-site Hamiltonian spectra and RS-volume observables", "Exact diagonalization of the hopping-plus-on-site-repulsion operator H_G=-t Σ_(i,j)∈E_G(E_ij+E_ji)+(U/2)Σ_i n_i(n_i−1), where E_ij=a_i†a_j+b_i†b_j and n_i=a_i†a_i+b_i†b_i. Four sites, fixed boson number 2K and total spin zero; K=2,3,4 gives dimensions 20,50,105, with empty sites allowed. Compare the complete graph (6 hopping bonds) and periodic ring (4), with equal t per bond. The 30 cases use (t,U)=(0,1) or t=1 and U/t=0,1,5,20.",
        "The positive Rovelli–Smolin (RS) volume V=(γℏ)^(3/2)Σ_(connected triples)√|q_ijk|, q_ijk=i[J_i·J_j,J_j·J_k], is a separate observable evaluated on energy eigenstates and Gibbs states; it is not a term in H_G, and no g_V V coupling was calculated. The optional spin-exchange setting is g=0. Both graphs select the same four connected triples, so V is the same operator and only the hopping graph changes. Project-normalized volume; physical calibration is open. The temperature response is a finite-sector crossover, not a phase transition. Ground-state entropy uses the Gibbs mixture when degenerate.",
        ["results/hamiltonian-studies", "notes/hamiltonian-studies.md"],
        sorted((ROOT/"results/hamiltonian-studies").glob("*.png")),
        {"columns":["K","graph","case","dimension","ground_energy","gap","ground_mean_volume","ground_probability_zero_volume"],"rows":spectra}, "Pilot complete; broader program open")
    d=read("results/closed-basis-volume/summary.json")
    add("closed-basis", "T1a", "Complete four-face closed-basis volumes", "Four labelled faces, zero-spin faces allowed; K=2 through 12, 10,549 basis states. RS/AL means, variances, spectra and reconstructible operators.",
        "One copy, zero temperature. K=13 was stopped and has no accepted result. Physical volume calibration remains open; full tensor/root checks cover K<=4, with the recorded block checks at higher K.",
        ["results/closed-basis-volume","results/closed-state-enumeration","notes/thermal-area-sectors.md"], ["figures/closed-basis-volume","figures/single-copy-volume"],
        {"columns":["K","basis_states","equal_weight_closed_rs_mean","equal_weight_closed_al_mean"],"rows":d["areas"]})
    d=read("results/variable-n-volume/summary.json")
    add("variable-faces", "T10", "Variable-face positive RS catalogue", "Nine sectors at K=2,3,4 with 4<=N<=2K. Closed dimensions 2,36,347; positive-volume dimensions 2,32,329. Independent reconstruction covers 112 blocks and 385 eigenstates.",
        "Labelled positive-spin active faces, one copy, zero temperature. Closed states and positive-volume eigenstates are counted separately. Higher-valence AL orientation signs and physical calibration remain unspecified.",
        ["results/variable-n-volume","notes/volume-studies.md"], ["figures/variable-n-volume"],
        {"columns":["K","N","basis_dimension","zero_volume_dimension","positive_volume_dimension","equal_weight_mean"],"rows":d["by_KN"]}, "Completed declared catalogue")
    for identifier,title,desc,sources,figs in [
        ("vacuum-area","Squeezed-vacuum area coefficients","J_in=0, four faces and eight modes per copy; coefficient and area distributions at four temperatures.",["figures/thermal-area-sectors","notes/thermal-area-sectors.md"],["figures/thermal-area-sectors"]),
        ("vacuum-spin","Squeezed-vacuum resultant spin","Ordinary per-copy spin distributions conditioned on boson number, at beta*hbar*omega=1.",["figures/thermal-spin-sectors"],["figures/thermal-spin-sectors"]),
        ("excited-spin","Excited J_in=1 joint area and spin","Five temperatures, q through 160; 32,805 independent-method comparisons with maximum difference 2.67e-16.",["results/thermal-j1-spin/j1_spin_method_summary.json","figures/thermal-j1-spin"],["figures/thermal-j1-spin"]),
    ]:
        add(identifier,"T9",title,desc,"Selected two-copy squeeze on full oscillator support; no separate per-copy singlet projection. Ordinary per-copy spin differs from combined/transformed closure. Plot ranges are truncated; full reduced-state spectra and geometric observables remain open.",sources,figs)
    add("high-j", "T5c", "Higher-J flat-boundary probes", "Saved Python and Rust probes extend the earlier weighted-input boundary scans.",
        "Finite exploratory points. Rust/Python RS comparison at J=10 differs by about 4.4e-10 and remains unresolved; AL agrees within about 4e-17. Stopped attempts are recorded as attempts, not results.",
        ["results/t5c_degenerate_limits_highJ_results.json"], [HISTORY/"high_j_boundary.png"])
    legacy = [
        ("magnetization","T5a","Magnetization and signed-grasp correlations","Converged n=5 magnetization sweep; the tested magnetization hypothesis was not supported.","t5a_mag","magnetization"),
        ("chirality","T5a′","Local-chirality pilot","Saved plane/channel agreement statistics; the local subset did not establish hidden handedness.","t5a_prime","chirality"),
        ("perturbation","T5b","Imaginary-perturbation response","Recorded n=4,5 onset of the signed-mean proxy, approximately epsilon^0.5.","t5b","perturbation"),
        ("phase","T5d","Cocycle-phase pilot","Ten recorded points compare phase defect with signed grasp; broader study remains open.","t5d_phase_scan","phase"),
        ("large-k","T5e","Large-K recorded families and fits","Saved families through historical K=24. The proposed K^(3/2) scaling was not supported for these families.","t5e","large_k"),
    ]
    legacy_notes = {"t5a_mag":"notes/experiments/t5a_mag_notes.md", "t5a_prime":"notes/experiments/t5a_prime_notes.md",
                    "t5b":"memory-bank/archive/T5b.md", "t5d_phase_scan":"memory-bank/tasks/T5d.md", "t5e":"notes/experiments/t5e_notes.md"}
    for identifier,task,title,desc,stem,figure in legacy:
        add(identifier,task,title,desc,"Historical notation is preserved in downloads. Signed grasp and sqrt(abs(mean grasp)) are proxies, distinct from positive-volume expectations. These finite sampled families do not establish universal behavior.",
            [f"results/{stem}_results.json", legacy_notes[stem]], [HISTORY/f"{figure}.png"])
    for stem,title in [("t7a","Historical single-copy thermal pilot"),("t7b","Historical energy-basis TFD pilot"),("t7e","Historical complexified purification")]:
        add(stem,"T9",title,f"Archived {stem.upper()} study, retained under current T9 ownership.",
            "Historical capped oscillator support and historical state construction; this is distinct from the currently selected two-copy squeezed FL family and exact singlet Hamiltonian Gibbs calculation. Undefined JSON numbers are null in dashboard exports.",
            [f"results/{stem}_results.json",f"notes/experiments/{stem}_notes.md"],[HISTORY/f"{stem}.png"])
    add("geometry-audit","T9","Small-sector thermal geometry audit","Four regular/unequal-shape seed cases; draft squeeze compared with explicit double-singlet postselection.",
        "Draft one-sided construction, cutoff and omitted probabilities are recorded. Postselection is not assumed Gibbs and differs from the selected two-copy input construction.",
        ["results/t7_geometry_thermal_results.json"],[HISTORY/"geometry_audit.png"])
    add("volume-controls","T1a","RS/AL volume-prescription controls","Independent tensor controls: paired spin-half singlet has positive RS/AL volume despite zero signed mean; collinear product gives zero.",
        "Simple-state implementation checks; project normalization and selected four-face AL embedding only.", ["results/volume_prescription_results.json"], [HISTORY/"volume_controls.png"])
    add("covariance-pilot","T5c","Initial covariance reconstruction pilot","Six saved pilot records; later shape recovery and weighted-input studies are shown in Volume Studies.",
        "Exploratory covariance-derived geometry; preserve the distinction from the classical input tetrahedron and positive-volume operator.", ["results/t5c_covariance_probe_results.json"], [HISTORY/"covariance_pilot.png"])

    # NS37 compares two exactly zero-total-momentum quantum preparations with
    # matched classical ensembles. Only compact late-window summaries are
    # selectable; the source time samples remain represented by the saved plot.
    parent_note = "notes/quantum-geometry-research.md"
    quantum_note = "notes/quantum-planar-rotor-energy-transfer.md"
    face_note = "notes/face-activation-connectivity.md"
    geometry_note = "notes/geometric-area-redistribution.md"
    parent_sources = [parent_note] if (ROOT / parent_note).is_file() else []
    quantum_rows = quantum_planar_rows(ROOT)
    quantum_sources = [
        "results/t11-quantum-planar-rotors/README.md",
        "results/t11-quantum-planar-rotors/protocol.md",
        "results/t11-quantum-planar-rotors/summary.json",
        quantum_note, *parent_sources,
        "code/python/t11_quantum_planar_rotors.py",
        "code/python/lqg_scattering/planar_rotors.py",
        # Keep every local destination in the parent research map available
        # in the dashboard package, without adding these references as note cards.
        "notes/published-paper-overview.md",
        "notes/state-space-probes.md",
        "notes/experiments/fl_volume_shape_scan_log.md",
        "figures/physical-illustrations/README.md",
        "notes/constructive-sewing-probe.md",
        "notes/binding-energy.md",
        "results/README.md",
        "memory-bank/sessions/2026-10-16-quantum-rotors-and-geometric-redistribution-summary.md",
        "memory-bank/sessions/2026-10-16-quantum-rotors-and-geometric-redistribution-transcript.md",
        "notes/task-specifications",
        "notes/thermal-area-sectors-reorganization.md",
        "notes/equilibration-session-note-map.md",
        *[f"figures/physical-illustrations/{name}" for name in sorted(p.name for p in (ROOT / "figures/physical-illustrations").glob("*.svg"))],
    ]
    add("t11-quantum-planar-rotors", "T11", "Quantum planar-rotor transfer at zero total momentum (NS37)",
        "Two four-rotor ring preparations start in |m,-m,0,0| with exactly zero total momentum. Each row compares the saved late-window cold-pair kinetic fraction with an independent classical ensemble and reports the quantum single-rotor entropy for the initially energetic pair, initially cold pair, and all four sites.",
        "First pilot at epsilon=I=lambda=hbar=1, four sites and times 0 to 20. The reported energy is a mean, not a sharp total-energy eigenvalue. The matched classical initial measure does not establish later quantum/classical agreement, equilibration, a classical limit, or three-dimensional singlet dynamics.",
        quantum_sources, ["figures/t11-quantum-planar-rotors"],
        table={"columns": list(quantum_rows[0]), "rows": quantum_rows},
        status="Two accepted cutoff-10 cases; 6,181 zero-momentum sector states; norm, energy, classical refinement and momentum checks recorded",
        catalogue_date="2026-10-16",
        chart={"type": "scatter", "x": "parameters.packet_energy", "y": "results.late_quantum_cold_pair_fraction",
               "labels": {"parameters.packet_energy": "Initial packet kinetic energy",
                          "results.late_quantum_cold_pair_fraction": "Late cold-pair kinetic fraction (10 ≤ τ ≤ 20)"}},
        source_hashes_map=source_hashes(ROOT, [
            "results/t11-quantum-planar-rotors/quantum-m2-c10.json",
            "results/t11-quantum-planar-rotors/quantum-m4-c10.json",
            "results/t11-quantum-planar-rotors/classical-m2.json",
            "results/t11-quantum-planar-rotors/classical-m4.json",
        ]),
        document_notes=[quantum_note, parent_note])

    # NS38 retains the six exact source/graph witnesses as compact transition
    # rows; full occupation-space coefficient arrays remain out of the package.
    face_rows = face_connectivity_rows(ROOT)
    face_sources = [
        "results/t11-face-connectivity/README.md",
        "results/t11-face-connectivity/protocol.md",
        "results/t11-face-connectivity/summary.json",
        "results/t11-face-connectivity/independent-validation.json",
        face_note, *parent_sources,
    ]
    add("t11-face-connectivity", "T11", "Closed and open four-to-five-to-six channel transitions (NS38)",
        "The static L=6, K=3 table follows one closed singlet and two open J=3 sources on ring and complete graphs. A direct four-to-six hop vanishes, while the selected witnesses have explicit four-to-five-to-six matrix elements. Size controls show when five- and six-active sectors exist.",
        "Operator connectivity at alpha=t=hbar=1, with fixed boson number. A connected singlet basis does not mean every state activates every sector; open zero-mean-spin states are not singlets. This is not time evolution or geometric reconstruction.",
        face_sources,
        table={"columns": list(face_rows[0]), "rows": face_rows},
        status="99 independent witness comparisons; maximum residual 1.99e-15; 67 regression tests passed in the research session",
        catalogue_date="2026-10-16",
        chart={"type": "scatter", "x": "parameters.to_active_channels", "y": "results.chart_matrix_magnitude",
               "groupBy": "results.series",
               "labels": {"parameters.to_active_channels": "Destination active channels",
                          "results.chart_matrix_magnitude": "Absolute direct-H matrix element",
                          "results.series": "Graph and source sector"}},
        source_hashes_map=source_hashes(ROOT, [
            "results/t11-face-connectivity/L6-K3.json",
            "results/t11-face-connectivity/L5-K3.json",
            "results/t11-face-connectivity/L6-K2.json",
        ]),
        document_notes=[face_note, parent_note])

    # NS39 uses one compact summary row for each exact trajectory and selected
    # geometry samples. The 5,454-row dynamics history is deliberately omitted.
    geometry_sources = [
        "results/t11-geometric-redistribution/README.md",
        "results/t11-geometric-redistribution/protocol.md",
        "results/t11-geometric-redistribution/summary.csv",
        "results/t11-geometric-redistribution/geometry.json",
        "results/t11-geometric-redistribution/validation.json",
        "results/t11-geometric-redistribution/independent-validation.json",
        "results/t11-geometric-redistribution/symmetry-control.json",
        "results/t11-geometric-redistribution/provenance.json",
        "results/t11-geometric-redistribution/postprocessing-provenance.json",
        "results/t11-geometric-redistribution/performance.json",
        "results/t11-geometric-redistribution/regression.json",
        geometry_note, *parent_sources,
        "code/python/t11_geometric_redistribution.py",
        "code/python/lqg_scattering/channel_dynamics.py",
        "code/python/verify_t11_geometric_redistribution.py",
        "code/python/check_t11_channel_symmetry.py",
        "code/python/plot_t11_geometric_redistribution.py",
    ]
    add("t11-geometric-redistribution", "T11", "Exact-singlet geometric area redistribution (NS39–NS40)",
        "Fifty-four K=4 exact-singlet trajectories compare L=4,6,8 rings and complete graphs at alpha=0,1,5. The 54 case summaries are grouped in the chart by size, graph and preparation, with one point per coupling. The package also includes 270 selected geometry samples and the post-run permutation selection rule recorded as NS40.",
        "Finite evolution through τ=20 from regular-sharp, deformed-sharp and regular FL preparations. K is conserved linear area; the higher-valence RS volume stays in project units. Singlet mean fluxes vanish, so the pair and volume readouts do not identify distinct classical face normals or a unique polyhedron. The permutation rule explains a source-specific all-channel suppression and did not select or remove trajectories.",
        geometry_sources, ["figures/t11-geometric-redistribution"],
        status="54 exact-singlet trajectories; 270 geometry samples; 91,476 independent observable checks with maximum residual 6.43e-12; NS40 post-run diagnostic included",
        catalogue_date="2026-10-16",
        chart={"type": "line", "x": "parameters.alpha", "y": "results.late_receiver_area_fraction",
               "groupBy": "results.series",
               "labels": {"parameters.alpha": "Casimir coupling α",
                          "results.late_receiver_area_fraction": "Late mean area in initially empty receivers / K",
                          "results.series": "Size, graph and preparation"}},
        document_notes=[geometry_note, parent_note])

    metadata={"method":"packages saved data; no scientific runs repeated", "jsonNonfinitePolicy":"Nonfinite numbers become null only in dashboard JSON exports; source hashes refer to originals.","studies":STUDIES}
    (DASH/"studies.json").write_text(json.dumps(clean(metadata),indent=2,allow_nan=False)+"\n")
    d=read("code/dashboard/data.json")
    d["tabs"]=[{"id":"runs","label":"Runs & Studies"},{"id":"figures","label":"Figure Archive"},{"id":"performance","label":"Charts"},{"id":"theory","label":"Tasks & Numerical Notes"}]
    d["runs"]=[r for r in d["runs"] if not r.get("studyId")]
    d["figures"]=[f for f in d["figures"] if not f.get("studyId")]
    for study in STUDIES:
        d["runs"].append({"runId":study["id"],"task":study["task"],"status":"complete","description":study["title"],"studyId":study["id"],"params":{"scope":study["description"],"limits":study["limits"],"calculationStatus":study["status"]},"figures":study["figures"]})
        d["figures"].extend({**f,"studyId":study["id"],"description":study["title"],"tags":[study["task"]]} for f in study["figures"])
    d["summary"].update(totalRuns=len(d["runs"]),completeRuns=sum(r["status"]=="complete" for r in d["runs"]),registeredStudies=len(STUDIES))
    d["project"]["subtitle"]="Hamiltonian, closed-basis volume, thermal-sector and rotor results, with curated data, figures and verification records"
    d["theory"]["description"]="The catalogue records exact singlet Hamiltonian studies, kinematic RS/AL catalogues, selected squeezed thermal-sector distributions, finite-area face-channel readouts, and classical rotor energy-transfer studies. Model support, sampling choices, normalization and verification limits accompany each result. Broader parameter, finite-size and bulk-phase studies remain open."
    d["tasks"]={"active":[{"id":t,"title":title,"description":desc} for t,title,desc in [("T1a","Positive-volume validation","Complete four-face baseline through K=12 saved; broader physical calibration remains open."),("T5c","Weighted FL volume and shape","Initial and higher-J probes saved; broad convergence and unresolved RS comparison remain open."),("T5d","Cocycle phase","Recorded ten-point pilot; broader phase study open."),("T9","Thermal intertwiners and TFD","Projected reference entropy, Schmidt spectra, coherent joint creation and thermal geometry saved. General FL inputs and full unprojected spectra remain open."),("T9a","Singlet exchange","Finite combined-area FL dynamics and canonical controls saved; reservoir and thermal-family comparison open."),("T11","Hamiltonian, face-channel and rotor studies","Four/five-site Hamiltonians, large-area face activation, a finite-area equilibration pilot, grouped classical rotor studies and the NS37–NS40 quantum/geometry records are saved. The geometric dataset has 54 exact-singlet trajectories and a post-run symmetry rule; broader finite-size, equilibration and geometric interpretation remain open.")]],"completed":[{"id":"T10","title":"Variable-face RS catalogue","description":"Declared K=2,3,4 catalogue complete."},{"id":"T1b","title":"Real-plane volume check","description":"Independent positive-volume comparison saved."},{"id":"T5a/T5a′/T5b/T5e","title":"Archived numerical pilots","description":"Recorded scope complete; finite sampling and proxy interpretation retained."}],"pending":[]}
    combined=d["tasks"]["completed"].pop()
    d["tasks"]["completed"].extend({"id":task,"title":title,"description":combined["description"]} for task,title in
        [("T5a","Magnetization pilot"),("T5a′","Local chirality"),("T5b","Perturbation response"),("T5e","Recorded large-K families")])
    (DASH/"data.json").write_text(json.dumps(clean(d),indent=2,allow_nan=False)+"\n")
    from export_numerical_data import export_numerical_data
    datasets = export_numerical_data(metadata)
    # The research guide keeps its repository-relative dashboard link. In the
    # package, route that mirrored path back to the working dashboard root.
    dashboard_alias = DASH / "study-assets/code/dashboard/index.html"
    dashboard_alias.parent.mkdir(parents=True, exist_ok=True)
    dashboard_alias.write_text(
        '<!doctype html><meta charset="utf-8">'
        '<meta http-equiv="refresh" content="0; url=../../../index.html">'
        '<title>Numerics dashboard</title>'
        '<p><a href="../../../index.html">Open the numerics dashboard</a></p>\n'
    )
    print(f"Exported {len(datasets)} InfoDash datasets")
    print(f"Packaged {len(STUDIES)} studies, {len(d['runs'])} run records, {len(d['figures'])} figures")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reuse-history", action="store_true", help="Package existing historical plots without redrawing them")
    main(reuse_history=parser.parse_args().reuse_history)
