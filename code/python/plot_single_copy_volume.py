"""Export saved single-copy volume results for the thermal research note.

No state construction or volume calculation is rerun. Vector PDFs and
300-DPI PNGs use the saved validated sweep and weighted-input results.
"""
from pathlib import Path
import hashlib
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "figures" / "single-copy-volume"
SOURCES = [ROOT / "results" / "fl_volume_area_results.json",
           ROOT / "results" / "t5c_input_geometry_results.json"]


def export(fig, name):
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=300)
    plt.close(fig)


def main():
    sweep, weighted = [json.loads(p.read_text()) for p in SOURCES]
    assert [r["areaLabelJ"] for r in sweep] == list(range(1, 6))
    for r in sweep:
        for kind, direct in [("rs", "directTensorRS"), ("al", "directTensorAL")]:
            value = r[f"{kind}PositiveVolumeProjectUnits"]
            assert math.isfinite(value) and value >= 0
            assert math.isclose(value, r[direct], abs_tol=3e-15)
    for case in weighted["cases"]:
        assert [r["J"] for r in case["results"]] == list(range(1, 8))
        target = case["classicalVolumeProjectUnitsAtUnitTotalArea"]
        assert target > 0
        for r in case["results"]:
            for kind in ["rs", "al"]:
                mean = r[f"{kind}GeometryMatchedMeanOverJ32"]
                sd = r[f"{kind}GeometryMatchedSDOverJ32"]
                variance = r[f"{kind}VarianceProjectUnitsSquared"]
                factor = weighted["normalization"]["fixedGeometryMatchingFactors"][kind]
                assert all(math.isfinite(v) and v >= 0 for v in [mean, sd, variance])
                assert math.isclose(mean / target, r[f"{kind}ToClassicalRatio"], abs_tol=3e-14)
                assert math.isclose(sd, factor * math.sqrt(variance) / r["J"]**1.5,
                                    abs_tol=3e-14)
            assert math.isclose(r["rsGeometryMatchedMeanOverJ32"],
                                r["alGeometryMatchedMeanOverJ32"], abs_tol=3e-14)
            assert math.isclose(r["rsGeometryMatchedSDOverJ32"],
                                r["alGeometryMatchedSDOverJ32"], abs_tol=3e-14)

    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 11, "axes.labelsize": 12,
                         "axes.titlesize": 12, "legend.fontsize": 10,
                         "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, ax = plt.subplots(figsize=(6.8, 3.8), layout="constrained")
    j = [r["areaLabelJ"] for r in sweep]
    for kind, label, color, marker, style in [
            ("rs", "RS", "#0072B2", "o", "-"),
            ("al", "AL", "#D55E00", "s", "--")]:
        ax.plot(j, [r[f"{kind}PositiveVolumeProjectUnits"] for r in sweep],
                label=label, color=color, marker=marker, linestyle=style, linewidth=1.8)
    ax.set(title="Regular FL tetrahedron: single-copy volume",
           xlabel=r"Total linear area label $J$", ylabel=r"$\langle V\rangle$ (raw project units)",
           xticks=j, ylim=(0, None))
    ax.grid(alpha=.25)
    ax.legend()
    export(fig, "regular_volume_area")

    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.8), layout="constrained")
    for case, color, marker, style in zip(weighted["cases"],
                                        ["#0072B2", "#D55E00"], ["o", "s"], ["-", "--"]):
        rows = case["results"]
        j = [r["J"] for r in rows]
        target = case["classicalVolumeProjectUnitsAtUnitTotalArea"]
        label = case["name"].replace("_", " ").capitalize()
        for ax, values in zip(axes, [
                [r["rsToClassicalRatio"] for r in rows],
                [r["rsGeometryMatchedSDOverJ32"] / target for r in rows]]):
            ax.plot(j, values, label=label, color=color, marker=marker,
                    linestyle=style, linewidth=1.8)
            ax.set(xlabel=r"Total linear area label $J$", xticks=j, ylim=(0, None))
            ax.grid(alpha=.25)
    axes[0].axhline(1, color="#555555", linestyle=":", label="Classical target")
    axes[0].set(title="Geometry-matched volume mean",
                ylabel=r"$\langle V\rangle/V_{\mathrm{cl}}$", ylim=(0, 1.1))
    axes[1].set(title="Intrinsic quantum volume spread",
                ylabel=r"$\sigma_V/V_{\mathrm{cl}}$")
    axes[0].legend(loc="lower right")
    axes[1].legend()
    export(fig, "weighted_volume_area")
    report = {
        "date": "2026-10-08", "agent": "GPT 6.1 Sol",
        "sources": [{"path": str(p.relative_to(ROOT)),
                     "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in SOURCES],
        "physics_rerun": False, "png_dpi": 300,
        "figures": {"regular_volume_area": "Raw RS/AL expectations, J=1..5",
                    "weighted_volume_area": "Geometry-matched means and intrinsic spreads, J=1..7"},
        "checks": ["nonnegative finite means and variances", "validated-sweep tensor agreement",
                   "area-label ranges", "ratios agree with saved normalized means",
                   "standard deviations agree with saved variances and fixed conversion factors",
                   "geometry-matched RS/AL means and spreads coincide"],
        "interpretation": "Zero-temperature single-copy FL states; finite-range results, not a classical-limit proof.",
        "matplotlib": matplotlib.__version__,
    }
    (OUT / "plot_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print("OK: two figures exported as PDF and 300-DPI PNG; saved-array checks passed.")


if __name__ == "__main__":
    main()
