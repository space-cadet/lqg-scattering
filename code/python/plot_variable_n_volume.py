"""Plot the saved variable-N RS catalogue without rerunning the physics."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.text import Text
import numpy as np
from PIL import Image

from project_paths import PROJECT_ROOT as ROOT

DATA = ROOT/"results"/"variable-n-volume"
OUT = ROOT/"figures"/"variable-n-volume"
COLORS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#8A6500")
STYLES = ("-", "--", "-.", ":", (0, (5, 1, 1, 1)))
MARKERS = ("o", "s", "^", "D", "v")


def cdf(spectrum):
    values = [g["rs_volume"] for g in spectrum]
    weights = np.asarray([g["multiplicity"] for g in spectrum], float)
    return np.array([0]+values+[max(values)*1.07]), np.r_[0, np.cumsum(weights)/weights.sum(), 1]


def export(fig, stem):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    outside_ticks = set()
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            low, high = sorted(axis.get_view_interval())
            for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                if not low <= tick.get_loc() <= high:
                    outside_ticks.update((id(tick.label1), id(tick.label2)))
    for item in fig.findobj(match=Text):
        if id(item) in outside_ticks or not item.get_visible() or not item.get_text():
            continue
        box = item.get_window_extent(renderer)
        assert box.x0 >= -2 and box.y0 >= -2, (item.get_text(), tuple(box.bounds))
        assert box.x1 <= fig.bbox.width+2 and box.y1 <= fig.bbox.height+2, item.get_text()
    fig.savefig(OUT/(stem+".pdf"))
    fig.savefig(OUT/(stem+".png"), dpi=300)
    with Image.open(OUT/(stem+".png")) as image:
        dpi = image.info["dpi"]
        assert abs(dpi[0]-300) < .1 and abs(dpi[1]-300) < .1
    plt.close(fig)


def main():
    summary = json.loads((DATA/"summary.json").read_text())
    hashes, statistics = [], []
    for record in summary["by_KN"]:
        path = DATA/f"metadata_k{record['K']}_n{record['N']}.json"
        metadata = json.loads(path.read_text())
        archive_path = DATA/record["archive"]
        assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == record["archive_sha256"]
        values = np.array([v for b in metadata["blocks"] for v in b["rs_eigenvalues"]])
        assert len(values) == record["basis_dimension"]
        assert sum(g["multiplicity"] for g in record["spectrum"]) == len(values)
        assert (values == 0).sum() == record["zero_volume_dimension"]
        assert np.isclose(values.mean(), record["equal_weight_mean"], rtol=0, atol=2e-13)
        assert np.isclose(values.std(), record["equal_weight_sd"], rtol=0, atol=2e-13)
        x, y = cdf(record["spectrum"])
        assert np.all(np.diff(x) >= 0) and np.all(np.diff(y) >= 0) and y[-1] == 1
        statistics.append({key: record[key] for key in
                           ("K", "N", "basis_dimension", "zero_volume_dimension",
                            "positive_volume_dimension", "equal_weight_mean", "equal_weight_sd")})
        hashes.append({"path": str(path.relative_to(ROOT)),
                       "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    hashes.append({"path": str((DATA/"summary.json").relative_to(ROOT)),
                   "sha256": hashlib.sha256((DATA/"summary.json").read_bytes()).hexdigest()})
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 11, "axes.labelsize": 11, "axes.titlesize": 12,
                         "legend.fontsize": 9, "pdf.fonttype": 42, "ps.fonttype": 42})
    areas = summary["areas"]
    fig, axes = plt.subplots(1, len(areas), figsize=(10.5, 5.2), layout="constrained", squeeze=False)
    for ax, area in zip(axes[0], areas):
        records = [r for r in summary["by_KN"] if r["K"] == area["K"]]
        for r in records:
            index = r["N"]-4
            x, y = cdf(r["spectrum"])
            ax.step(x, y, where="post", color=COLORS[index], ls=STYLES[index], lw=1.8,
                    label=f"N={r['N']} (d={r['basis_dimension']})")
        x, y = cdf(area["spectrum"])
        if len(records) > 1:
            ax.step(x, y, where="post", color="#333333", ls=(0, (2, 2)), lw=1.5,
                    label=f"All N (d={area['basis_dimension']})")
        ax.set(title=f"K={area['K']}: RS volume distribution",
               xlabel="RS eigenvalue (raw project units)", ylim=(-.03, 1.06),
               xlim=(-.02*x[-1], x[-1]))
        ax.grid(alpha=.2)
        ax.legend(loc="upper left", bbox_to_anchor=(0, -.25), ncol=2, borderaxespad=0)
    axes[0, 0].set_ylabel("Fraction of eigenstates with volume ≤ V")
    export(fig, "rs_volume_distributions")

    fig, axes = plt.subplots(1, len(areas), figsize=(10.5, 3.8), layout="constrained", squeeze=False)
    for ax, area in zip(axes[0], areas):
        records = [r for r in summary["by_KN"] if r["K"] == area["K"]]
        n = np.array([r["N"] for r in records])
        positive = np.array([r["positive_volume_dimension"] for r in records])
        zero = np.array([r["zero_volume_dimension"] for r in records])
        ax.bar(n, positive, color="#0072B2", width=.65, label="Positive volume")
        ax.bar(n, zero, bottom=positive, color="#BBBBBB", hatch="///", width=.65, label="Zero volume")
        for face, p, z in zip(n, positive, zero):
            ax.text(face, p+z, str(p+z), ha="center", va="bottom", fontsize=10)
            if z:
                ax.text(face, p+z/2, str(z), ha="center", va="center", fontsize=9)
        ax.set(title=f"K={area['K']}: {area['basis_dimension']} closed states",
               xlabel="Active faces N", xticks=n, ylim=(0, 1.22*max(positive+zero)))
        ax.grid(axis="y", alpha=.2)
    axes[0, 0].set_ylabel("Independent eigenstates")
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="outside upper center", ncol=2)
    export(fig, "closed_state_counts")

    fig, ax = plt.subplots(figsize=(5.0, 3.8), layout="constrained")
    for area_index, area in enumerate(areas):
        records = [r for r in summary["by_KN"] if r["K"] == area["K"]]
        n = [r["N"] for r in records]
        mean = [r["equal_weight_mean"] for r in records]
        ax.plot(n, mean, marker=MARKERS[area_index], color=COLORS[area_index],
                ls=STYLES[area_index], lw=1.6, label=f"K={area['K']}")
    ax.set(xlabel="Active faces N", ylabel="Equal-weight mean RS volume (raw units)",
           title="Volume means at fixed area", xticks=range(4, 9), ylim=(0, None))
    ax.grid(alpha=.2)
    ax.legend()
    export(fig, "rs_volume_means")
    (OUT/"plot_summary.json").write_text(json.dumps(
        {"sources": hashes, "statistics": statistics, "png_dpi": 300,
         "physics_rerun": False, "matplotlib": matplotlib.__version__,
         "checks": ["archive hashes", "dimensions and multiplicities", "zero counts",
                    "trace means and variances", "CDF monotonicity and normalization",
                    "text inside canvas", "PNG DPI"],
         "interpretation": "Equal weights per independent eigenstate; pooled N weights are proportional to dimensions; raw RS units with no geometric conversion."},
        indent=2, allow_nan=False)+"\n")
    print("OK: saved-data physics checks, plot layout checks, three vector PDF/300-DPI PNG exports.")


if __name__ == "__main__":
    main()
