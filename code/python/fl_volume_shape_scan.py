#!/usr/bin/env python3
"""Sample equal-face-area FL tetrahedron shapes at fixed total area label J.

The four unit face normals close exactly.  The shape coordinates are the
normalized diagonal length x = |n_0+n_1|/2 and the bending angle phi.  Their
spinor rays define a four-point cross ratio, which is also a natural complex
coordinate on the four-marked-sphere moduli space used by Thurston.  This
records a coordinate correspondence; it does not identify Thurston's cone
metric with the LQG flux geometry or its volume operator.
"""

import argparse
import json
import math
import re
from functools import lru_cache
from pathlib import Path

import numpy as np

from lqg_scattering.fl_volume import evaluate_area
from lqg_scattering.spinors import four_point_cross_ratio
from lqg_scattering.tetrahedra import (
    closed_equal_area_normals, tetrahedron_vertices,
)
from lqg_scattering.intertwiners import spinors_from_normals
from dashboard_assets.tetrahedron_thumbnails import coordinate_key
from project_paths import DASHBOARD_ROOT


def shape_record(area_label, x, phi, direct_check=False):
    normals = closed_equal_area_normals(x, phi)
    closure = np.sum(normals, axis=0)
    if np.linalg.norm(closure) > 1e-12:
        raise ArithmeticError("constructed face normals failed closure")
    spinors = spinors_from_normals(normals)
    cross_ratio = four_point_cross_ratio(spinors)
    t_squared = (1.0 - x) / (1.0 + x)
    phase = np.exp(1j * phi)
    analytic_ratio = ((t_squared - phase) / (t_squared + phase)) ** 2
    cross_ratio_error = float(abs(cross_ratio - analytic_ratio))
    if cross_ratio_error > 1e-10:
        raise ArithmeticError("spinor cross ratio disagrees with shape-coordinate formula")
    values = evaluate_area(
        area_label, direct_check=direct_check, spinors=spinors
    )
    return {
        "xDiagonal": float(x),
        "phiRadians": float(phi),
        "phiDegrees": float(np.degrees(phi)),
        "crossRatioReal": float(cross_ratio.real),
        "crossRatioImag": float(cross_ratio.imag),
        "crossRatioFormulaError": cross_ratio_error,
        "closureResidual": float(np.linalg.norm(closure)),
        "classicalTripleOrientation": float(np.linalg.det(normals[:3])),
        **values,
    }


def representative_invariance_check(area_label):
    """Check spinor-column phase and common-frame invariance of the volumes."""
    normals = closed_equal_area_normals(0.5, math.pi / 3.0)
    spinors = spinors_from_normals(normals)
    baseline = evaluate_area(area_label, spinors=spinors)
    phases = np.exp(1j * np.array([0.3, 1.4, -0.8, 2.1]))
    rephased = evaluate_area(area_label, spinors=spinors * phases[:, None])
    angle = 0.73
    rotation = np.array(
        [
            [math.cos(angle / 2.0), -math.sin(angle / 2.0)],
            [math.sin(angle / 2.0), math.cos(angle / 2.0)],
        ],
        dtype=complex,
    )
    rotated = evaluate_area(area_label, spinors=(rotation @ spinors.T).T)
    keys = ("rsPositiveVolumeProjectUnits", "alPositiveVolumeProjectUnits")
    return {
        key: {
            "columnPhaseDifference": float(abs(baseline[key] - rephased[key])),
            "globalSU2Difference": float(abs(baseline[key] - rotated[key])),
        }
        for key in keys
    }


