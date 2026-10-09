"""Package saved studies and plots for the standalone numerics dashboard.

Run with conda run -n qc-diff python code/python/dashboard_assets/build_research_catalogue.py.
No scientific calculation is rerun. Historical figures are drawn from saved arrays.
"""
import csv
import hashlib
import json
import math
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

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
}


def read(path):
    return json.loads((ROOT / path).read_text())


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
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix == ".json":
        target.write_text(json.dumps(clean(read(source)), indent=2, allow_nan=False) + "\n")
    else:
        shutil.copy2(ROOT / source, target)
    return {"name": source.name, "path": target.relative_to(DASH).as_posix(),
            "source": source.as_posix(),
            "sourceSha256": hashlib.sha256((ROOT / source).read_bytes()).hexdigest()}


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


def add(identifier, task, title, description, limits, sources, figures=(), table=None, status="Saved calculation"):
    files = []
    for source in sources:
        path = ROOT / source
        if path.is_dir():
            files.extend(export(p.relative_to(ROOT)) for p in sorted(path.iterdir()) if p.is_file() and p.suffix in [".json", ".csv", ".md", ".npz"])
        else:
            files.append(export(source))
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
    STUDIES.append({"id":identifier,"task":task,"title":title,"description":description,
                    "limits":limits,"status":status,"files":files,"figures":images,"table":table})


def main():
    historical_plots()
    spectra = list(csv.DictReader((ROOT / "results/hamiltonian-studies/spectra.csv").open()))
    add("hamiltonian", "T11", "Four-site Hamiltonian and thermal volume", "30 exact singlet calculations on complete and ring graphs. K=2,3,4 means 4,6,8 bosons; dimensions 20,50,105. Dense K=4 temperature scan: 6,030 rows and 409 energy groups.",
        "g=0; empty sites allowed. Project-normalized connected-triple RS volume. The temperature response is a finite-sector crossover; the proposed dense U/t transition scan has not been run. Ground-state entropy uses the Gibbs mixture when degenerate.",
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
        ("excited-spin","Excited J_in=1 joint area and spin","Five temperatures, q through 160; 32,805 independent-method comparisons with maximum difference 2.67e-16.",["results/thermal-j1-spin","figures/thermal-j1-spin"],["figures/thermal-j1-spin"]),
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
    metadata={"method":"packages saved data; no scientific runs repeated", "jsonNonfinitePolicy":"Nonfinite numbers become null only in dashboard JSON exports; source hashes refer to originals.","studies":STUDIES}
    (DASH/"studies.json").write_text(json.dumps(clean(metadata),indent=2,allow_nan=False)+"\n")
    d=read("code/dashboard/data.json")
    d["tabs"]=[{"id":"studies","label":"Study Catalogue"}]+[t for t in d["tabs"] if t["id"]!="studies"]
    d["runs"]=[r for r in d["runs"] if not r.get("studyId")]
    d["figures"]=[f for f in d["figures"] if not f.get("studyId")]
    for study in STUDIES:
        d["runs"].append({"runId":study["id"],"task":study["task"],"status":"complete","description":study["title"],"studyId":study["id"],"params":{"scope":study["description"],"limits":study["limits"],"calculationStatus":study["status"]},"figures":study["figures"]})
        d["figures"].extend({**f,"studyId":study["id"],"description":study["title"],"tags":[study["task"]]} for f in study["figures"])
    d["summary"].update(totalRuns=len(d["runs"]),completeRuns=sum(r["status"]=="complete" for r in d["runs"]),registeredStudies=len(STUDIES))
    d["project"]["subtitle"]="Hamiltonian, closed-basis volume and thermal-sector results, with data, plots and verification records"
    d["theory"]["description"]="The catalogue records exact singlet Hamiltonian studies, kinematic RS/AL catalogues, selected squeezed thermal-sector distributions, and earlier proxy studies. Model support, normalization and verification limits accompany each result. The proposed dense interaction scan and bulk phase analysis remain future work."
    d["tasks"]={"active":[{"id":t,"title":title,"description":desc} for t,title,desc in [("T1a","Positive-volume validation","Complete four-face baseline through K=12 saved; broader physical calibration remains open."),("T5c","Weighted FL volume and shape","Initial and higher-J probes saved; broad convergence and unresolved RS comparison remain open."),("T5d","Cocycle phase","Recorded ten-point pilot; broader phase study open."),("T9","Thermal intertwiners and TFD","Recent area/spin distributions saved; full reduced-state and geometric studies open."),("T11","Hamiltonian studies","Four-site milestone and dense thermal scan saved; interaction-transition scan, larger systems and dynamics open.")]],"completed":[{"id":"T10","title":"Variable-face RS catalogue","description":"Declared K=2,3,4 catalogue complete."},{"id":"T1b","title":"Real-plane volume check","description":"Independent positive-volume comparison saved."},{"id":"T5a/T5a′/T5b/T5e","title":"Archived numerical pilots","description":"Recorded scope complete; finite sampling and proxy interpretation retained."}],"pending":[]}
    combined=d["tasks"]["completed"].pop()
    d["tasks"]["completed"].extend({"id":task,"title":title,"description":combined["description"]} for task,title in
        [("T5a","Magnetization pilot"),("T5a′","Local chirality"),("T5b","Perturbation response"),("T5e","Recorded large-K families")])
    (DASH/"data.json").write_text(json.dumps(clean(d),indent=2,allow_nan=False)+"\n")
    print(f"Packaged {len(STUDIES)} studies, {len(d['runs'])} run records, {len(d['figures'])} figures")


if __name__ == "__main__":
    main()
