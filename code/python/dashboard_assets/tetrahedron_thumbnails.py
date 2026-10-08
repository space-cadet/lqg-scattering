"""Generate reusable SVG thumbnails for dashboard tetrahedron shape traces.

Run from the repository root with:
    python code/python/dashboard_assets/tetrahedron_thumbnails.py

The input-shape previews are shared by T1a and T5c. T5c covariance previews
are generated once per saved (shape, J) record and reused by chart points and
result tables; the browser only loads these static SVG assets.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from project_paths import DASHBOARD_ROOT


DASHBOARD = DASHBOARD_ROOT
FIGURES = DASHBOARD / "figures"
INPUT_DIR = FIGURES / "t5c-input"
COVARIANCE_DIR = FIGURES / "t5c-covariance"
CAMERA = np.array(
    [
        [math.sqrt(3.0) / 2.0, -0.5, 0.0],
        [0.25, math.sqrt(3.0) / 4.0, -math.sqrt(3.0) / 2.0],
        [math.sqrt(3.0) / 4.0, 0.75, 0.5],
    ]
)
FACES = ((1, 2, 3), (0, 3, 2), (0, 1, 3), (0, 2, 1))


def coordinate_key(x: float, phi_radians: float) -> str:
    """Stable filename key shared by the SVG figure and dashboard HTML."""
    x_label = f"{float(x):.8f}".replace(".", "p")
    phi_degrees = math.degrees(float(phi_radians))
    phi_label = f"{phi_degrees:.8f}".replace(".", "p")
    return f"x{x_label}-phi{phi_label}"


def input_normals(x: float, phi: float) -> np.ndarray:
    u = math.sqrt(max(0.0, 1.0 - x * x))
    return np.array(
        [
            [u, 0.0, x],
            [-u, 0.0, x],
            [u * math.cos(phi), u * math.sin(phi), -x],
            [-u * math.cos(phi), -u * math.sin(phi), -x],
        ],
        dtype=float,
    )


def vertices_from_face_vectors(face_vectors: np.ndarray) -> np.ndarray:
    """Use the documented dual formula for four closed face-area vectors."""
    faces = np.asarray(face_vectors, dtype=float).copy()
    triple = faces[[1, 2, 3]].copy()
    determinant = float(np.linalg.det(triple))
    if determinant > 0.0:
        faces[:, 2] *= -1.0
        triple[:, 2] *= -1.0
        determinant = -determinant
    if determinant >= -1e-14:
        raise ValueError("cannot draw a degenerate tetrahedron")

    dual_scale = math.sqrt(-8.0 * determinant)
    edges = np.array(
        [
            4.0 * np.cross(triple[1], triple[2]) / dual_scale,
            4.0 * np.cross(triple[2], triple[0]) / dual_scale,
            4.0 * np.cross(triple[0], triple[1]) / dual_scale,
        ]
    )
    vertices = np.vstack((np.zeros(3), edges))
    return vertices - np.mean(vertices, axis=0)


def svg_thumbnail(vertices: np.ndarray, title: str, description: str) -> str:
    width = height = 120
    viewed = np.asarray(vertices) @ CAMERA.T
    projected = viewed[:, :2]
    span = max(float(np.ptp(projected[:, 0])), float(np.ptp(projected[:, 1])))
    if span <= 1e-12:
        raise ValueError("tetrahedron projection is degenerate")
    scale = 104.0 / span
    px = width / 2 + (projected[:, 0] - np.mean(projected[:, 0])) * scale
    py = height / 2 - (projected[:, 1] - np.mean(projected[:, 1])) * scale

    light = np.array([0.4, -0.5, 0.75], dtype=float)
    light /= np.linalg.norm(light)
    rendered = []
    for face in FACES:
        p0, p1, p2 = vertices[list(face)]
        normal = np.cross(p1 - p0, p2 - p0)
        normal /= np.linalg.norm(normal)
        shade = 0.35 + 0.45 * max(0.0, float(np.dot(normal, light)))
        channel = round(184 + 55 * shade)
        fill = f"#{channel-15:02x}{channel-5:02x}{channel:02x}"
        points = " ".join(f"{px[i]:.2f},{py[i]:.2f}" for i in face)
        depth = float(np.mean(viewed[list(face), 2]))
        rendered.append((depth, points, fill))

    polygons = "".join(
        f'<polygon points="{points}" fill="{fill}" stroke="#334155" '
        'stroke-width="1.6" stroke-linejoin="round"/>'
        for _, points, fill in sorted(rendered)
    )
    safe_title = (title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    safe_description = (
        description.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" '
        'viewBox="0 0 120 120" role="img" '
        f'aria-labelledby="shape-title shape-desc"><title id="shape-title">{safe_title}</title>'
        f'<desc id="shape-desc">{safe_description}</desc>{polygons}</svg>\n'
    )


def covariance_face_vectors(gram: np.ndarray, reference_normals: np.ndarray) -> np.ndarray:
    """Factor G=XX^T and orient X toward the input normals for display only."""
    values, vectors = np.linalg.eigh(0.5 * (gram + gram.T))
    if values[1] <= 0.0:
        raise ValueError("covariance Gram matrix has fewer than three spatial modes")
    factor = vectors[:, 1:] * np.sqrt(values[1:])[None, :]
    left, _, right = np.linalg.svd(factor.T @ reference_normals)
    return factor @ (left @ right)


def collect_input_shapes(t5c: dict) -> dict[str, tuple[float, float]]:
    shapes = {
        name: (float(spec["x"]), float(spec["phiRadians"]))
        for name, spec in t5c["shapes"].items()
    }

    # Reuse these same static shape previews in the T1a x/phi axis guides.
    shape_scan = json.loads((DASHBOARD / "fl-volume-shape-j2.json").read_text())
    records = shape_scan["records"]
    x_slice = [r for r in records if math.isclose(r["phiDegrees"], 90.0, abs_tol=1e-8)]
    phi_slice = [
        r
        for r in records
        if math.isclose(r["xDiagonal"], 1.0 / math.sqrt(3.0), abs_tol=1e-12)
    ]
    for target_x in np.linspace(0.0, 1.0, 6):
        sample = min(x_slice, key=lambda r: abs(r["xDiagonal"] - target_x))
        shapes[f"t1a-x-{target_x:.1f}"] = (sample["xDiagonal"], sample["phiRadians"])
    for target_phi in (0.0, 90.0, 180.0, 270.0, 360.0):
        sample = min(phi_slice, key=lambda r: abs(r["phiDegrees"] - target_phi))
        shapes[f"t1a-phi-{target_phi:.0f}"] = (sample["xDiagonal"], sample["phiRadians"])

    # Coordinates can repeat across T1a/T5c labels; retain one reusable asset.
    return {
        coordinate_key(x, phi): (x, phi)
        for x, phi in shapes.values()
    }


def main() -> None:
    t5c = json.loads((DASHBOARD / "t5c-shape-recovery.json").read_text())
    input_shapes = collect_input_shapes(t5c)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    COVARIANCE_DIR.mkdir(parents=True, exist_ok=True)

    for key, (x, phi) in input_shapes.items():
        degrees = math.degrees(phi)
        title = f"Input tetrahedron: x={x:.6g}, phi={degrees:.4g} degrees"
        svg = svg_thumbnail(
            vertices_from_face_vectors(input_normals(x, phi)),
            title,
            "Tetrahedron reconstructed from the four closed, equal-area input face normals.",
        )
        (INPUT_DIR / f"{key}.svg").write_text(svg)

    for record in t5c["records"]:
        shape = record["shape"]
        J = int(record["J"])
        x = float(record["x"])
        phi = float(record["phiRadians"])
        reference = input_normals(x, phi)
        face_vectors = covariance_face_vectors(np.asarray(record["fluxGram"]), reference)
        title = f"Covariance candidate: {shape}, J={J}"
        svg = svg_thumbnail(
            vertices_from_face_vectors(face_vectors),
            title,
            "Candidate tetrahedron reconstructed from the quantum state's flux-covariance Gram matrix.",
        )
        (COVARIANCE_DIR / f"{shape}-j{J}.svg").write_text(svg)

    print(
        f"Generated {len(input_shapes)} shared input-shape thumbnails and "
        f"{len(t5c['records'])} covariance thumbnails."
    )


if __name__ == "__main__":
    main()