def scan(area_label=2, x_samples=19, phi_samples=24):
    if x_samples < 3 or phi_samples < 6:
        raise ValueError("use at least 3 diagonal and 6 angular samples")
    x_values = sorted(
        set(float(v) for v in np.linspace(0.03, 0.97, x_samples))
        | {float(1.0 / math.sqrt(3.0))}
    )
    phi_values = [
        2.0 * math.pi * k / phi_samples
        for k in range(1, phi_samples)
        if abs(math.sin(2.0 * math.pi * k / phi_samples)) > 1e-10
    ]
    records = []
    for x in x_values:
        for phi in phi_values:
            regular = math.isclose(x, 1.0 / math.sqrt(3.0), abs_tol=1e-12) and math.isclose(
                phi, math.pi / 2.0, abs_tol=1e-12
            )
            generic_check = math.isclose(x, 0.5, abs_tol=1e-12) and math.isclose(
                phi, math.pi / 3.0, abs_tol=1e-12
            )
            records.append(
                shape_record(area_label, x, phi, direct_check=regular or generic_check)
            )
    return {
        "schemaVersion": 1,
        "model": "Freidel-Livine Eq. (38), four unit spinors, closed equal-area face-normal family",
        "areaLabelJ": area_label,
        "areaDefinition": "A_FL / ell_p^2 = J for the fixed-area state",
        "normalization": "Project-normalized positive RS/AL expectations; physical prefactor remains open",
    "shapeScope": "Equal face-area ratios only; this is a controlled subfamily at fixed total J, not all Gr(2,4) labels or all area partitions. Face labels are ordered and samples are not quotiented by leg permutations.",
        "coordinates": {
            "xDiagonal": "x = |n_0+n_1|/2 in (0,1), with each |n_i|=1",
            "phiRadians": "Bending angle between the (0,1) and (2,3) face-normal planes",
            "crossRatio": "lambda = <0,2><1,3> / (<0,3><1,2>) for the four normalized spinor rays",
            "crossRatioInShapeCoordinates": "lambda = ((t^2 - exp(i*phi))/(t^2 + exp(i*phi)))^2, t^2=(1-x)/(1+x)",
            "thurstonRelation": "For four marked points, lambda is a complex coordinate on M_0,4. It labels the spinor-ray configuration here; the cone-metric Kähler metric and its curvature data are not assumed to equal the LQG flux geometry.",
        },
        "sampling": {"xValues": x_values, "phiDegrees": [float(np.degrees(p)) for p in phi_values]},
        "records": records,
        "validation": {
            "closureMax": max(r["closureResidual"] for r in records),
            "crossRatioFormulaMaxError": max(r["crossRatioFormulaError"] for r in records),
            "independentTensorChecks": [
                r for r in records if "directTensorRS" in r
            ],
            "representativeInvariance": representative_invariance_check(area_label),
        },
    }


def color(value, low, high):
    t = 0.5 if high == low else (value - low) / (high - low)
    stops = [(45, 84, 130), (236, 231, 211), (178, 69, 55)]
    if t <= 0.5:
        a, b, f = stops[0], stops[1], 2 * t
    else:
        a, b, f = stops[1], stops[2], 2 * (t - 0.5)
    rgb = tuple(round(a[i] + f * (b[i] - a[i])) for i in range(3))
    return "#%02x%02x%02x" % rgb


def tetrahedron_glyph(x, phi, center_x, center_y, size, title):
    """Reuse a saved orthographic thumbnail for this input shape."""
    asset_path = DASHBOARD_ROOT / "figures" / "t5c-input" / f"{coordinate_key(x, phi)}.svg"
    polygons = thumbnail_polygons(str(asset_path))
    safe_title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    x0, y0 = center_x - size / 2, center_y - size / 2
    return (
        f'<svg x="{x0:.2f}" y="{y0:.2f}" width="{size:.2f}" height="{size:.2f}" '
        f'viewBox="0 0 120 120" role="img" aria-label="{safe_title}">'
        f'<title>{safe_title}</title>{polygons}</svg>'
    )


@lru_cache(maxsize=None)
def thumbnail_polygons(asset_path):
    """Read vector faces from the one-time generated reusable thumbnail."""
    svg = Path(asset_path).read_text()
    polygons = re.findall(r'<polygon\b[^>]*/>', svg)
    if len(polygons) != 4:
        raise ValueError(f"expected four saved tetrahedron faces in {asset_path}")
    return "".join(polygons)


def make_svg(data):
    """Render a compact, self-contained dashboard figure as vector SVG."""
    width, height = 1160, 520
    panels = [
        ("RS positive volume", "rsPositiveVolumeProjectUnits"),
        ("AL positive volume", "alPositiveVolumeProjectUnits"),
    ]
    plot = {"left": 116, "top": 82, "width": 350, "height": 280}
    gaps = [0, 525]
    records = data["records"]
    regular = min(
        records,
        key=lambda r: abs(r["xDiagonal"] - 1.0 / math.sqrt(3.0))
        + abs(r["phiRadians"] - math.pi / 2.0),
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">FL volume across equal-area tetrahedron shapes at fixed J</title>',
        '<desc id="desc">Heatmap samples over ordered closed equal-area four-face configurations. Miniature reconstructed tetrahedra below and beside both panels show the x and bending-angle coordinate slices.</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#20252b}.tick{font-size:12px}.label{font-size:14px}.title{font-size:17px;font-weight:600}.small{font-size:11px;fill:#59636e}</style>',
        f'<text x="580" y="28" text-anchor="middle" class="title">FL positive volume across tetrahedron shapes at J={data["areaLabelJ"]}</text>',
        f'<text x="580" y="49" text-anchor="middle" class="small">Equal face-area ratios; {len(records)} ordered samples; project-normalized values</text>',
    ]
    for panel_index, (panel_title, key) in enumerate(panels):
        dx = gaps[panel_index]
        left, top = plot["left"] + dx, plot["top"]
        pw, ph = plot["width"], plot["height"]
        values = [r[key] for r in records]
        lo, hi = min(values), max(values)
        parts.append(f'<text x="{left + pw/2}" y="70" text-anchor="middle" class="label">{panel_title}</text>')
        parts.append(f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}" fill="#fafafa" stroke="#64707b"/>')
        for tick in range(6):
            xval = tick / 5
            px = left + xval * pw
            parts.append(f'<path d="M {px:.1f} {top} V {top+ph}" stroke="#dce1e6" stroke-width="1"/>')
            parts.append(f'<text x="{px:.1f}" y="{top+ph+19}" text-anchor="middle" class="tick">{xval:.1f}</text>')
        for deg in (0, 90, 180, 270, 360):
            py = top + ph * deg / 360
            parts.append(f'<path d="M {left} {py:.1f} H {left+pw}" stroke="#e5e8eb" stroke-width="1"/>')
            parts.append(f'<text x="{left-8}" y="{py+4:.1f}" text-anchor="end" class="tick">{deg}°</text>')
        for record in records:
            px = left + record["xDiagonal"] * pw
            py = top + ph * record["phiDegrees"] / 360
            fill = color(record[key], lo, hi)
            is_regular = record is regular
            radius = 5.4 if is_regular else max(2.4, min(4.4, 140.0 / math.sqrt(len(records))))
            stroke = "#111820" if is_regular else "#ffffff"
            sw = 2.2 if is_regular else 0.8
            title = f'J={data["areaLabelJ"]}; x={record["xDiagonal"]:.4f}; phi={record["phiDegrees"]:.0f} deg; {key}={record[key]:.7g}; lambda={record["crossRatioReal"]:.5g}{record["crossRatioImag"]:+.5g}i'
            parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"><title>{title}</title></circle>')
        parts.append(f'<text x="{left+pw/2}" y="{top+ph+42}" text-anchor="middle" class="label">x = |n₀ + n₁| / 2</text>')
        y_label_x = left - (82 if panel_index == 0 else 94)
        parts.append(f'<text x="{y_label_x}" y="{top+ph/2}" text-anchor="middle" class="label" transform="rotate(-90 {y_label_x} {top+ph/2})">bending angle φ</text>')
        # Separate compact color scale per panel.
        bar_x, bar_y, bar_w, bar_h = left + pw + 14, top, 13, ph
        for step in range(40):
            val = lo + (hi - lo) * (step / 39)
            y = bar_y + bar_h * (39 - step) / 40
            parts.append(f'<rect x="{bar_x}" y="{y:.2f}" width="{bar_w}" height="{bar_h/40+0.3:.2f}" fill="{color(val, lo, hi)}"/>')
        parts.append(f'<text x="{bar_x+19}" y="{bar_y+5}" class="tick">{hi:.4g}</text>')
        parts.append(f'<text x="{bar_x+19}" y="{bar_y+bar_h}" class="tick">{lo:.4g}</text>')
    # Each volume panel gets its own copies of the same shape-coordinate slices:
    # x varies at phi=90 degrees below it, while phi varies at the regular-
    # tetrahedron x value beside its vertical axis.
    x_slice = [r for r in records if math.isclose(r["phiDegrees"], 90.0, abs_tol=1e-8)]
    phi_slice = [r for r in records if math.isclose(r["xDiagonal"], 1.0 / math.sqrt(3.0), abs_tol=1e-12)]
    for panel_index in range(len(panels)):
        left = plot["left"] + gaps[panel_index]
        side_x = left - (48 if panel_index == 0 else 53)
        for target_x in np.linspace(0.0, 1.0, 6):
            sample = min(x_slice, key=lambda r: abs(r["xDiagonal"] - target_x))
            parts.append(
                tetrahedron_glyph(
                    sample["xDiagonal"], sample["phiRadians"],
                    left + target_x * plot["width"], 436, 32,
                    f'x-axis miniature at tick x={target_x:.1f}; nearest scan sample '
                    f'x={sample["xDiagonal"]:.4f}, phi={sample["phiDegrees"]:.0f} degrees',
                )
            )
        for target_phi in (0.0, 90.0, 180.0, 270.0, 360.0):
            sample = min(phi_slice, key=lambda r: abs(r["phiDegrees"] - target_phi))
            parts.append(
                tetrahedron_glyph(
                    sample["xDiagonal"], sample["phiRadians"], side_x,
                    plot["top"] + plot["height"] * target_phi / 360.0, 32,
                    f'bending-angle miniature at tick phi={target_phi:.0f} degrees; '
                    f'nearest nondegenerate scan sample phi={sample["phiDegrees"]:.0f} degrees',
                )
            )
    parts.append('<text x="580" y="470" text-anchor="middle" class="small">Each panel: bottom row varies x at φ=90°; side column varies φ at x=1/√3; nearest valid samples shown</text>')
    parts.append('<circle cx="78" cy="500" r="5" fill="#ece7d3" stroke="#111820" stroke-width="2"/>')
    parts.append('<text x="90" y="504" class="small">regular tetrahedron reference</text>')
    parts.append('<text x="1150" y="504" text-anchor="end" class="small">All miniatures use equal display scale. Samples also store the spinor-ray cross ratio λ.</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--j", type=int, default=2)
    parser.add_argument("--x-samples", type=int, default=19)
    parser.add_argument("--phi-samples", type=int, default=24)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--svg", type=Path)
    args = parser.parse_args()
    data = scan(args.j, args.x_samples, args.phi_samples)
    output_path = args.output or DASHBOARD_ROOT / f"fl-volume-shape-j{args.j}.json"
    svg_path = args.svg or DASHBOARD_ROOT / "figures" / f"fl-volume-shape-j{args.j}.svg"
    output_path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(make_svg(data) + "\n")
    vals = [r["rsPositiveVolumeProjectUnits"] for r in data["records"]]
    al_vals = [r["alPositiveVolumeProjectUnits"] for r in data["records"]]
    regular = next(
        r for r in data["records"]
        if math.isclose(r["xDiagonal"], 1.0 / math.sqrt(3.0), abs_tol=1e-12)
        and math.isclose(r["phiRadians"], math.pi / 2.0, abs_tol=1e-12)
    )
    print(json.dumps({
        "records": len(data["records"]),
        "closureMax": data["validation"]["closureMax"],
        "rsRange": [min(vals), max(vals)],
        "alRange": [min(al_vals), max(al_vals)],
        "regularCrossRatio": [regular["crossRatioReal"], regular["crossRatioImag"]],
        "independentChecks": len(data["validation"]["independentTensorChecks"]),
        "json": str(output_path),
        "svg": str(svg_path),
    }, indent=2))


if __name__ == "__main__":
    main()
